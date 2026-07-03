"""Phase-0 build: transform the verified research-workflow JSON into the study's
research deliverables. Deterministic — every field is copied from the workflow
output (which was schema-forced to carry source URLs and adversarially verified).
No values are invented here. Run once; kept for reproducibility/audit.
"""
import argparse
import json, csv, re, os
from collections import Counter, defaultdict
from pathlib import Path

BASE = str(Path(__file__).resolve().parent)
DEFAULT_SRC = os.path.join(BASE, "data", "raw", "phase0_claude_output_2026-06-17.json")
TODAY = "2026-06-17"


def parse_args():
    parser = argparse.ArgumentParser(
        description="Rebuild Phase-0 economic-impact study artifacts from the verified workflow JSON."
    )
    parser.add_argument(
        "--source",
        default=DEFAULT_SRC,
        help="Path to the Phase-0 workflow JSON. Defaults to the repo-local raw source copy.",
    )
    return parser.parse_args()


ARGS = parse_args()
SRC = ARGS.source
if not os.path.isabs(SRC):
    SRC = os.path.join(BASE, SRC)
if not os.path.exists(SRC):
    raise SystemExit(f"Source JSON not found: {SRC}")

print("using source", SRC)
raw = json.load(open(SRC, encoding="utf-8"))
R = raw["result"]


def w(path, text):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(text)
    print("wrote", path, len(text), "chars")


def esc(s):
    if s is None:
        return ""
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def num(s):
    """Extract a numeric magnitude from a messy string; None if not parseable."""
    if not s or not isinstance(s, str):
        return None
    t = s.lower().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(billion|bn|million|mn|m|k|thousand)?", t)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2)
    mult = {"billion": 1e9, "bn": 1e9, "million": 1e6, "mn": 1e6, "m": 1e6,
            "k": 1e3, "thousand": 1e3}.get(unit, 1)
    return val * mult


def parse_money(s):
    """Extract a capital amount ONLY when tied to a currency symbol or a magnitude
    word, so bare years and stray integers are not mistaken for dollars."""
    if not s or not isinstance(s, str):
        return None
    t = s.lower().replace(",", "")
    m = re.search(r"[$£€]\s*(\d+(?:\.\d+)?)\s*(billion|bn|million|mn|m|k|thousand)?", t)
    if not m:
        m = re.search(r"(\d+(?:\.\d+)?)\s*(billion|bn|million|mn|thousand)", t)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2)
    mult = {"billion": 1e9, "bn": 1e9, "million": 1e6, "mn": 1e6, "m": 1e6,
            "k": 1e3, "thousand": 1e3}.get(unit, 1)
    # a bare currency number with no magnitude unit below 100k is implausible as capital
    if unit is None and val < 100000:
        return None
    return val * mult


# ---------------------------------------------------------------- 02 catalog
mechs = []
for g in R["catalog"]:
    mechs += g.get("mechanisms", [])
# dedupe by name
seen = {}
for m in mechs:
    seen.setdefault(m.get("name", "").strip().lower(), m)
mechs = list(seen.values())

unknown = [m for m in mechs if m.get("likely_unknown_to_ethan")]
by_cat = defaultdict(list)
for m in mechs:
    by_cat[m.get("category", "Other")].append(m)

lines = []
lines.append("# Mechanism Catalog — Worker Value-Sharing\n")
lines.append("Broad-and-deep catalog of mechanisms for sharing a company's created value with its workers. "
             "Every entry is source-cited from the Phase-0 research workflow (2026-06-17); each was generated "
             "under an anti-hallucination rule (real source URL required or the value is omitted). "
             f"**{len(mechs)} mechanisms** across {len(by_cat)} categories.\n")
lines.append("> Posture: descriptive. Inclusion here is *not* an endorsement or a claim of impact — the "
             "causal question is handled separately in `03_evidence_synthesis.md`.\n")

lines.append("\n## Quick index — mechanisms a generalist VC likely does NOT know\n")
lines.append("Extracted for the conversation with Ethan (his \"possibly even terms I do not know\").\n")
if unknown:
    for m in sorted(unknown, key=lambda x: x.get("name", "")):
        lines.append(f"- **{esc(m.get('name'))}** — {esc(m.get('definition'))}")
else:
    lines.append("_None flagged._")
lines.append("")

for cat in sorted(by_cat):
    lines.append(f"\n## {cat}\n")
    for m in sorted(by_cat[cat], key=lambda x: x.get("name", "")):
        flag = "  ·  ⚑ likely unfamiliar to a generalist VC" if m.get("likely_unknown_to_ethan") else ""
        lines.append(f"### {esc(m.get('name'))}{flag}\n")
        lines.append(f"- **What it is:** {esc(m.get('definition'))}")
        if m.get("how_it_works"):
            lines.append(f"- **How it works:** {esc(m.get('how_it_works'))}")
        if m.get("legal_regime"):
            lines.append(f"- **Legal regime / geography:** {esc(m.get('legal_regime'))}")
        if m.get("who_uses_it"):
            lines.append(f"- **Who uses it:** {esc(m.get('who_uses_it'))}")
        if m.get("real_example"):
            ex = esc(m.get("real_example"))
            url = m.get("example_source_url")
            lines.append(f"- **Example:** {ex}" + (f"  \n  Source: {url}" if url else ""))
        if m.get("notes"):
            lines.append(f"- **Notes:** {esc(m.get('notes'))}")
        lines.append("")
w("docs/02_mechanism_catalog.md", "\n".join(lines))


# ---------------------------------------------------------------- 03 evidence
lines = []
lines.append("# Evidence Synthesis — Does Value-Sharing Tip the Odds?\n")
lines.append("Graded synthesis of the existing empirical evidence on whether worker value-sharing improves "
             "firm and worker outcomes. Each finding carries an honest evidence grade and a citation, "
             "produced by the Phase-0 research workflow (2026-06-17). **Posture: balanced.** Correlation is "
             "separated from causal identification; independent research is separated from advocacy.\n")

all_findings = []
for body in R["literature"]:
    for f in body.get("findings", []):
        f["_body"] = body.get("evidence_body", "")
        all_findings.append(f)

grade_counts = Counter((f.get("evidence_grade", "unspecified") or "unspecified").lower() for f in all_findings)
lines.append("\n## Evidence-grade ladder (how strong is the base?)\n")
lines.append("| Grade | # findings |\n|---|---|")
order = ["causal-identified", "quasi-experimental", "correlational", "advocacy-weak"]
shown = set()
for k in order:
    cnt = sum(v for g, v in grade_counts.items() if k in g)
    if cnt:
        lines.append(f"| {k} | {cnt} |")
        shown.add(k)
for g, v in grade_counts.items():
    if not any(k in g for k in shown):
        lines.append(f"| {esc(g)} | {v} |")
lines.append(f"\n_Total findings: {len(all_findings)}. Read the grade column before quoting any number to "
             "the professor — a correlational finding is not a causal one._\n")

for body in R["literature"]:
    lines.append(f"\n## {esc(body.get('evidence_body'))}\n")
    fs = body.get("findings", [])
    if fs:
        lines.append("| Finding | Outcome | Direction | Grade | Citation | Source |\n|---|---|---|---|---|---|")
        for f in fs:
            url = f.get("source_url", "")
            link = f"[link]({url})" if url else "—"
            lines.append("| {} | {} | {} | {} | {} | {} |".format(
                esc(f.get("claim")), esc(f.get("outcome")), esc(f.get("direction")),
                esc(f.get("evidence_grade")), esc(f.get("study_citation")), link))
        # caveats
        cavs = [f.get("caveat") for f in fs if f.get("caveat")]
        if cavs:
            lines.append("\n**Caveats on the above:**")
            for c in cavs[:8]:
                lines.append(f"- {esc(c)}")
    if body.get("skeptical_notes"):
        lines.append(f"\n**Skeptical read:** {esc(body.get('skeptical_notes'))}")
    lines.append("")
w("docs/03_evidence_synthesis.md", "\n".join(lines))


# ---------------------------------------------------------------- 04 providers
prov_groups = R["providers"]
lines = []
lines.append("# Data Strategy — Public-First Pilot, Licensed-Later Scale\n")
lines.append("Per the 2026-06-17 directive, the Phase-0 pilot uses **public / compliant sources only** — no "
             "ToS-violating scraping. This document also compiles the **provider × metric × cost matrix** so a "
             "licensed provider can be integrated in Phase 2, *after* Ethan reviews the first 20-vs-20.\n")
lines.append("\n## Metrics the study needs\n")
lines.append("- Employee **headcount** (current + historical) — for jobs and per-dollar metrics\n"
             "- **Capital raised / deployed** (whole-portfolio) — the per-dollar denominator\n"
             "- **Ownership / cap-table** split — for the distribution metric\n"
             "- **Exits / valuations**, **founding date**, **sector**, **geography** — matching + outcomes\n")

for grp in prov_groups:
    plist = grp.get("providers", [])
    free = all((("free" in (p.get("cost", "").lower())) or ("public" in (p.get("access_model", "").lower())) or ("free" in (p.get("access_model", "").lower()))) for p in plist) if plist else False
    title = "Free / public sources" if free else "Commercial data providers"
    lines.append(f"\n## {title}\n")
    lines.append("| Provider | Access | Metrics covered | Cost | Source |\n|---|---|---|---|---|")
    for p in plist:
        mc = ", ".join(p.get("metrics_covered", []))
        url = p.get("cost_source_url", "")
        link = f"[link]({url})" if url else "—"
        lines.append("| {} | {} | {} | {} | {} |".format(
            esc(p.get("provider")), esc(p.get("access_model")), esc(mc), esc(p.get("cost")), link))
        if p.get("coverage_notes"):
            lines.append(f"| | | _{esc(p.get('coverage_notes'))}_ | | |")
lines.append("\n## Recommendation\n")
lines.append("- **Phase 0–1 (now):** lean on the free/public stack (SEC EDGAR, DOL Form 5500 for ESOPs, NCEO, "
             "Companies House, company disclosures). It covers headcount, ESOP presence, founding, sector, and "
             "geography for many firms — but leaves private cap-table splits and private-company capital figures "
             "thin. Those gaps are the pilot's main finding (see `../analysis/pilot_first_cuts.md`).\n"
             "- **Phase 2 (after Ethan's go-ahead):** add ONE licensed provider that covers headcount history + "
             "funding + ownership in a single feed. Decide the provider against the cost column above and the "
             "budget Ethan sets (see `05_questions_for_ethan.md`, Q6).\n")
w("docs/04_data_strategy.md", "\n".join(lines))


# ---------------------------------------------------------------- pilot CSV + first cuts (RETIRED 2026-06-18)
# The company-level pilot was retired - it conflated companies with funds. The fund-level
# pilot is now built by build_fund_level.py. Stop here so re-running cannot resurrect the
# deleted company-level files (see analysis/2026-06-18_audit_and_rebuild.md).
import sys
print("build_phase0.py: company-level pilot retired 2026-06-18 - regenerated 02/03/04 only; "
      "pilot skipped (see build_fund_level.py).")
sys.exit(0)

pc = R["pilot"]["companies"]
verifs = {v.get("company", "").strip().lower(): v for v in R["pilot"]["verifications"]}
# dedupe companies by name
seenc = {}
for c in pc:
    k = c.get("company", "").strip().lower()
    if k and k not in seenc:
        seenc[k] = c
companies = list(seenc.values())

fields = ["company", "group", "sector", "country", "founded_year", "headcount", "headcount_source_url",
          "capital_model", "capital_source_url", "value_sharing", "value_sharing_quote",
          "value_sharing_source_url", "capital_raised_or_deployed", "capital_amount_source_url",
          "outcome_notes", "data_confidence", "verified_claims_hold", "verify_issues"]
csv_path = os.path.join(BASE, "data", "pilot_companies.csv")
os.makedirs(os.path.dirname(csv_path), exist_ok=True)
with open(csv_path, "w", encoding="utf-8", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
    wr.writeheader()
    for c in companies:
        v = verifs.get(c.get("company", "").strip().lower(), {})
        row = dict(c)
        row["verified_claims_hold"] = v.get("claims_hold", "")
        row["verify_issues"] = v.get("issues_found", "")
        wr.writerow(row)
print("wrote data/pilot_companies.csv", len(companies), "rows")

# ---- first cuts ----
def group(c):
    return c.get("group", "?")

pu = [c for c in companies if group(c) == "post-unicorn"]
vc = [c for c in companies if group(c) == "vc-backed"]


def has_sharing(c):
    s = (c.get("value_sharing") or "").lower()
    if not s or s in ("not public", "none", "n/a", "na"):
        return False
    neg = any(k in s for k in ["no broad", "none", "no employee ownership", "concentrated", "standard vc",
                               "no value sharing", "absent", "typical vc", "minimal"])
    return not neg


def hc(c):
    return num(c.get("headcount"))


def cap(c):
    return parse_money(c.get("capital_raised_or_deployed"))


def covered(items, fn):
    return sum(1 for c in items if fn(c) is not None)


lines = []
lines.append("# Pilot — First Cuts (Phase 0)\n")
lines.append(f"Deep, small, matched seed: **{len(pu)} post-unicorn** vs **{len(vc)} VC-backed** companies "
             "(matched by sector + country). Every record is source-cited and was adversarially verified "
             f"(all {len(companies)} retained). Data: `../data/pilot_companies.csv`.\n")
lines.append("> **Read this as a methodology demonstration, not a result.** A 31-firm purposive sample cannot "
             "establish causation; selection into the sample is deliberate, not random. The value here is "
             "(a) showing the fairness engine runs, and (b) mapping exactly which data are publicly available "
             "vs missing — the gap that justifies licensed-data integration in Phase 2.\n")

lines.append("\n## 1. Sample composition\n")
secs = Counter(c.get("sector", "?") for c in companies)
ctry = Counter(c.get("country", "?") for c in companies)
lines.append(f"- Sectors represented: {', '.join(f'{k} ({v})' for k,v in secs.most_common())}")
lines.append(f"- Countries represented: {', '.join(f'{k} ({v})' for k,v in ctry.most_common())}")

lines.append("\n## 2. Public-data coverage (the honest gap map)\n")
lines.append("| Field | Post-unicorn covered | VC-backed covered |\n|---|---|---|")
lines.append(f"| Headcount | {covered(pu,hc)}/{len(pu)} | {covered(vc,hc)}/{len(vc)} |")
lines.append(f"| Capital raised/deployed | {covered(pu,cap)}/{len(pu)} | {covered(vc,cap)}/{len(vc)} |")
both_pu = sum(1 for c in pu if hc(c) and cap(c))
both_vc = sum(1 for c in vc if hc(c) and cap(c))
lines.append(f"| Both (enables per-dollar) | {both_pu}/{len(pu)} | {both_vc}/{len(vc)} |")
lines.append("\n_Where capital figures are missing it is usually because the firm is privately held / "
             "employee-owned and does not disclose capital deployed — precisely the gap a licensed provider fills._\n")

lines.append("\n## 3. A1 signal — does the capital model coincide with value-sharing?\n")
lines.append("Caveat: this reflects how the sample was *constructed* (value-sharing exemplars vs VC-backed "
             "firms), so it is illustrative of the contrast, not a prevalence estimate.\n")
lines.append(f"- Post-unicorn firms with a documented broad value-sharing mechanism: **{sum(1 for c in pu if has_sharing(c))}/{len(pu)}**")
lines.append(f"- VC-backed firms with a documented broad value-sharing mechanism: **{sum(1 for c in vc if has_sharing(c))}/{len(vc)}**")

lines.append("\n## 4. Per-dollar first cut (illustrative only)\n")
rows = []
for c in companies:
    h, k = hc(c), cap(c)
    if h and k:
        jpm = h / (k / 1e6)
        rows.append((c.get("company"), group(c), int(h), k, round(jpm, 2)))
if rows:
    lines.append("Computed only where BOTH headcount and capital are public. **Heavy caveats apply** "
                 "(headcount today vs capital over time; whole-portfolio denominator not yet applied; no matching).\n")
    lines.append("| Company | Group | Headcount | Capital ($) | Jobs per $1M |\n|---|---|---|---|---|")
    for r0 in sorted(rows, key=lambda x: -x[4]):
        lines.append(f"| {esc(r0[0])} | {r0[1]} | {r0[2]:,} | {r0[3]:,.0f} | {r0[4]} |")
    lines.append("\n- **No group median or comparison is reported.** The capital figures are not comparable "
                 "across groups: for VC-backed firms they are *funding raised*, for post-unicorn buyout deals "
                 "they are *acquisition / enterprise value*, and for employee-owned firms they are often absent. "
                 "Comparing jobs-per-$1M across these denominators would be apples-to-oranges.")
    lines.append("- **Do not quote these as findings.** The table proves the metric computes on real, sourced "
                 "firms; it is not a result. A like-for-like denominator (capital deployed across the whole fund "
                 "portfolio) requires the licensed data in Phase 2.")
else:
    lines.append("_No company had both headcount and capital public in machine-parseable form — itself the "
                 "key finding: the per-dollar metric needs licensed capital/ownership data to run at scale._")

lines.append("\n## 5. What the pilot establishes\n")
lines.append("- The fairness engine (`../docs/01_comparison_methodology.md`) is implementable on real firms.\n"
             "- Public data reliably yields **headcount, value-sharing presence, sector, country, founding**; "
             "it is thin on **capital deployed** and **ownership splits** for private firms.\n"
             "- Therefore Phase 2 needs one licensed provider (see `../docs/04_data_strategy.md`) to compute "
             "whole-portfolio per-dollar and distribution metrics credibly.\n")
lines.append(f"\n_Generated {TODAY} from the verified Phase-0 research workflow._\n")
w("analysis/pilot_first_cuts.md", "\n".join(lines))

print("DONE")
