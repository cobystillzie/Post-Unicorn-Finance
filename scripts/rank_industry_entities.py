"""Rank industry atlas entities for coverage and verification priority."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from atlas_scoring import entity_score

ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "evidence" / "industry_entities.csv"
EXPORT_ALL = ROOT / "data" / "exports" / "ranked_industry_entities.csv"
EXPORT_BY_CLASS_DIR = ROOT / "data" / "exports" / "asset_class_rankings"


def read_rows() -> list[dict[str, str]]:
    with INPUT_PATH.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = ["atlas_priority_score"] + [
        name for name in rows[0].keys() if name != "atlas_priority_score"
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Rows for the main ranked export; 0 means all entities")
    args = parser.parse_args()

    rows = read_rows()
    for row in rows:
        row["atlas_priority_score"] = str(entity_score(row))
    rows.sort(key=lambda item: int(item["atlas_priority_score"]), reverse=True)

    limited_rows = rows[: args.limit] if args.limit and args.limit > 0 else rows
    write_csv(EXPORT_ALL, limited_rows)
    write_csv(ROOT / "data" / "exports" / "ranked_industry_entities_top150.csv", rows[:150])

    EXPORT_BY_CLASS_DIR.mkdir(parents=True, exist_ok=True)
    for stale_csv in EXPORT_BY_CLASS_DIR.glob("*.csv"):
        stale_csv.unlink()
    for asset_class in sorted({row["primary_asset_class"] for row in rows}):
        class_rows = [row for row in rows if row["primary_asset_class"] == asset_class]
        safe_name = asset_class.lower().replace("/", "-").replace(" ", "_")
        write_csv(EXPORT_BY_CLASS_DIR / f"{safe_name}.csv", class_rows)

    print(f"Wrote {len(limited_rows)} ranked entities to {EXPORT_ALL}")
    print("Wrote top 150 triage export to data/exports/ranked_industry_entities_top150.csv")
    print("Top 12:")
    for row in rows[:12]:
        print(
            f"{row['atlas_priority_score']:>3}  "
            f"{row['name']}  "
            f"{row['primary_asset_class']}  "
            f"{row['ecosystem_role']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
