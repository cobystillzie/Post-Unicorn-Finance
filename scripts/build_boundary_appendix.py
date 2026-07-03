"""
Build the boundary/taxonomy appendix data for the Atlas packet.

Produces data/runtime/boundary_appendix_2026-06-01.json, consumed by
export_shareable_atlas.py to render four boss-facing sections:
  1. taxonomy diagram  (7 allocator classes + 2 non-allocator layers:
                         core mechanism, instrument, one-line test, live count)
  2. mechanism axes    (the 5 axes that separate the classes — similarities/differences)
  3. boundary resolutions ("where the classes bleed") — grouped BY OVERLAP PAIR,
                         every contested company as a row with: what it looks like,
                         why, what decided it, its final class, and a VERBATIM quote.
  4. two non-allocator layers (Ecosystem roster + UVC-adjacent excluded roster).

All taxonomy/axes/overlap prose is authored from docs/research/
emergent_post_unicorn_taxonomy_2026-06-01.md (Tier-3). Every per-company quote is
copied verbatim from data/runtime/phase3_profiles (never generated).

Run from project root:
    python scripts/build_boundary_appendix.py
"""

from __future__ import annotations

import csv
import json
import os
import re
from collections import Counter
from pathlib import Path

EVID = Path("data/evidence")
RUNTIME = Path("data/runtime")
ENT = EVID / "industry_entities.csv"
ECO = EVID / "ecosystem_entities.csv"
UVC = EVID / "removed_uvc_2026-06-01.csv"
PREVIEW = RUNTIME / "aplus_reclass_preview_2026-06-01.json"
PROFDIR = RUNTIME / "phase3_profiles"
OUT = RUNTIME / "boundary_appendix_2026-06-01.json"
TODAY = "2026-06-01"

# --- Authored taxonomy (from Tier-3 §2.1 table + §2.3 boundary tests) -----------
TAXONOMY = [
    {"klass": "Patient Capital", "layer": "allocator",
     "mechanism": "Structural commitment over exit",
     "instrument": "Permanent equity, steward-ownership, mission/CDFI mandate, capped returns, shared earnings",
     "test": "Is exit structurally constrained — purpose-trust, capped returns, ESOP-only exit, CDFI/DFI mandate, or an explicit no-sale covenant — not merely 'long-term' talk?"},
    {"klass": "Portfolio Capital", "layer": "allocator",
     "mechanism": "Buy-and-compound existing companies",
     "instrument": "Control equity, holdco roll-up, programmatic / serial acquisition",
     "test": "Does it acquire existing operating companies (buy-not-build) and compound through programmatic acquisitions or holdco operation, without unicorn-style exit timelines?"},
    {"klass": "SMV", "layer": "allocator",
     "mechanism": "Non-dilutive / structured credit",
     "instrument": "Revenue-based financing, venture debt, mezzanine, ABL, factoring, secondaries, shared-earnings",
     "test": "Is the primary instrument non-equity (RBF, debt, mezz, ABL, factoring, secondaries) or an explicit anti-VC equity mechanic targeting bootstrapped founders?"},
    {"klass": "LMV", "layer": "allocator",
     "mechanism": "Solo-GP / micro / indie equity",
     "instrument": "Pre-seed/seed equity checks ($10K-$5M), sub-$150M funds, accelerator+fund / fellowship",
     "test": "GP count <=3, no corporate parent, fund <$150M, AND documented equity-deployment history (not just a community or program)?"},
    {"klass": "Sovereign Capital", "layer": "allocator",
     "mechanism": "Public-charter mandate",
     "instrument": "Sovereign-wealth, DFI/MDB, public-pension, tribal/sub-national capital",
     "test": "Does the investment authority flow from a PUBLIC LEGAL CHARTER (sovereign decree, act of legislature, multilateral treaty, tribal constitution) with a public/political mandate?"},
    {"klass": "Search/ETA", "layer": "allocator",
     "mechanism": "Capitalize a single searcher / operator",
     "instrument": "Search capital, acquisition debt, independent-sponsor equity",
     "test": "Does it capitalize an individual searcher or owner-operator for a single (or small number of) acquisition WITHOUT building a shared operating platform?"},
    {"klass": "Venture Studio", "layer": "allocator",
     "mechanism": "Build-not-buy: co-found companies in-house",
     "instrument": "Studio equity from day zero, shared talent/operating platform",
     "test": "Does it ORIGINATE companies internally (in-house IP, EIR co-founders, team built by the studio) rather than acquiring or backing external founders?"},
    {"klass": "Ecosystem / Infrastructure", "layer": "non-allocator (layer, not an asset class)",
     "mechanism": "Principal-vs-agent: enables allocation, does not allocate",
     "instrument": "Advisory (RIA/OCIO), brokerage, marketplace, network, grants, fund administration",
     "test": "Does it deploy its OWN or LP capital - or does it manage CLIENT capital, broker transactions, run a marketplace, or convene a community? If agent -> this layer."},
    {"klass": "UVC-adjacent (excluded baseline)", "layer": "non-allocator (exclusion baseline)",
     "mechanism": "Classic unicorn VC / corporate CVC / standard buyout PE",
     "instrument": "Standard LP-bounded fund, target IRR, defined exit cycle",
     "test": "Does it raise standard LP-bounded funds with a target IRR, defined exit cycles, and unicorn-scale optionality? If yes -> excluded baseline, regardless of founder-friendly language."},
]

# --- Authored mechanism axes (from Tier-3 §2.4) ---------------------------------
AXES = [
    {"axis": "Acquire vs Build vs Fund-external",
     "splits": "Portfolio Capital (acquires existing) | Venture Studio (builds in-house) | LMV / UVC (funds external founders)",
     "note": "The line venture studios were hiding behind inside Portfolio Capital - a fundamentally different mechanism."},
    {"axis": "Equity vs Non-dilutive credit",
     "splits": "SMV (RBF, debt, mezz, ABL, factoring, secondaries) | every other class (equity)",
     "note": "Specialty credit slid into Patient and Portfolio on long-hold / balance-sheet language; the instrument test pulls it back to SMV."},
    {"axis": "Principal vs Agent",
     "splits": "All 7 allocator classes (deploy own/LP capital) | Ecosystem layer (advise, broker, convene)",
     "note": "RIAs, OCIOs, brokers, marketplaces, networks and grantmakers wear allocator vocabulary but deploy none of their own capital."},
    {"axis": "Private vs Public-charter mandate",
     "splits": "Sovereign Capital (public legal charter) | every other class (private LP / balance-sheet)",
     "note": "Public pensions and state pools differ from family balance-sheets by the SOURCE of the mandate, not the hold period."},
    {"axis": "Exit-constrained vs Exit-seeking",
     "splits": "Patient Capital (structural no-exit) | most classes (harvest on a horizon) | UVC (unicorn exit - the baseline we exclude)",
     "note": "The original taxonomy conflated 'long hold' with 'patient'; the real test is whether exit is structurally off the table."},
]

# --- Authored overlap-pair descriptions (from Tier-3 §3 + cluster boundary_issues) ---
PAIR_INFO = {
    ("Patient Capital", "UVC"): {
        "looks_like": "VC and PE funds wrapped in mission, impact, 'patient', or founder-friendly language.",
        "why": "The vocabulary of capital - 'long-term', 'partner', 'mission-driven' - is shared, so a keyword gate cannot tell a steward from a standard fund.",
        "what_decides": "If it raises a standard LP fund with a target IRR and a defined exit cycle, it is classic unicorn-style VC/PE and is excluded as UVC - regardless of the rhetoric."},
    ("Patient Capital", "LMV"): {
        "looks_like": "Small regional or seed funds that describe themselves as long-term, founder-aligned partners.",
        "why": "They carry long-hold rhetoric but possess no structural patient-capital feature.",
        "what_decides": "<=3 GPs, no corporate parent, sub-$150M fund, conventional economics -> an indie micro-fund (LMV), not structurally Patient Capital."},
    ("Patient Capital", "Portfolio Capital"): {
        "looks_like": "Permanent-equity acquirers, 'forever home' holdcos, and healthcare / home-services roll-ups using partnership language.",
        "why": "Both speak 'permanent capital', so the serial-acquisition mechanism hides behind steward-flavored rhetoric.",
        "what_decides": "Buy-and-compound acquisition of existing companies -> Portfolio Capital; Patient Capital only with an explicit no-exit / single-business steward covenant."},
    ("Patient Capital", "Sovereign Capital"): {
        "looks_like": "Large public pension funds and state-owned perpetual pools sitting in the patient slot.",
        "why": "Both are long-duration, no-redemption pools of capital.",
        "what_decides": "If the investment mandate flows from a public legal charter (statute, sovereign decree, treaty) -> Sovereign Capital."},
    ("Patient Capital", "SMV"): {
        "looks_like": "Specialty private credit, mezzanine, and revenue-based providers parked in the patient slot.",
        "why": "Balance-sheet and long-hold language obscures the underlying instrument.",
        "what_decides": "If the primary instrument is non-dilutive (private credit, RBF, factoring, mezzanine) -> SMV."},
    ("Patient Capital", "Search/ETA"): {
        "looks_like": "Operator-acquirers and search-fund backers labeled as patient capital.",
        "why": "Single-owner, long-hold ownership language reads as 'patient'.",
        "what_decides": "If it capitalizes one operator buying one business with no shared platform -> Search/ETA."},
    ("Patient Capital", "ECOSYSTEM"): {
        "looks_like": "RIAs, OCIOs, foundations, and grantmakers using allocator vocabulary.",
        "why": "They sit adjacent to allocators and speak the same language of capital.",
        "what_decides": "Principal-vs-agent: if it manages client money, makes grants, or convenes - rather than deploying its own/LP capital - it belongs in the Ecosystem layer, not an asset class."},
    ("Portfolio Capital", "UVC"): {
        "looks_like": "A standard lower-middle-market buyout fund using buy-and-build language.",
        "why": "Buy-and-build resembles compounding, but the fund structure is classic PE.",
        "what_decides": "Standard LP fund + target IRR + defined exit cycle -> excluded as UVC, not Portfolio Capital."},
    ("Portfolio Capital", "Patient Capital"): {
        "looks_like": "A permanent-equity software acquirer that explicitly forecloses exit.",
        "why": "It looks like a VMS roll-up holdco.",
        "what_decides": "An explicit no-sale / single-business steward covenant pulls it from Portfolio into genuine Patient Capital."},
    ("SMV", "Patient Capital"): {
        "looks_like": "A long-hold, mission-anchored capital provider mis-bucketed as middle-market.",
        "why": "Its non-dilutive framing read as 'strategic middle'.",
        "what_decides": "A structural no-exit mandate moves it to Patient Capital."},
    ("Search/ETA", "Patient Capital"): {
        "looks_like": "An owner-operator vehicle described in permanent-home language.",
        "why": "Single-owner stewardship reads as patient.",
        "what_decides": "An explicit permanent / no-exit hold mandate -> Patient Capital."},
    ("Search/ETA", "Portfolio Capital"): {
        "looks_like": "An operator-led SMB platform that runs a shared back-office across acquisitions.",
        "why": "It presents like a single-searcher ETA story.",
        "what_decides": "A shared operating platform across multiple acquisitions -> Portfolio Capital, not single-target Search/ETA."},
    ("LMV", "SMV"): {
        "looks_like": "An indie-branded fund whose actual instrument is non-dilutive.",
        "why": "The indie-fund aesthetic masks the instrument.",
        "what_decides": "A non-dilutive instrument (RBF / shared-earnings) -> SMV regardless of indie branding."},
    ("LMV", "ECOSYSTEM"): {
        "looks_like": "A fellowship, community, or accelerator with indie-fund styling.",
        "why": "It uses fund vocabulary without documented capital deployment.",
        "what_decides": "No documented equity-deployment history -> Ecosystem layer, not LMV."},
    ("Search/ETA", "ECOSYSTEM"): {
        "looks_like": "A searcher membership / community or marketplace.",
        "why": "It serves searchers and speaks ETA language.",
        "what_decides": "It convenes or brokers rather than deploying capital -> Ecosystem layer."},
}
FLAG_INFO = {
    "looks_like": "A thin or ambiguous self-description that gave no clear structural signal.",
    "why": "The page did not provide enough mechanism evidence to move it confidently.",
    "what_decides": "Held in its current class and flagged for human review - unverifiable is not the same as misclassified.",
}


def norm(n: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (n or "").lower())).strip()


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def load_profiles() -> dict[str, dict]:
    m: dict[str, dict] = {}
    for f in sorted(os.listdir(PROFDIR)):
        if f.endswith(".json"):
            for p in json.load(open(PROFDIR / f, encoding="utf-8")).get("profiles", []):
                if isinstance(p, dict) and p.get("name"):
                    m.setdefault(norm(p["name"]), p)
    return m


def best_quote(prof: dict | None) -> str:
    """Return one VERBATIM self-description string from the profile, or '' if none."""
    if not prof:
        return ""
    qs = prof.get("verbatim_quotes")
    if isinstance(qs, list):
        for q in qs:
            if str(q).strip():
                return str(q).strip()
    elif str(qs or "").strip():
        return str(qs).strip()
    return str(prof.get("self_named_role") or "").strip()


def pair_label(current: str, final: str, action: str) -> str:
    if action == "flag":
        return f"{current} - kept, flagged borderline"
    if action == "remove_uvc":
        return f"{current} <-> UVC (excluded)"
    if action == "demote_ecosystem":
        return f"{current} <-> Ecosystem (non-allocator)"
    return f"{current} <-> {final}"


def pair_info(current: str, final: str, action: str) -> dict:
    if action == "flag":
        return FLAG_INFO
    key = (current, final if action == "reclass" else ("UVC" if action == "remove_uvc" else "ECOSYSTEM"))
    return PAIR_INFO.get(key, FLAG_INFO)


def main() -> int:
    profs = load_profiles()
    preview = json.load(open(PREVIEW, encoding="utf-8"))
    contested = [p for p in preview if p["action"] in ("reclass", "remove_uvc", "demote_ecosystem", "flag")]

    ent_counts = Counter(r["primary_asset_class"] for r in read_csv(ENT))
    eco_rows = read_csv(ECO)
    uvc_rows = read_csv(UVC)
    layer_counts = {"Ecosystem / Infrastructure": len(eco_rows),
                    "UVC-adjacent (excluded baseline)": len(uvc_rows)}
    taxonomy = [{**t, "count": ent_counts.get(t["klass"], layer_counts.get(t["klass"], 0))} for t in TAXONOMY]

    groups: dict[str, dict] = {}
    for p in contested:
        cur, fin, act = p["current_class"], p["target_class"], p["action"]
        label = pair_label(cur, fin, act)
        if label not in groups:
            groups[label] = {"pair": label, **pair_info(cur, fin, act), "companies": []}
        prof = profs.get(norm(p["name"]))
        final_class = ("UVC (excluded)" if act == "remove_uvc"
                       else "Ecosystem (non-allocator)" if act == "demote_ecosystem"
                       else fin)
        groups[label]["companies"].append({
            "name": p["name"],
            "final_class": final_class,
            "verdict": (p.get("reason") or "").strip(),
            "quote": best_quote(prof),
        })

    overlap_pairs = sorted(groups.values(), key=lambda g: -len(g["companies"]))
    for g in overlap_pairs:
        g["companies"].sort(key=lambda c: c["name"].lower())
        g["count"] = len(g["companies"])

    def layer_entries(rows: list[dict], reason_field_order: list[str]) -> list[dict]:
        out = []
        for r in rows:
            prof = profs.get(norm(r.get("name", "")))
            reason = ""
            for fld in reason_field_order:
                if (r.get(fld) or "").strip():
                    reason = r[fld].strip()
                    break
            out.append({
                "name": r.get("name", ""),
                "former_class": r.get("primary_asset_class", ""),
                "reason": reason[:300],
                "quote": best_quote(prof),
                "website": r.get("website", ""),
            })
        return sorted(out, key=lambda e: e["name"].lower())

    layers = {
        "ecosystem": layer_entries(eco_rows, ["ecosystem_role", "non_unicorn_thesis", "notes"]),
        "uvc": layer_entries(uvc_rows, ["notes", "non_unicorn_thesis"]),
    }

    appendix = {
        "generated_at": TODAY,
        "taxonomy": taxonomy,
        "axes": AXES,
        "overlap_pairs": overlap_pairs,
        "layers": layers,
        "summary": {
            "contested_total": len(contested),
            "reclassified": sum(1 for p in contested if p["action"] == "reclass"),
            "excluded_uvc": sum(1 for p in contested if p["action"] == "remove_uvc"),
            "moved_ecosystem": sum(1 for p in contested if p["action"] == "demote_ecosystem"),
            "kept_flagged": sum(1 for p in contested if p["action"] == "flag"),
            "ecosystem_layer_total": len(eco_rows),
            "uvc_layer_total": len(uvc_rows),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(appendix, open(OUT, "w", encoding="utf-8"), indent=1, ensure_ascii=False)

    print(f"Wrote {OUT}")
    print(f"  taxonomy rows: {len(taxonomy)} | axes: {len(AXES)} | overlap pairs: {len(overlap_pairs)}")
    print(f"  contested companies: {len(contested)} | ecosystem layer: {len(eco_rows)} | uvc layer: {len(uvc_rows)}")
    missing_q = sum(1 for g in overlap_pairs for c in g["companies"] if not c["quote"])
    print(f"  contested companies missing a verbatim quote: {missing_q}")
    for g in overlap_pairs:
        print(f"    {g['count']:>3}  {g['pair']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
