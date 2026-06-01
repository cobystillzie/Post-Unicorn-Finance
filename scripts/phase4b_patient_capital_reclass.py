"""
Phase 4b — Targeted Patient Capital reclassification.

Moves 4 unambiguous sub-clusters out of Patient Capital:
  PERM_EQUITY_SOFTWARE  (15) -> Portfolio Capital
  HEALTHCARE_PRACTICE_ROLLUP (10) -> Portfolio Capital
  HOME_SERVICES_ROLLUP   (7) -> Portfolio Capital
  PERM_EQUITY_SMB        (4) -> Portfolio Capital

Skipped (flag-only):
  LISTED_HOLDCO (13) - Generation Investment Management is uncertain
  INSTITUTIONAL_ENDOWMENT (24) - Foundations (grantmakers) need ECOSYSTEM
    treatment; Capricorn stays Patient Capital per CLAUDE.md correction
    2026-05-28; public-sector pensions only partially sovereign.

Run from project root:
    python scripts/phase4b_patient_capital_reclass.py
"""

import csv, json, re
from pathlib import Path

EVIDENCE  = Path("data/evidence")
CLUSTER   = Path("data/runtime/phase3_cluster_findings/cluster_Patient_Capital.json")
ENTITIES  = EVIDENCE / "industry_entities.csv"
LOG       = EVIDENCE / "manual_changes_2026-06-01.log"
TODAY     = "2026-06-01"

PORTFOLIO_SUBS = {
    "PERM_EQUITY_SOFTWARE",
    "HEALTHCARE_PRACTICE_ROLLUP",
    "HOME_SERVICES_ROLLUP",
    "PERM_EQUITY_SMB",
}

PROTECTED = {
    "capricorn investment group",
}

def norm(n):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (n or "").lower())).strip()


def build_reclass_set():
    with open(CLUSTER, encoding="utf-8") as f:
        data = json.load(f)
    names = set()
    for sc in data.get("sub_clusters", []):
        sid = sc.get("sub_cluster_id", "")
        if sid not in PORTFOLIO_SUBS:
            continue
        for m in sc.get("members", []):
            name = m.get("name", m) if isinstance(m, dict) else m
            nn = norm(str(name))
            if nn and nn not in PROTECTED:
                names.add(nn)
    return names


def apply_reclass(reclass_names):
    with open(ENTITIES, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    fieldnames = list(rows[0].keys())

    changed = []
    out_rows = []
    for row in rows:
        nn = norm(row.get("name", "") or row.get("legal_name", ""))
        cur = row.get("primary_asset_class", "")
        if nn in reclass_names and cur == "Patient Capital":
            row = dict(row)
            row["primary_asset_class"] = "Portfolio Capital"
            changed.append({"name": row.get("name", ""), "from": cur, "to": "Portfolio Capital"})
        out_rows.append(row)

    with open(ENTITIES, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)

    return changed


def class_distribution():
    counts = {}
    with open(ENTITIES, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            c = r.get("primary_asset_class", "")
            counts[c] = counts.get(c, 0) + 1
    return counts


if __name__ == "__main__":
    reclass_names = build_reclass_set()
    print(f"Reclass target set: {len(reclass_names)} entities")
    for n in sorted(reclass_names):
        print(f"  {n}")

    changed = apply_reclass(reclass_names)
    print(f"\nApplied: {len(changed)} reclassifications")
    for c in changed:
        msg = (f"[{TODAY}] RECLASS | {c['name']} | {c['from']} -> {c['to']} "
               "| Patient Capital sub-cluster (PERM_EQUITY_SOFTWARE/ROLLUP/SMB)")
        print(f"  {msg}")
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

    print("\nClass distribution after 4b:")
    dist = class_distribution()
    total = sum(dist.values())
    print(f"  Total: {total}")
    for k, v in sorted(dist.items(), key=lambda x: -x[1]):
        print(f"  {k:<32} {v:>4}")

    print("\nFLAGGED for manual review (not auto-reclassified):")
    print("  LISTED_HOLDCO (13) - verify Generation Investment Management")
    print("  INSTITUTIONAL_ENDOWMENT (24) - exclude Capricorn (stays Patient Capital),")
    print("    foundations -> ECOSYSTEM, public-sector pensions -> Sovereign Capital")
    print("\nDone.")
