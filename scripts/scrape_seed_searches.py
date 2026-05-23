"""Generate the next manual/agentic search queue from scrape targets.

This script is deliberately conservative. It does not scrape search engines or
websites directly yet because the schema should be locked before automation.
It turns industry-atlas scrape targets into reproducible query URLs for a human
or browser/research agent to work through.
"""

from __future__ import annotations

import csv
from pathlib import Path
from urllib.parse import quote_plus


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "evidence" / "scrape_targets.csv"
INTAKE_PATH = ROOT / "data" / "evidence" / "entity_intake_queue.csv"
OUTPUT_PATH = ROOT / "data" / "exports" / "search_queue.csv"


def main() -> int:
    with INPUT_PATH.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if INTAKE_PATH.exists():
        with INTAKE_PATH.open("r", encoding="utf-8", newline="") as handle:
            intake_rows = list(csv.DictReader(handle))
    else:
        intake_rows = []

    output_rows = []
    for index, row in enumerate(rows, start=1):
        query = row["query"]
        output_rows.append(
            {
                "queue_id": f"atlas-search-{index:03d}",
                **row,
                "google_url": f"https://www.google.com/search?q={quote_plus(query)}",
                "bing_url": f"https://www.bing.com/search?q={quote_plus(query)}",
                "intake_table": "industry_entities.csv + entity_claims.csv",
                "default_evidence_status": "candidate_evidence",
                "queue_notes": "Use results to create source-backed industry entity claims. Do not add unsourced company rows.",
            }
        )
    for index, row in enumerate(intake_rows, start=len(output_rows) + 1):
        query = f"{row['name']} {row['target_entity_type']} {row['target_asset_class']}"
        output_rows.append(
            {
                "queue_id": f"entity-intake-{index:03d}",
                "lane": "Entity Intake",
                "target_asset_class": row["target_asset_class"],
                "source_family": "public_web",
                "query": query,
                "seed_entities_or_sources": row["source_urls"],
                "source_tier": row["source_tier"],
                "priority": row["priority"],
                "expected_fields": "name;website;claim_candidate;asset_class_candidate;source_text",
                "notes": row["notes"],
                "google_url": f"https://www.google.com/search?q={quote_plus(query)}",
                "bing_url": f"https://www.bing.com/search?q={quote_plus(query)}",
                "intake_table": "entity_intake_queue.csv",
                "default_evidence_status": row["evidence_status"],
                "queue_notes": "Research this lead first. Do not promote to industry_entities.csv or entity_claims.csv until source text supports a specific atlas classification.",
            }
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_PATH.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0].keys()))
        writer.writeheader()
        writer.writerows(output_rows)

    print(f"Wrote {len(output_rows)} search queue rows to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
