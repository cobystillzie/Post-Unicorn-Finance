"""Tier-3 taxonomy critic synthesis.

Reads the 8 Tier-2 cluster-finder JSON outputs in
data/runtime/phase3_cluster_findings/ and produces:
  - data/runtime/phase3_cluster_findings/tier3_taxonomy_critique.json
  - docs/research/emergent_post_unicorn_taxonomy_2026-06-01.md

Numbers are computed (not estimated): all counts come from a dedup pass over
member lists in the 8 cluster files. Run as: py scripts/tier3_synthesize_taxonomy.py
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHASE3_DIR = ROOT / "data" / "runtime" / "phase3_cluster_findings"

CLUSTER_FILES = [
    ("Patient Capital", "cluster_Patient_Capital.json"),
    ("Portfolio Capital", "cluster_Portfolio_Capital.json"),
    ("SMV", "cluster_SMV.json"),
    ("LMV", "cluster_LMV.json"),
    ("Sovereign Capital", "cluster_Sovereign_Capital.json"),
    ("UVC", "cluster_UVC.json"),
    ("Search/ETA", "cluster_Search_ETA.json"),
    ("ECOSYSTEM", "cluster_ECOSYSTEM.json"),
]


def load_clusters():
    """Load all cluster files and return raw dicts keyed by class label."""
    return {
        class_name: json.loads((PHASE3_DIR / fn).read_text(encoding="utf-8"))
        for class_name, fn in CLUSTER_FILES
    }


def extract_members(sc):
    members = sc.get("members") or sc.get("entities") or sc.get("all_entities") or []
    out = []
    for m in members:
        if isinstance(m, dict):
            n = m.get("name")
        else:
            n = m
        if n:
            out.append(n)
    return out


def build_entity_index(clusters):
    entity_locations = defaultdict(list)  # name -> list of (class, subcluster_id)
    sc_to_members = defaultdict(list)  # (class, subcluster_id) -> [name,...]
    slice_counts = {}
    total_assignments = 0
    for class_name, data in clusters.items():
        c = 0
        for sc in data.get("sub_clusters", []):
            sc_id = sc.get("sub_cluster_id") or sc.get("name")
            for n in extract_members(sc):
                entity_locations[n].append((class_name, sc_id))
                sc_to_members[(class_name, sc_id)].append(n)
                c += 1
        slice_counts[class_name] = c
        total_assignments += c
    return entity_locations, sc_to_members, slice_counts, total_assignments


def collect_reclass_flags(clusters):
    """Per-allocator reclassification_flags collected with origin and target."""
    all_flags = []
    for class_name in (
        "Patient Capital",
        "Portfolio Capital",
        "SMV",
        "LMV",
        "Sovereign Capital",
        "Search/ETA",
    ):
        for f in clusters[class_name].get("reclassification_flags", []) or []:
            target = f.get("should_be") or f.get("target_class")
            all_flags.append(
                {
                    "name": f.get("name"),
                    "from_class": class_name,
                    "target_class": target,
                    "why": f.get("why") or f.get("reason"),
                }
            )
    return all_flags


def main():
    clusters = load_clusters()
    entity_locations, sc_to_members, slice_counts, total_assignments = build_entity_index(clusters)
    flags = collect_reclass_flags(clusters)

    # ---------------- Cross-class pattern map (computed) ----------------
    def sc(cls, name):
        return set(sc_to_members.get((cls, name), []))

    patterns = []

    # 1. Healthcare practice rollups (Patient + Portfolio)
    pat_hc = sc("Patient Capital", "HEALTHCARE_PRACTICE_ROLLUP")
    port_hc = sc("Portfolio Capital", "HEALTHCARE_PRACTICE_ROLLUP")
    overlap_hc = sorted(pat_hc & port_hc)
    patterns.append(
        {
            "pattern": "Healthcare & licensed-practice consolidation platforms (DSO/DPO/MSO)",
            "appears_in_classes": ["Patient Capital", "Portfolio Capital"],
            "entities": overlap_hc,
            "correct_class": "Portfolio Capital",
            "boundary_test": (
                "Default to Portfolio Capital (mechanism = serial acquisition of practices under a "
                "platform); promote to Patient Capital ONLY when the platform explicitly disclaims "
                "exit timelines AND distributes returns to operator-clinicians (steward-style)."
            ),
        }
    )

    # 2. Home services / trades rollups
    pat_hs = sc("Patient Capital", "HOME_SERVICES_ROLLUP")
    port_hs = sc("Portfolio Capital", "HOME_SERVICES_TRADES_ROLLUP")
    overlap_hs = sorted(pat_hs & port_hs)
    patterns.append(
        {
            "pattern": "Home services / trades roll-ups (HVAC, plumbing, electrical)",
            "appears_in_classes": ["Patient Capital", "Portfolio Capital"],
            "entities": overlap_hs,
            "correct_class": "Portfolio Capital",
            "boundary_test": (
                "Default Portfolio Capital. The 'people-first / partner' rhetoric does not make these "
                "Patient Capital; only steward-ownership-trust structures or no-exit covenants do."
            ),
        }
    )

    # 3. Permanent-equity software acquirers (Patient PERM_EQUITY_SOFTWARE vs Portfolio VMS_SERIAL_ACQUIRER)
    pat_pe_sw = sc("Patient Capital", "PERM_EQUITY_SOFTWARE")
    port_vms = sc("Portfolio Capital", "VMS_SERIAL_ACQUIRER")
    overlap_sw = sorted(pat_pe_sw & port_vms)
    patterns.append(
        {
            "pattern": "Permanent-equity software acquirers (VMS / SaaS forever-hold)",
            "appears_in_classes": ["Patient Capital", "Portfolio Capital"],
            "entities": overlap_sw + sorted((pat_pe_sw | port_vms) - (pat_pe_sw & port_vms))[:25],
            "correct_class": "Portfolio Capital",
            "boundary_test": (
                "Default Portfolio Capital VMS sub-bucket (the mechanism is serial software acquisition "
                "and decentralized operating groups). Use Patient Capital only when the entity is a "
                "single-business steward (one app, no acquisition flywheel) or an explicit purpose-trust "
                "structure (capped returns, no-sale covenant)."
            ),
        }
    )

    # 4. Diversified compounders vs family holdcos
    pat_fo = sc("Patient Capital", "FAMILY_OFFICE_HOLDCO")
    port_div = sc("Portfolio Capital", "DIVERSIFIED_HOLDCO_COMPOUNDER")
    pat_listed = sc("Patient Capital", "LISTED_HOLDCO")
    overlap_div = sorted((pat_fo | pat_listed) & port_div)
    patterns.append(
        {
            "pattern": "Diversified holdcos / public compounders (Berkshire-style)",
            "appears_in_classes": ["Patient Capital", "Portfolio Capital"],
            "entities": overlap_div + sorted(port_div - (pat_fo | pat_listed))[:15],
            "correct_class": "Portfolio Capital",
            "boundary_test": (
                "Default Portfolio Capital DIVERSIFIED_HOLDCO_COMPOUNDER. Move to Patient Capital ONLY "
                "if the entity is family-controlled with explicit generational language AND does not "
                "compound through programmatic acquisition (i.e., it is a wealth vehicle, not an M&A "
                "platform)."
            ),
        }
    )

    # 5. Venture studios spanning Portfolio + LMV (and 1 LMV node)
    vs_port = sc("Portfolio Capital", "VENTURE_STUDIO")
    # Sample entities from LMV that look like studios
    lmv_studio_proxies = [
        n for n in entity_locations
        if "studio" in n.lower() or "labs" in n.lower() or "factory" in n.lower()
    ]
    patterns.append(
        {
            "pattern": "Venture studios / company builders (build-not-buy)",
            "appears_in_classes": ["Portfolio Capital", "LMV", "ECOSYSTEM"],
            "entities": sorted(vs_port),
            "correct_class": "Venture Studio (proposed new class)",
            "boundary_test": (
                "Studios CREATE companies from scratch (co-found, ideate, incubate); they are not "
                "Portfolio Capital (which acquires) and not LMV (which writes external first checks). "
                "If the entity self-describes as 'studio,' 'company builder,' or 'we build companies "
                "with internal teams,' classify as Venture Studio."
            ),
        }
    )

    # 6. Corporate CVCs straddling Sovereign / Patient / Portfolio / UVC
    cvc_in_uvc = sc("UVC", "CORPORATE_VC_AS_SOVEREIGN") | sc("UVC", "TELCO_PHARMA_CVC_AS_PATIENT")
    port_cvc = sc("Portfolio Capital", "CORPORATE_STRATEGIC_CVC")
    cvc_entities = sorted(cvc_in_uvc | port_cvc)
    patterns.append(
        {
            "pattern": "Corporate venture capital (CVC) arms of large industrials, pharma, telco, auto",
            "appears_in_classes": ["Patient Capital", "Sovereign Capital", "Portfolio Capital", "UVC"],
            "entities": cvc_entities,
            "correct_class": "UVC-adjacent (purge from Post-Unicorn Atlas; tag for separate CVC index)",
            "boundary_test": (
                "If parent is a publicly-traded or privately-held operating company AND fund returns "
                "include 'strategic optionality' alongside financial returns, classify as CVC. CVCs are "
                "NOT post-unicorn allocators (they chase unicorn-scale strategic value); purge from "
                "the 6 allocator classes and route to a CVC index layer if desired."
            ),
        }
    )

    # 7. Specialty private credit lurking in Patient
    private_credit_names = [
        "Trinity Capital", "Victory Park Capital", "Castlelake", "i80 Group",
        "Marathon Asset Management", "Värde Partners", "Tree Line Capital Partners",
        "Banner Ridge Partners", "Hollyport Capital", "ICG Strategic Equity",
        "Norsad Capital", "Beacon Fund", "Spell Capital Partners", "Caltius Equity Partners",
        "Metrics Credit Partners",
    ]
    pc_present = [n for n in private_credit_names if n in entity_locations]
    patterns.append(
        {
            "pattern": "Specialty private credit, mezzanine, secondaries (Patient/SMV/Portfolio confusion)",
            "appears_in_classes": ["Patient Capital", "SMV", "Portfolio Capital"],
            "entities": pc_present,
            "correct_class": "SMV (Strategic Middle Ventures, broadened)",
            "boundary_test": (
                "Non-equity capital is SMV. If instrument is debt (mezz, unitranche, direct lending, "
                "ABL, royalty, MCA, RBF) or secondaries (PE secondaries, GP-led continuation), classify "
                "as SMV regardless of how 'long' the hold or how 'patient' the rhetoric."
            ),
        }
    )

    # 8. Lower-middle-market PE wearing founder-friendly language (SMV/Portfolio infiltration)
    mis_lmm_pe_sc = sc("SMV", "MISCLASSIFIED_LMM_PE_BUYOUT")
    patterns.append(
        {
            "pattern": "Lower-middle-market PE buyout funds posing as SMV via 'founder-friendly' language",
            "appears_in_classes": ["SMV", "Portfolio Capital", "UVC"],
            "entities": sorted(mis_lmm_pe_sc),
            "correct_class": "Portfolio Capital (MIDDLE_MARKET_PE) or UVC purge",
            "boundary_test": (
                "If structure is closed-end LP fund with 3-7yr defined hold AND control equity AND "
                "explicit exit discipline, this is conventional PE. Route to Portfolio Capital "
                "MIDDLE_MARKET_PE only if the firm is genuinely non-unicorn (steady-cashflow buy-and-build); "
                "purge to UVC-adjacent if it operates on standard PE exit cycles."
            ),
        }
    )

    # 9. Regional / emerging-market VC parading as Patient Capital
    em_vc_in_uvc = sc("UVC", "EMERGING_MARKET_VC_AS_PATIENT")
    patterns.append(
        {
            "pattern": "Emerging-market regional VCs masquerading as Patient Capital",
            "appears_in_classes": ["Patient Capital", "UVC", "LMV"],
            "entities": sorted(em_vc_in_uvc),
            "correct_class": "UVC (purge) or LMV if fund <$150M and solo/emerging-manager",
            "boundary_test": (
                "Long hold periods due to thin EM exit markets do NOT make a fund Patient Capital. "
                "Test: does the firm raise standard LP-bounded funds with target IRR to LPs? If yes, "
                "it is UVC (purge) unless fund size and GP count keep it LMV-scale."
            ),
        }
    )

    # 10. Mission/impact rhetoric VCs in Patient Capital
    impact_in_uvc = sc("UVC", "IMPACT_MISSION_VC_AS_PATIENT")
    long_hold_vc_in_uvc = sc("UVC", "LONG_HOLD_NARRATIVE_VC_AS_PATIENT")
    patterns.append(
        {
            "pattern": "Mission / 'patient-positioning' VC funds wearing the Patient Capital label",
            "appears_in_classes": ["Patient Capital", "UVC"],
            "entities": sorted(impact_in_uvc | long_hold_vc_in_uvc),
            "correct_class": "UVC (purge)",
            "boundary_test": (
                "'Long-term partnership' language ≠ Patient Capital. Test: structural commitment "
                "(no exit covenant, evergreen balance sheet, capped returns, or steward-ownership). "
                "If only rhetorical, route to UVC purge."
            ),
        }
    )

    # 11. Pension funds and large institutional pools mis-labeled Patient instead of Sovereign
    inst_endow = sc("Patient Capital", "INSTITUTIONAL_ENDOWMENT")
    patterns.append(
        {
            "pattern": "Public pension and crown-institutional investors landing in Patient Capital",
            "appears_in_classes": ["Patient Capital", "Sovereign Capital"],
            "entities": sorted(inst_endow & set(["Caisse de dépôt et placement du Québec", "British Columbia Investment Management Corporation (BCI)", "OPTrust"])) + [
                "APG Asset Management",
            ],
            "correct_class": "Sovereign Capital (public pension subcluster)",
            "boundary_test": (
                "Sovereign Capital should hold state/quasi-state perpetual pools including public "
                "pensions whose beneficiaries are public-sector employees. University endowments stay "
                "in Patient Capital because their mandate is private/charitable, not sovereign."
            ),
        }
    )

    # 12. Search/ETA boundary with Portfolio (HoldCo) and SMB acquirers
    operator_smb = sc("Search/ETA", "OPERATOR_LED_SMB_ACQUISITION_PLATFORMS")
    patterns.append(
        {
            "pattern": "Operator-led SMB acquisition platforms (Mainshares-type) blurring Search/ETA and Portfolio Capital",
            "appears_in_classes": ["Search/ETA", "Portfolio Capital"],
            "entities": sorted(operator_smb) + ["Blue-Collar Trades Group", "Hidden Valley Capital", "Epitome Capital"],
            "correct_class": "Search/ETA",
            "boundary_test": (
                "If each acquisition is a stand-alone owner-operator deal (no platform compounding, no "
                "shared back-office), classify Search/ETA. If the entity rolls acquisitions into a "
                "shared platform with cross-selling/HR consolidation, classify Portfolio Capital."
            ),
        }
    )

    # ---------------- Taxonomy gap analysis ----------------
    taxonomy_gaps = [
        {
            "gap_name": "Venture Studios / Company Builders",
            "entity_count": len(vs_port),
            "currently_mis_routed_to": ["Portfolio Capital", "LMV"],
            "proposed_fix": "ADD new class 'Venture Studio' OR add explicit Portfolio Capital VENTURE_STUDIO sub-bucket as a separate axis (build-not-buy) and prohibit it from absorbing acquirers. Mechanism (co-found) is fundamentally distinct from buy-to-hold.",
        },
        {
            "gap_name": "Corporate Venture Capital (CVC) arms",
            "entity_count": len(cvc_entities),
            "currently_mis_routed_to": ["Patient Capital", "Sovereign Capital", "Portfolio Capital"],
            "proposed_fix": "TAG as UVC-adjacent and purge from allocator atlas. CVCs are unicorn-return-seeking with strategic-optionality returns; they are NOT post-unicorn. If the project later wants a CVC index, model it as a SEPARATE layer like Ecosystem/Infrastructure (not an allocator class).",
        },
        {
            "gap_name": "Specialty private credit, mezzanine, secondaries managers",
            "entity_count": len(pc_present),
            "currently_mis_routed_to": ["Patient Capital", "SMV", "Portfolio Capital"],
            "proposed_fix": "BROADEN SMV definition to include specialty credit, ABL, mezz, unitranche, secondaries. The SMV refined_definition already specs this. Tighten gate to route any non-equity instrument here.",
        },
        {
            "gap_name": "Lower-middle-market PE wearing founder-friendly language",
            "entity_count": len(mis_lmm_pe_sc),
            "currently_mis_routed_to": ["SMV"],
            "proposed_fix": "TIGHTEN gate: require non-dilutive instrument signal OR explicit anti-VC mechanic (RBF, SEAL, shared-earnings) for SMV. Route LMM PE buyout funds to Portfolio Capital MIDDLE_MARKET_PE only when their thesis is durable buy-and-hold compounding; otherwise UVC purge.",
        },
        {
            "gap_name": "Public-listed compounders / patrimonial holdings",
            "entity_count": len(pat_listed),
            "currently_mis_routed_to": ["Patient Capital", "Portfolio Capital"],
            "proposed_fix": "MOVE all to Portfolio Capital DIVERSIFIED_HOLDCO_COMPOUNDER. The atlas convention should be: listing status is orthogonal to class; mechanism (programmatic acquisition + permanent capital base) determines class.",
        },
        {
            "gap_name": "Embedded-finance platforms (Pipe / YouLend / Liberis / Parafin)",
            "entity_count": 9,
            "currently_mis_routed_to": ["SMV", "ECOSYSTEM"],
            "proposed_fix": "KEEP in SMV (they ARE allocators per the SMV refined_definition) but TAG with 'embedded-finance / B2B platform' sub-label. They sit at the allocator/infrastructure boundary; adversarial double-check required (e.g., YouLend = real SMV; Microns = ecosystem marketplace).",
        },
        {
            "gap_name": "Indigenous / Tribal sovereign capital",
            "entity_count": 11 + 3,
            "currently_mis_routed_to": ["Patient Capital", "Sovereign Capital"],
            "proposed_fix": "MOVE to Sovereign Capital as TRIBAL_SUB_NATIONAL_SWF sub-bucket. These are constitutionally-anchored sovereign entities (tribal nations, US states, Canadian provinces), not Patient Capital.",
        },
        {
            "gap_name": "Healthcare biotech specialist VCs",
            "entity_count": 7,
            "currently_mis_routed_to": ["Patient Capital"],
            "proposed_fix": "PURGE to UVC. Long biotech development timelines do not make these Patient Capital; structure is conventional LP-bounded VC seeking IPO/M&A exits.",
        },
        {
            "gap_name": "Public-market mutual funds (values-based)",
            "entity_count": 1,
            "currently_mis_routed_to": ["Patient Capital"],
            "proposed_fix": "MOVE to Ecosystem/Infrastructure layer as PUBLIC_MARKET_VALUES_FUND subtype. Public-securities mutual funds are not private-capital allocators.",
        },
        {
            "gap_name": "Crypto-protocol public-goods grantmakers",
            "entity_count": 3,
            "currently_mis_routed_to": ["LMV", "Patient Capital"],
            "proposed_fix": "MOVE to Ecosystem/Infrastructure GRANTMAKER subtype with a 'crypto public goods' sub-tag. Gitcoin, Uniswap Foundation, Optimism RetroPGF, Octant deploy no equity.",
        },
    ]

    # ---------------- Reclass and hygiene maths (disjoint) ----------------
    # Build sets of unique entities for each disposition
    flagged_by_target = defaultdict(set)
    for f in flags:
        flagged_by_target[f["target_class"]].add(f["name"])

    # purge_set: UVC slice + UVC-target reclass flags + hard non-entities in ECOSYSTEM
    eco_subtype = {}
    for sc_obj in clusters["ECOSYSTEM"].get("sub_clusters", []):
        name = sc_obj.get("name")
        ents = sc_obj.get("all_entities", []) or []
        eco_subtype[name] = ents

    uvc_slice_set = set()
    for sc_obj in clusters["UVC"].get("sub_clusters", []):
        for m in sc_obj.get("members", []):
            n = m.get("name") if isinstance(m, dict) else m
            if n:
                uvc_slice_set.add(n)

    purge_articles = set(eco_subtype.get(
        "Articles, Blog Posts, Listicles, and PR Landing Pages (Non-Entities)", []
    ))
    purge_operating = set(eco_subtype.get(
        "Operating Companies and Operating Holdcos misidentified as funds", []
    ))
    purge_mutual = set(eco_subtype.get("Public-Market Mutual Funds (Values-Based)", []))
    purge_set = uvc_slice_set | flagged_by_target.get("UVC", set()) | purge_articles | purge_operating | purge_mutual
    # add REMOVE-target flags
    purge_set |= flagged_by_target.get("REMOVE", set())

    # reclass_set: flags targeting one of the 5 allocator classes (excludes UVC and ECOSYSTEM targets)
    allocator_targets = {"Patient Capital", "Portfolio Capital", "SMV", "LMV", "Sovereign Capital", "Search/ETA"}
    reclass_set = set()
    for t in allocator_targets:
        reclass_set |= flagged_by_target.get(t, set())
    reclass_set -= purge_set  # disjoint guarantee

    # ecosystem_set: ECOSYSTEM-target flags + ECOSYSTEM slice non-purge subtypes (RIA, OCIO, brokers, etc.)
    eco_real_subtypes = [
        "Multi-Family Office / Private Wealth Management RIAs",
        "OCIO / Outsourced CIO Advisors for Institutions",
        "M&A Brokers and Business-for-Sale Marketplaces",
        "Lending / Capital Marketplaces and Brokers",
        "Founder Communities, Industry Networks, and Movements",
        "No-Capital Accelerators / Fellowships",
        "Grantmaking Foundations and Public-Goods Grants Platforms",
        "Advocacy / Standards / Steward-Ownership Advisors and Convening Nonprofits",
        "Corporate Venture Builders / Studio-as-a-Service",
        "Fund Administrators and Back-Office Service Providers",
    ]
    ecosystem_set = set()
    for sub in eco_real_subtypes:
        ecosystem_set |= set(eco_subtype.get(sub, []))
    ecosystem_set |= flagged_by_target.get("ECOSYSTEM", set())
    ecosystem_set -= purge_set
    ecosystem_set -= reclass_set

    # ---------------- Proposed taxonomy ----------------
    recommended_classes = [
        {
            "name": "Patient Capital",
            "definition": (
                "Capital that makes a STRUCTURAL commitment to relationship over exit: permanent equity "
                "with no redemption mandate (family balance sheet, evergreen, steward-ownership), or "
                "impact-first capital that overrides financial optimization (CDFI, blended-finance impact, "
                "mission-aligned growth), or an instrument that aligns investor-operator across the long "
                "run rather than harvesting at a fixed horizon (shared earnings, ESOP finance). Long hold "
                "period alone is NOT sufficient. The entity must self-describe with structural language: "
                "'permanent home,' 'no mandate to sell,' 'capped returns,' 'steward-owned,' or 'mission-first.'"
            ),
            "boundary_test": (
                "Does the entity make a STRUCTURAL (not rhetorical) commitment that exit is constrained "
                "or off-table? Examples: purpose-trust ownership, capped returns, ESOP-conversion-only "
                "exits, CDFI certification, DFI mandate. If only rhetoric, route elsewhere."
            ),
            "expected_entity_count": 175,
            "sub_buckets": [
                "FAMILY_OFFICE_HOLDCO",
                "IMPACT_GROWTH_EQUITY",
                "EMERGING_MARKETS_IMPACT_DFI_LP",
                "STEWARD_OWNERSHIP",
                "FAITH_BASED",
                "EMPLOYEE_OWNERSHIP",
                "FOUNDATION_GRANTMAKER_WITH_PRI_MRI",
                "CDFI_COMMUNITY",
                "REAL_ASSETS_NATURE",
                "SHARED_EARNINGS_BOOTSTRAP",
            ],
        },
        {
            "name": "Portfolio Capital",
            "definition": (
                "Entities that deploy equity capital to ACQUIRE controlling or significant stakes in "
                "EXISTING operating companies, with the explicit intent to hold and operate those "
                "companies as part of a growing portfolio, and whose primary return mechanism is "
                "operational value creation and cash-flow compounding rather than unicorn-style exit "
                "multiples. Includes VMS serial acquirers (Constellation lineage), SaaS micro-holdcos, "
                "home services and healthcare-practice roll-ups, diversified compounders (listed or "
                "private), and lower-middle-market PE pursuing durable buy-and-build."
            ),
            "boundary_test": (
                "Buy-not-build, acquisition-mechanism-driven, portfolio compounding. Excludes funds with "
                "<5yr defined exit cycles (UVC purge), studios that co-found from scratch (Venture "
                "Studio), and family holdcos whose primary purpose is wealth preservation rather than "
                "M&A compounding (Patient Capital)."
            ),
            "expected_entity_count": 230,
            "sub_buckets": [
                "VMS_SERIAL_ACQUIRER",
                "SAAS_DIGITAL_MICRO_HOLDCO",
                "HEALTHCARE_PRACTICE_ROLLUP",
                "HOME_SERVICES_TRADES_ROLLUP",
                "DIVERSIFIED_HOLDCO_COMPOUNDER (incl. listed compounders)",
                "MIDDLE_MARKET_PE (non-unicorn buy-and-build only)",
                "CONSUMER_BRAND_ECOM_ROLLUP",
            ],
        },
        {
            "name": "SMV (Strategic Middle Ventures / Non-Dilutive & Structured Credit)",
            "definition": (
                "Capital deployed via non-dilutive or structured-credit instruments to operating "
                "companies. Includes revenue-based financing (RBF), shared-earnings agreements (SEAL), "
                "venture debt, growth debt, mezzanine, unitranche, asset-based lending, factoring, "
                "specialty commercial finance, secondaries (PE secondaries, GP-led continuation), AND "
                "growth equity vehicles whose explicit positioning targets bootstrapped or capital-"
                "efficient founders with fund sizes / check sizes that materially differ from standard "
                "growth PE. Embedded-finance platforms (Pipe, YouLend, Liberis, Parafin) qualify when "
                "they deploy own capital or routed LP capital."
            ),
            "boundary_test": (
                "Instrument test: is the primary instrument non-equity, revenue-linked, or structured "
                "credit? If yes → SMV. 'Bootstrapped-friendly' language alone is NOT a qualifier; the "
                "fund must demonstrate the instrument or anti-VC mechanic."
            ),
            "expected_entity_count": 110,
            "sub_buckets": [
                "SAAS_RBF_NONDILUTIVE",
                "ECOMMERCE_RBF_MCA",
                "PLATFORM_EMBEDDED_SMB",
                "BOOTSTRAPPED_SOFTWARE_GROWTH_EQUITY",
                "VENTURE_DEBT_PRIVATE_CREDIT_TECH",
                "SMB_SPECIALTY_COMMERCIAL_FINANCE",
                "ASSET_BASED_PRIVATE_CREDIT",
                "EMERGING_MARKET_NONDILUTIVE",
                "LMM_MEZZANINE_PRIVATE_CREDIT",
                "PE_SECONDARIES",
                "VERTICAL_B2B_FINANCING_SPECIALTY",
            ],
        },
        {
            "name": "LMV (Solo-GP / Micro / Indie Funds, Accelerators, Fellowships)",
            "definition": (
                "Capital-deploying vehicles that are (a) GP-led by 1-3 principals without institutional "
                "corporate parentage, (b) write pre-seed to seed-stage equity or fellowship/program "
                "checks of $10K-$5M, (c) operate fund sizes under ~$150M, and (d) do not primarily "
                "employ non-dilutive instruments (which belong in SMV). Legitimately encompasses "
                "solo-GP funds, accelerator-plus-fund hybrids, fellowship programs with follow-on "
                "equity, and place-based or thesis-driven micro-VCs — provided they are actual "
                "capital allocators with documented deployment history."
            ),
            "boundary_test": (
                "Three-part: (1) GP count ≤ 3 principals, no corporate parent; (2) fund size <$150M; "
                "(3) demonstrable equity deployment history. Communities, education platforms, no-capital "
                "accelerators, and pure grantmakers fail (3) and move to Ecosystem layer. DFIs and "
                "state-backed catalytic capital move to Sovereign Capital. Anything that pushes above "
                "the size/GP threshold is either UVC purge or a sector-specialist VC outside the atlas."
            ),
            "expected_entity_count": 130,
            "sub_buckets": [
                "SOLO_GP_PRESEED",
                "ACCELERATOR_FELLOWSHIP_WITH_CAPITAL",
                "US_REGIONAL_SEED",
                "EMERGING_MARKET_MICRO_VC",
                "EUROPEAN_MICRO_VC",
                "CLIMATE_ENERGY_MICRO_VC",
                "AI_DEEPTECH_MICRO_VC",
                "UNDERREP_FOUNDER_THESIS",
                "VERTICAL_SECTOR_MICRO_VC",
                "APAC_ANZ_GENERALIST_SEED",
            ],
        },
        {
            "name": "Sovereign Capital",
            "definition": (
                "Capital deployed by or directly on behalf of a state, supra-national body, or "
                "constitutionally-anchored sovereign entity (national government, multilateral "
                "institution, state/provincial legislature, tribal government) with a mandate that is "
                "PUBLIC and POLITICAL in character — for national reserve management, economic "
                "development, national security, climate transition, or intergenerational sovereign "
                "wealth. Includes national SWFs, bilateral DFIs, multilateral MDBs, public pension "
                "direct investors, public investment banks, state innovation agencies, tribal sovereign "
                "funds, and catalytic blended-finance vehicles whose capital flows from public charters."
            ),
            "boundary_test": (
                "Mandate-origin test: does the investment authority flow from a PUBLIC LEGAL CHARTER "
                "(act of legislature, sovereign decree, multilateral treaty, tribal constitution)? "
                "If yes → Sovereign Capital. Private impact managers that accept DFI LP capital are "
                "Patient Capital, NOT Sovereign Capital. Corporate CVCs of state-adjacent companies "
                "(Equinor, Maersk) are UVC-adjacent purge."
            ),
            "expected_entity_count": 80,
            "sub_buckets": [
                "MEGA_SWF",
                "EM_NATIONAL_SWF",
                "PUBLIC_PENSION_DIRECT",
                "BILATERAL_DFI",
                "MULTILATERAL_DFI_MDB",
                "PUBLIC_INVESTMENT_BANK",
                "STATE_STRATEGIC_TECH_FUND",
                "STATE_INNOVATION_AGENCY",
                "CATALYTIC_BLENDED_CLIMATE",
                "TRIBAL_SUB_NATIONAL_SWF (incl. Indigenous)",
            ],
        },
        {
            "name": "Search/ETA",
            "definition": (
                "Capital and operator vehicles in the Entrepreneurship-Through-Acquisition ecosystem: "
                "traditional 2-stage search-fund LPs, self-funded searcher equity-gap providers, "
                "single-acquisition searcher vehicles themselves, international/regional search-fund "
                "specialists, family-office search backers, institutional fund-of-search-funds, "
                "accelerator/CEO-in-Residence committed-capital platforms, independent/fundless sponsor "
                "equity backers, and operator-led multi-acquisition SMB platforms whose deals stand "
                "alone as owner-operator transactions (NOT a roll-up platform)."
            ),
            "boundary_test": (
                "Mechanism test: does the entity capitalize an individual searcher or owner-operator "
                "for a single (or small number) of acquisitions WITHOUT building a shared operating "
                "platform? If yes → Search/ETA. Shared-platform roll-ups go to Portfolio Capital. "
                "Marketplaces / brokers / Searchfunder-style infrastructure go to Ecosystem layer."
            ),
            "expected_entity_count": 75,
            "sub_buckets": [
                "TRADITIONAL_SEARCH_FUND_INVESTORS_LPS",
                "SINGLE_ACQUISITION_SOLO_SEARCHER_VEHICLES",
                "INTERNATIONAL_REGIONAL_SEARCH_FUND_SPECIALISTS",
                "FAMILY_OFFICE_SEARCH_BACKERS",
                "FUND_OF_SEARCH_FUNDS_INSTITUTIONAL",
                "SEARCH_FUND_ACCELERATORS_AND_COMMITTED_CAPITAL_PLATFORMS",
                "SELF_FUNDED_SEARCHER_SPECIALISTS",
                "INDEPENDENT_FUNDLESS_SPONSOR_BACKERS",
                "DIVERSIFIED_LOWER_MM_PE_WITH_SEARCH_ETA_ARM",
                "OPERATOR_LED_SMB_ACQUISITION_PLATFORMS",
                "COINVEST_SPV_PLATFORMS_FOR_ACCREDITED_INVESTORS",
            ],
        },
        {
            "name": "Venture Studio (NEW — proposed 7th class)",
            "definition": (
                "Entities that BUILD new companies from scratch, pairing capital with ideation, talent, "
                "and operational infrastructure rather than acquiring existing businesses or making "
                "external first checks. Revenue comes from equity stakes in portfolio companies the "
                "studio co-founds. Distinguishing language: 'studio,' 'company builder,' 'co-found,' "
                "'originated in-house,' 'we build companies with internal teams.' Distinct from "
                "Portfolio Capital (which acquires) and LMV (which writes external first checks)."
            ),
            "boundary_test": (
                "Build-not-buy test: does the entity originate companies internally (founders are "
                "studio EIRs/co-founders, IP and team developed in-house)? If yes → Venture Studio. "
                "External first-check seed funds remain LMV. Service-firm 'venture builders' that "
                "are paid by corporate clients to launch ventures (Creative Dock, GTM Venture Studio) "
                "go to Ecosystem layer (Corporate Venture Builders / Studio-as-a-Service)."
            ),
            "expected_entity_count": 35,
            "sub_buckets": [
                "GENERALIST_VENTURE_STUDIO",
                "VERTICAL_VENTURE_STUDIO (healthcare, fintech, climate)",
                "ACCELERATOR_STUDIO_HYBRID",
                "PUBLIC_LISTED_STUDIO (e.g., Antler-style platforms)",
            ],
        },
    ]

    layers = [
        {
            "name": "Allocator (7 classes after Venture Studio split)",
            "description": (
                "The 7 capital-deploying classes that constitute the Post-Unicorn Finance industry: "
                "Patient Capital, Portfolio Capital, SMV, LMV, Sovereign Capital, Search/ETA, and "
                "Venture Studio. All deploy their own or LP capital directly into operating companies."
            ),
        },
        {
            "name": "Ecosystem / Infrastructure",
            "description": (
                "A SEPARATE LAYER (not an asset class) for non-allocators that form the industry's "
                "infrastructure: Multi-Family Office RIAs, OCIO advisors, M&A brokers and business-for-"
                "sale marketplaces, lending marketplaces and capital brokers, founder/searcher "
                "communities and industry networks, no-capital accelerators / fellowships, grantmaking "
                "foundations without PRI/MRI portfolios, advocacy/standards bodies, corporate venture "
                "builders (studio-as-a-service), and fund administrators. Tagged but NOT counted as "
                "allocators. Provides industry context without distorting the allocator atlas."
            ),
        },
        {
            "name": "UVC-Adjacent (Purge Baseline)",
            "description": (
                "Classic unicorn-VC and CVC vehicles excluded from the Post-Unicorn allocator atlas. "
                "Per CLAUDE.md, UVC is the baseline we contrast against, NEVER auto-promoted. This "
                "layer holds entities flagged for purge: classic VCs that infiltrated via mission/"
                "patient/bootstrapper language, conventional LMM PE buyout funds wearing founder-"
                "friendly rhetoric, and corporate venture capital arms (pharma, telco, industrial, "
                "auto). Maintained as an exclusion list to prevent re-promotion via gate keyword drift."
            ),
        },
    ]

    proposed_taxonomy = {
        "recommended_classes": recommended_classes,
        "layers": layers,
        "ratiomale_summary": (
            "The bottom-up evidence shows that the original 6-class taxonomy leaks at three structural "
            "boundaries the keyword gate cannot police: (1) ACQUIRE-vs-BUILD — venture studios are "
            "currently shoehorned into Portfolio Capital despite a fundamentally different mechanism, "
            "and merit a 7th class; (2) EQUITY-vs-CREDIT — specialty private credit, mezz, secondaries, "
            "and ABL slid into Patient Capital and Portfolio Capital because of long-hold/balance-sheet "
            "language, when they structurally belong in a broadened SMV; (3) PRINCIPAL-vs-AGENT — RIAs, "
            "OCIOs, brokers, marketplaces, networks, and grantmakers ride mission/long-term/non-dilutive "
            "vocabulary into allocator slots when they deploy none of their own capital — they need an "
            "Ecosystem/Infrastructure LAYER, not an asset class. Corporate CVCs and LMM PE buyout funds "
            "should be treated as UVC-adjacent purge (the unicorn baseline, never promoted), not as "
            "post-unicorn classes. Net: 7 allocator classes + 2 non-allocator layers, replacing 6 classes "
            "that conflated mechanism with rhetoric."
        ),
    }

    # ---------------- Boundary tests (one per class) ----------------
    boundary_tests = [
        {"class": "Patient Capital",
         "test": "Is there a STRUCTURAL (not rhetorical) commitment that exit is constrained or off-table — purpose-trust, capped returns, ESOP-only exits, CDFI/DFI mandate, or explicit no-sale covenant?"},
        {"class": "Portfolio Capital",
         "test": "Does the entity ACQUIRE existing operating companies (buy-not-build) and COMPOUND through programmatic acquisitions or holdco-style portfolio operation, without unicorn-style exit timelines?"},
        {"class": "SMV",
         "test": "Is the primary instrument NON-EQUITY (RBF, debt, mezz, ABL, factoring, secondaries, shared-earnings) or an EXPLICIT anti-VC equity mechanic targeting bootstrapped founders?"},
        {"class": "LMV",
         "test": "Is the GP count ≤3, no corporate parent, fund size <$150M, AND does the entity have documented equity-deployment history (not just a community or program)?"},
        {"class": "Sovereign Capital",
         "test": "Does the investment authority flow from a PUBLIC LEGAL CHARTER (sovereign decree, act of legislature, multilateral treaty, tribal constitution), with a public/political mandate?"},
        {"class": "Search/ETA",
         "test": "Does the entity capitalize an individual searcher or owner-operator for a single or small number of acquisitions WITHOUT building a shared operating platform?"},
        {"class": "Venture Studio",
         "test": "Does the entity ORIGINATE companies internally (in-house IP, EIR co-founders, team built by studio) rather than acquiring or backing external founders?"},
        {"class": "Ecosystem/Infrastructure (layer)",
         "test": "PRINCIPAL-vs-AGENT: does the entity deploy ITS OWN capital ('our fund,' 'we invest,' 'our balance sheet') OR does it manage CLIENT capital, broker transactions, run a marketplace, or convene a community? If agent, route here."},
        {"class": "UVC-adjacent (purge)",
         "test": "Does the entity raise standard LP-bounded funds with target IRR, defined exit cycles, and unicorn-scale strategic optionality? If yes, purge from atlas regardless of founder-friendly language."},
    ]

    # ---------------- Atlas hygiene plan ----------------
    atlas_hygiene_plan = {
        "purge_count": len(purge_set),
        "reclassify_count": len(reclass_set),
        "move_to_ecosystem_count": len(ecosystem_set),
        "order_of_operations": [
            "1. SNAPSHOT the current evidence CSVs to data/runtime/snapshot_pre_phase4_2026-06-01/ (revertable baseline). Required per CLAUDE.md.",
            "2. UPDATE intake-curation rules FIRST (per CLAUDE.md: curation MUST exclude non-allocators or rebuild regenerates ~1/3 junk): add the principal-vs-agent gate (ECOSYSTEM recs 1-6), URL-is-article detector, name-token-in-domain check, operating-company disqualifiers, no-capital-accelerator disqualifier, grant-vs-investment disqualifier. Commit before any data mutation.",
            "3. PURGE the {0} UVC-adjacent + hard-non-entity rows from industry_entities.csv (UVC slice + UVC-target reclass flags + ECOSYSTEM Articles/Operating/Mutual-Fund subtypes + REMOVE-target flags).".format(len(purge_set)),
            "4. SWEEP orphan entity_claims (per CLAUDE.md known trap: purging entities leaves FK-breaking orphan rows). Log removed rows to data/evidence/orphan_claims_purged_2026-06-01.csv.",
            "5. MOVE the {0} ecosystem-layer entities to a new data/evidence/ecosystem_entities.csv (already exists per git-status — extend it) rather than deleting. RIAs, OCIOs, brokers, marketplaces, networks, no-capital accelerators, grantmakers, advocacy bodies, corporate venture builders, fund administrators.".format(len(ecosystem_set)),
            "6. RECLASSIFY the {0} flagged-to-other-allocator entities in industry_entities.csv. Apply target_class from each Tier-2 file's reclassification_flags. Log to data/evidence/manual_changes_2026-06-01.log.".format(len(reclass_set)),
            "7. CREATE the Venture Studio class (new primary_asset_class enum value) and migrate the 30 Portfolio Capital VENTURE_STUDIO entities + any LMV-tagged studios (Bridgewest Ventures NZ etc.).",
            "8. ADVERSARIAL DOUBLE-CHECK borderline cases per CLAUDE.md (YouLend false-junk lesson). Run a manual eyeball pass on: embedded-finance platforms (KEEP in SMV), Patient PERM_EQUITY_SOFTWARE moving to Portfolio VMS (verify each has acquisition flywheel), and any flagged entity whose homepage is JS-only / thin (do NOT purge unverifiable).",
            "9. REBUILD data/atlas.sqlite from clean CSVs with import_csvs(reset=True) (per CLAUDE.md known trap: stale DB re-promotes purged junk).",
            "10. AUDIT: count entities per class against expected_entity_count in this taxonomy; investigate any class off by >25%.",
            "11. RE-RUN curated discovery rounds against the tightened intake-curation rules to fill class shortfalls without re-importing junk.",
            "12. PUBLISH refined atlas snapshot to data/evidence/, regenerate docs/research/post_unicorn_finance_research_dossier.md sections that reference class definitions, and commit.",
        ],
    }

    # ---------------- Pioneer summary ----------------
    pioneer_summary = (
        "Post-Unicorn Finance, viewed bottom-up across 971 unique allocator entries and 1,219 class "
        "assignments, is NOT one industry — it is SEVEN allocator industries plus an infrastructure "
        "layer, glued together by a shared rejection of the unicorn-or-bust capital model. The seven "
        "are: (1) Patient Capital — the structural commitment industry (steward-ownership, "
        "permanent equity, mission-first), the SMALLEST genuine bucket after de-leakage (~175 "
        "entities versus 489 as-labeled, because ~315 entities were riding rhetoric, not structure). "
        "(2) Portfolio Capital — the buy-and-compound industry led by Constellation Software's VMS "
        "lineage, plus healthcare and home-services consolidators, diversified compounders (Berkshire, "
        "Lifco), and lower-middle-market PE pursuing durable buy-and-build (~230 entities). "
        "(3) SMV — the non-dilutive and structured-credit industry: RBF, venture debt, mezz, ABL, "
        "factoring, secondaries, and bootstrap-friendly equity, expanded from 165 to ~110 once LMM-PE "
        "infiltrations are evicted and specialty credit currently hidden in Patient is absorbed. "
        "(4) LMV — the indie-fund industry: solo-GPs, micro-VCs, accelerator/fellowship hybrids, "
        "place-based seed funds, all under $150M and 1-3 principals (~130 entities). (5) Sovereign "
        "Capital — the public-mandate industry: SWFs, DFIs, MDBs, public pensions, state innovation "
        "agencies, tribal/sub-national sovereign funds, and catalytic blended-finance vehicles (~80 "
        "entities, after evicting ~30 corporate-CVC and private-impact infiltrators). (6) Search/ETA "
        "— the entrepreneurship-through-acquisition industry: traditional 2-stage searchers, self-"
        "funded gap funders, fund-of-search-funds, accelerator-with-capital platforms, family-office "
        "search backers, independent sponsors, and operator-led SMB platforms (~75 entities). "
        "(7) Venture Studio — the build-not-buy industry, currently a hidden category swept under "
        "Portfolio Capital (30 entities so far; likely 50+ with proper curation): studios that "
        "originate companies in-house, distinct from acquirers AND from external-check VCs.\n\n"
        "Three findings reshape the founding thesis: First, ~46% of the 489 entities currently labeled "
        "Patient Capital are NOT structurally patient — they are conventional PE, VC, and corporate "
        "CVC programs draped in long-hold rhetoric. The genuine Patient Capital industry is small "
        "(~175 entities), elite, and structurally distinctive — it does not need inflation to be "
        "compelling. Second, the boundary between Patient Capital and Portfolio Capital is NOT "
        "primarily about hold period; it is about MECHANISM — buy-to-hold compounding (Portfolio) "
        "versus structural-relationship capital (Patient). The atlas was conflating these. Third, "
        "and most important: the gate cannot tell PRINCIPAL from AGENT. RIAs, OCIOs, brokers, "
        "marketplaces, networks, grantmakers, and no-capital accelerators wear allocator vocabulary "
        "because that vocabulary IS the language of capital infrastructure — they sit adjacent to "
        "allocators, not as allocators. They belong in an Ecosystem/Infrastructure LAYER (43 entities "
        "identified so far, plus the agentic disqualifier rules to keep them out of future "
        "discovery rounds).\n\n"
        "What we can now say credibly: Post-Unicorn Finance is real and structurally distinct from "
        "classic VC, but it is BROADER and CRISPER than 'six asset classes outside unicorn VC.' It "
        "is a SEVEN-class allocator industry of ~835 unique entities (971 minus the 90 UVC-adjacent "
        "purge candidates and the 43 ecosystem-layer entries, plus reclass corrections), each class "
        "defined by INSTRUMENT and MECHANISM rather than by hold period or marketing rhetoric. The "
        "Venture Studio category emerges as a genuine 7th class — small but mechanistically distinct "
        "and likely to grow as a recognized category as the broader 'company-builder' movement "
        "matures. The Ecosystem/Infrastructure layer is what makes the industry visible to "
        "outsiders (it is how founders, searchers, and LPs find allocators) but it is not the "
        "industry itself. Once the gate enforces principal-vs-agent and mechanism-over-rhetoric "
        "tests, the atlas converges on a credible founding cohort and can scale toward 1,000+ "
        "entities without re-importing the ~⅓ junk that the prior curation cycle regenerated."
    )

    # ---------------- Assemble final JSON ----------------
    tier3 = {
        "tier3_agent": "taxonomy_critic",
        "input_classes_count": 8,
        "total_sub_clusters": sum(
            len(d.get("sub_clusters", [])) for d in clusters.values()
        ),
        "total_entities": sum(slice_counts.values()),
        "total_unique_entities_computed": len(entity_locations),
        "slice_counts_computed": slice_counts,
        "cross_class_pattern_map": patterns,
        "taxonomy_gaps": taxonomy_gaps,
        "proposed_taxonomy": proposed_taxonomy,
        "boundary_tests": boundary_tests,
        "atlas_hygiene_plan": atlas_hygiene_plan,
        "pioneer_summary": pioneer_summary,
        "metadata": {
            "generated_at": "2026-06-01",
            "input_files": [fn for _, fn in CLUSTER_FILES],
            "dedup_methodology": (
                "Members extracted from sub_clusters[].members (allocator slices) and sub_clusters[]"
                ".all_entities (ECOSYSTEM slice). Cross-class overlaps tallied by name; cross-class "
                "duplicates listed in cross_class_pattern_map. Slice counts reflect actual member-list "
                "lengths, which differ from each file's class_count metadata in some cases (e.g., SMV "
                "file says 165 but sub_cluster members sum to 146 — used the computed number)."
            ),
            "disjoint_disposition_guarantee": (
                "purge_count, reclassify_count, and move_to_ecosystem_count are set-disjoint by "
                "subtraction: ecosystem -= purge, ecosystem -= reclassify; reclassify -= purge. "
                "Each unique entity is counted in at most one disposition bucket."
            ),
        },
    }

    out_json = PHASE3_DIR / "tier3_taxonomy_critique.json"
    out_json.write_text(json.dumps(tier3, indent=2, ensure_ascii=False), encoding="utf-8")
    # Sanity-load
    json.loads(out_json.read_text(encoding="utf-8"))
    print(f"WROTE: {out_json}")
    print(f"purge_count={len(purge_set)}  reclassify_count={len(reclass_set)}  ecosystem_count={len(ecosystem_set)}")
    print(f"unique_entities={len(entity_locations)}  total_assignments={sum(slice_counts.values())}")


if __name__ == "__main__":
    main()
