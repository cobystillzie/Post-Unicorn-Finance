"""Rank SMV and adjacent candidates for review.

The score is not an investment recommendation. It is a research-priority score
for deciding which sourced candidates deserve human verification first.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "evidence" / "company_events.csv"
EXPORT_PATH = ROOT / "data" / "exports" / "ranked_smv_candidates.csv"


STATUS_WEIGHT = {
    "verified_fact": 18,
    "candidate_evidence": 9,
    "inference": 2,
    "user_thesis": 0,
    "needs_verification": -8,
}

SOURCE_WEIGHT = {
    "primary": 14,
    "credible_press": 12,
    "research": 9,
    "database_seed": 2,
    "discourse": 1,
    "social": -2,
    "unknown": -5,
}

BUCKET_WEIGHT = {
    "SMV": 22,
    "Patient Capital": 12,
    "LMV": 10,
    "Portfolio Capital": 8,
    "Search/ETA": 8,
    "UVC": 2,
    "Unknown Candidate": 0,
}

PATHWAY_WEIGHT = {
    "strategic_acquisition": 15,
    "bootstrapped": 13,
    "profitable_independent": 12,
    "delayed_vc": 8,
    "patient_capital": 8,
    "portfolio_studio": 5,
    "revenue_financed": 5,
    "lmv": 5,
    "search_eta": 4,
    "sovereign_backed": 4,
    "unknown_candidate": -4,
}


def read_rows() -> list[dict[str, str]]:
    with INPUT_PATH.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_pathways(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def outcome_bonus(value: str) -> int:
    normalized = value.strip().lower()
    if not normalized or normalized in {"not disclosed", "none"}:
        return 0
    if "arr" in normalized:
        return 6
    if "b" in normalized:
        return 6
    if "m" in normalized:
        return 10
    return 2


def rank_score(row: dict[str, str]) -> int:
    try:
        confidence = int(row.get("confidence_score", "0"))
    except ValueError:
        confidence = 0

    score = confidence
    score += STATUS_WEIGHT.get(row.get("evidence_status", ""), 0)
    score += SOURCE_WEIGHT.get(row.get("source_quality", ""), 0)
    score += BUCKET_WEIGHT.get(row.get("asset_bucket", ""), 0)
    score += outcome_bonus(row.get("outcome_value", ""))

    for pathway in parse_pathways(row.get("pathway", "")):
        score += PATHWAY_WEIGHT.get(pathway, 0)

    if "needs separate" in row.get("notes", "").lower():
        score -= 5
    if "boundary case" in row.get("why_prioritized", "").lower():
        score -= 4
    return score


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--asset-bucket", default="")
    args = parser.parse_args()

    rows = read_rows()
    for row in rows:
        row["research_priority_score"] = str(rank_score(row))

    if args.asset_bucket:
        rows = [row for row in rows if row.get("asset_bucket") == args.asset_bucket]

    rows.sort(key=lambda item: int(item["research_priority_score"]), reverse=True)
    rows = rows[: args.limit]

    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["research_priority_score"] + [
        name for name in rows[0].keys() if name != "research_priority_score"
    ]
    with EXPORT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} ranked candidates to {EXPORT_PATH}")
    for row in rows[:10]:
        print(
            f"{row['research_priority_score']:>3}  "
            f"{row['company_name']}  "
            f"{row['asset_bucket']}  "
            f"{row['outcome_value']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
