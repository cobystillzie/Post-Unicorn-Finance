"""
Phase 4c - Targeted reclassification of LISTED_HOLDCO and INSTITUTIONAL_ENDOWMENT
sub-clusters using entity-by-entity adversarial determinations.

LISTED_HOLDCO decisions:
  -> Portfolio Capital: LVO Industries, HAL Investments, Industrivarden, Sofina,
     Gimv, Bergman & Beving, Luxempart
  -> SMV: Burford Capital (litigation finance), Metrics Credit Partners (private credit)
  -> ECOSYSTEM: Simplicity NZ (nonprofit retirement fund manager)
  -> Stay Patient Capital: Generation Investment Management (impact sustainable PE)
  (Asseco Group, Diploma plc already moved in Phase 4)

INSTITUTIONAL_ENDOWMENT decisions:
  -> Sovereign Capital: State of Wisconsin Investment Board (SWIB)
     (CDPQ, BCI, OPTrust already reclassified in Phase 4 flags)
  -> ECOSYSTEM (endowment LPs, not direct company allocators):
     Surdna Foundation, McKnight Foundation, DUMAC, MITIMCo,
     Stanford Management Company, UTIMCO, Cornell, Notre Dame,
     PRINCO, Yale, Northwestern, Vanderbilt, Washington
  -> SMV: Crayhill Capital Management
  -> LMV: PSV (PreSeed Ventures)
  -> Stay Patient Capital: Capricorn (CLAUDE.md 2026-05-28),
     Cambridge Innovation Capital, Oxford Science Enterprises,
     Northern Gritstone, Sango Capital

Run from project root:
    python scripts/phase4c_listed_holdco_endowment_reclass.py
"""

import csv, re
from pathlib import Path

EVIDENCE = Path("data/evidence")
ENTITIES = EVIDENCE / "industry_entities.csv"
ECOSYSTEM = EVIDENCE / "ecosystem_entities.csv"
LOG      = EVIDENCE / "manual_changes_2026-06-01.log"
TODAY    = "2026-06-01"

def norm(n):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (n or "").lower())).strip()

def read_csv(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def write_csv(path, rows, fieldnames=None):
    if not rows:
        return
    fns = fieldnames or list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

def append_log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


RECLASS_MAP = {
    # LISTED_HOLDCO -> Portfolio Capital
    "lvo industries":               "Portfolio Capital",
    "hal investments":              "Portfolio Capital",
    "industrivarden":               "Portfolio Capital",
    "industri rden":                "Portfolio Capital",
    "sofina":                       "Portfolio Capital",
    "gimv":                         "Portfolio Capital",
    "bergman beving":               "Portfolio Capital",
    "luxempart":                    "Portfolio Capital",
    # LISTED_HOLDCO -> SMV
    "burford capital":              "SMV",
    "metrics credit partners":      "SMV",
    # LISTED_HOLDCO -> ECOSYSTEM
    "simplicity nz":                "ECOSYSTEM",
    # INSTITUTIONAL_ENDOWMENT -> Sovereign Capital
    "state of wisconsin investment board swib": "Sovereign Capital",
    # INSTITUTIONAL_ENDOWMENT -> ECOSYSTEM (endowment LPs)
    "surdna foundation":            "ECOSYSTEM",
    "mcknight foundation":          "ECOSYSTEM",
    "duke university management company dumac": "ECOSYSTEM",
    "mit investment management company mitimco": "ECOSYSTEM",
    "stanford management company":  "ECOSYSTEM",
    "the university of texas texas a m investment management company utimco": "ECOSYSTEM",
    "utimco":                       "ECOSYSTEM",
    "cornell university office of university investments": "ECOSYSTEM",
    "notre dame investment office":  "ECOSYSTEM",
    "princeton university investment company princo": "ECOSYSTEM",
    "yale investments office":      "ECOSYSTEM",
    "northwestern university investment office": "ECOSYSTEM",
    "vanderbilt university office of investments": "ECOSYSTEM",
    "washington university investment management company": "ECOSYSTEM",
    # INSTITUTIONAL_ENDOWMENT -> SMV
    "crayhill capital management":  "SMV",
    # INSTITUTIONAL_ENDOWMENT -> LMV
    "psv":                          "LMV",
}


if __name__ == "__main__":
    rows = read_csv(ENTITIES)
    fieldnames = list(rows[0].keys()) if rows else []

    changed = []
    eco_moved = []
    out_rows = []

    for row in rows:
        nn = norm(row.get("name", "") or row.get("legal_name", ""))
        cur = row.get("primary_asset_class", "")
        target = RECLASS_MAP.get(nn)

        if target and cur == "Patient Capital":
            if target == "ECOSYSTEM":
                eco_moved.append(row)
                continue  # remove from main entities
            else:
                row = dict(row)
                row["primary_asset_class"] = target
                changed.append({"name": row.get("name",""), "from": cur, "to": target})

        out_rows.append(row)

    write_csv(ENTITIES, out_rows, fieldnames)

    # Extend ecosystem_entities.csv
    existing_eco = read_csv(ECOSYSTEM)
    existing_names = {norm(r.get("name","") or r.get("legal_name","")) for r in existing_eco}
    new_eco = [r for r in eco_moved if norm(r.get("name","")) not in existing_names]
    if new_eco:
        all_eco = existing_eco + new_eco
        write_csv(ECOSYSTEM, all_eco, list(all_eco[0].keys()))

    for c in changed:
        msg = f"[{TODAY}] RECLASS | {c['name']} | {c['from']} -> {c['to']} | LISTED_HOLDCO/INSTITUTIONAL_ENDOWMENT adversarial review 4c"
        print(msg)
        append_log(msg)
    for r in eco_moved:
        msg = f"[{TODAY}] ECOSYSTEM | {r.get('name','')} | Patient Capital -> ECOSYSTEM | endowment LP / grantmaker 4c"
        print(msg)
        append_log(msg)

    print(f"\nReclassified:          {len(changed)}")
    print(f"Moved to ecosystem:    {len(eco_moved)}")
    print(f"New ecosystem entries: {len(new_eco)}")

    counts = {}
    for r in read_csv(ENTITIES):
        c = r.get("primary_asset_class","")
        counts[c] = counts.get(c, 0) + 1
    total = sum(counts.values())
    print(f"\nFinal atlas: {total} entities")
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {k:<32} {v:>4}")
    print("\nDone.")
