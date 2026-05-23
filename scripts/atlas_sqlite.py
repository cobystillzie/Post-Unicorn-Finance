"""SQLite storage layer for the Post-Unicorn Finance industry atlas."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from atlas_scoring import default_claim_confidence, entity_score


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data" / "evidence"
EXPORTS = ROOT / "data" / "exports"
DEFAULT_DB = ROOT / "data" / "atlas.sqlite"

CSV_PATHS = {
    "asset_classes": EVIDENCE / "asset_classes.csv",
    "industry_entities": EVIDENCE / "industry_entities.csv",
    "entity_claims": EVIDENCE / "entity_claims.csv",
    "instrument_provider_map": EVIDENCE / "instrument_provider_map.csv",
    "source_registry": EVIDENCE / "source_registry.csv",
    "scrape_targets": EVIDENCE / "scrape_targets.csv",
    "entity_intake_queue": EVIDENCE / "entity_intake_queue.csv",
    "company_events": EVIDENCE / "company_events.csv",
    "funds_instruments": EVIDENCE / "funds_instruments.csv",
}

MIRRORED_TABLES = [
    "asset_classes",
    "industry_entities",
    "entity_claims",
    "instrument_provider_map",
    "source_registry",
    "scrape_targets",
    "entity_intake_queue",
    "company_events",
    "funds_instruments",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "item"


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def open_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def exec_script(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS asset_classes (
            asset_class TEXT PRIMARY KEY,
            classification_status TEXT NOT NULL,
            definition TEXT NOT NULL,
            return_model TEXT NOT NULL,
            capital_source TEXT NOT NULL,
            risk_type TEXT NOT NULL,
            liquidity_path TEXT NOT NULL,
            company_stage TEXT NOT NULL,
            founder_profile TEXT NOT NULL,
            industry_standard_signals TEXT NOT NULL,
            notes TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS industry_entities (
            entity_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            primary_asset_class TEXT NOT NULL,
            secondary_asset_classes TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            website TEXT NOT NULL,
            active_status TEXT NOT NULL,
            source_tier TEXT NOT NULL,
            geography TEXT NOT NULL,
            sector_focus TEXT NOT NULL,
            capital_model TEXT NOT NULL,
            instrument_types TEXT NOT NULL,
            target_company_profile TEXT NOT NULL,
            non_unicorn_thesis TEXT NOT NULL,
            ecosystem_role TEXT NOT NULL,
            fit_score INTEGER NOT NULL,
            evidence_status TEXT NOT NULL,
            last_verified_at TEXT NOT NULL,
            notes TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS entity_claims (
            claim_id TEXT PRIMARY KEY,
            entity_id TEXT NOT NULL,
            entity_name TEXT NOT NULL,
            claim_type TEXT NOT NULL,
            claim TEXT NOT NULL,
            source_url TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_quality TEXT NOT NULL,
            source_tier TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            last_verified_at TEXT NOT NULL,
            notes TEXT NOT NULL,
            claim_confidence INTEGER NOT NULL DEFAULT 0,
            source_page_id TEXT NOT NULL DEFAULT '',
            source_text_snippet TEXT NOT NULL DEFAULT '',
            paper_ready INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(entity_id) REFERENCES industry_entities(entity_id)
        );

        CREATE TABLE IF NOT EXISTS instrument_provider_map (
            instrument_id TEXT NOT NULL,
            instrument_name TEXT NOT NULL,
            provider_entity_id TEXT NOT NULL,
            provider_name TEXT NOT NULL,
            asset_class TEXT NOT NULL,
            description TEXT NOT NULL,
            source_url TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            notes TEXT NOT NULL,
            PRIMARY KEY (instrument_id, provider_entity_id),
            FOREIGN KEY(provider_entity_id) REFERENCES industry_entities(entity_id)
        );

        CREATE TABLE IF NOT EXISTS source_registry (
            source_url TEXT PRIMARY KEY,
            source_name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_quality TEXT NOT NULL,
            license_or_access TEXT NOT NULL,
            notes TEXT NOT NULL,
            last_checked TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS scrape_targets (
            target_id TEXT PRIMARY KEY,
            lane TEXT NOT NULL,
            target_asset_class TEXT NOT NULL,
            source_family TEXT NOT NULL,
            query TEXT NOT NULL,
            seed_entities_or_sources TEXT NOT NULL,
            source_tier TEXT NOT NULL,
            priority TEXT NOT NULL,
            expected_fields TEXT NOT NULL,
            notes TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS entity_intake_queue (
            lead_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            lead_type TEXT NOT NULL,
            website TEXT NOT NULL,
            source_urls TEXT NOT NULL,
            discovered_from TEXT NOT NULL,
            target_asset_class TEXT NOT NULL,
            target_entity_type TEXT NOT NULL,
            active_status TEXT NOT NULL,
            source_tier TEXT NOT NULL,
            priority TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            review_status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            notes TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS company_events (
            event_id TEXT PRIMARY KEY,
            company_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            asset_bucket TEXT NOT NULL,
            pathway TEXT NOT NULL,
            claim TEXT NOT NULL,
            why_prioritized TEXT NOT NULL,
            source_url TEXT NOT NULL,
            source_type TEXT NOT NULL,
            source_quality TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            confidence_score INTEGER NOT NULL,
            geography TEXT NOT NULL,
            sector TEXT NOT NULL,
            outcome_type TEXT NOT NULL,
            outcome_value TEXT NOT NULL,
            acquirer_or_investor TEXT NOT NULL,
            funding_path TEXT NOT NULL,
            founder_story_signal TEXT NOT NULL,
            notes TEXT NOT NULL,
            last_verified_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS funds_instruments (
            name TEXT PRIMARY KEY,
            entity_type TEXT NOT NULL,
            category TEXT NOT NULL,
            claim TEXT NOT NULL,
            source_url TEXT NOT NULL,
            source_quality TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            why_it_matters TEXT NOT NULL,
            last_verified_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS source_pages (
            page_id TEXT PRIMARY KEY,
            source_url TEXT NOT NULL UNIQUE,
            fetched_at TEXT NOT NULL,
            status_code INTEGER NOT NULL,
            fetch_status TEXT NOT NULL,
            content_type TEXT NOT NULL,
            title TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            text_hash TEXT NOT NULL,
            error TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS discovery_candidates (
            candidate_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            lane TEXT NOT NULL,
            target_asset_class TEXT NOT NULL,
            name TEXT NOT NULL,
            website TEXT NOT NULL,
            source_url TEXT NOT NULL,
            source_snippet TEXT NOT NULL,
            source_type TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            confidence_score INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            notes TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS classification_suggestions (
            suggestion_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            entity_id TEXT NOT NULL,
            suggested_primary_asset_class TEXT NOT NULL,
            suggested_secondary_asset_classes TEXT NOT NULL,
            suggested_instrument_types TEXT NOT NULL,
            suggested_fit_score INTEGER NOT NULL,
            rationale TEXT NOT NULL,
            confidence_score INTEGER NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(entity_id) REFERENCES industry_entities(entity_id)
        );

        CREATE TABLE IF NOT EXISTS intake_promotion_reviews (
            review_id TEXT PRIMARY KEY,
            lead_id TEXT NOT NULL,
            run_id TEXT NOT NULL,
            status TEXT NOT NULL,
            name TEXT NOT NULL,
            proposed_entity_id TEXT NOT NULL,
            proposed_primary_asset_class TEXT NOT NULL,
            proposed_entity_row TEXT NOT NULL,
            proposed_claim_row TEXT NOT NULL,
            source_url TEXT NOT NULL,
            source_page_id TEXT NOT NULL,
            source_snippet TEXT NOT NULL,
            checks TEXT NOT NULL,
            rejection_reason TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS agent_runs (
            run_id TEXT PRIMARY KEY,
            agent_name TEXT NOT NULL,
            stage TEXT NOT NULL,
            status TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT NOT NULL,
            input_count INTEGER NOT NULL,
            output_count INTEGER NOT NULL,
            notes TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS review_feedback (
            feedback_id TEXT PRIMARY KEY,
            target_type TEXT NOT NULL,
            target_id TEXT NOT NULL,
            label TEXT NOT NULL,
            reviewer TEXT NOT NULL,
            rationale TEXT NOT NULL,
            created_at TEXT NOT NULL,
            applied_to_learning INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS claim_reviews (
            review_id TEXT PRIMARY KEY,
            claim_id TEXT NOT NULL,
            review_status TEXT NOT NULL,
            reviewer TEXT NOT NULL,
            direct_evidence TEXT NOT NULL,
            rationale TEXT NOT NULL,
            created_at TEXT NOT NULL,
            paper_ready INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(claim_id) REFERENCES entity_claims(claim_id)
        );

        CREATE TABLE IF NOT EXISTS query_performance (
            query_id TEXT PRIMARY KEY,
            target_id TEXT NOT NULL,
            query TEXT NOT NULL,
            run_id TEXT NOT NULL,
            results_found INTEGER NOT NULL DEFAULT 0,
            candidates_added INTEGER NOT NULL DEFAULT 0,
            claims_added INTEGER NOT NULL DEFAULT 0,
            accepted_count INTEGER NOT NULL DEFAULT 0,
            rejected_count INTEGER NOT NULL DEFAULT 0,
            notes TEXT NOT NULL,
            last_run_at TEXT NOT NULL,
            FOREIGN KEY(target_id) REFERENCES scrape_targets(target_id)
        );

        CREATE TABLE IF NOT EXISTS evolution_proposals (
            proposal_id TEXT PRIMARY KEY,
            run_id TEXT NOT NULL,
            proposal_type TEXT NOT NULL,
            target TEXT NOT NULL,
            recommendation TEXT NOT NULL,
            rationale TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )


def clear_imported_tables(conn: sqlite3.Connection) -> None:
    for table in reversed(
        [
            "asset_classes",
            "industry_entities",
            "entity_claims",
            "instrument_provider_map",
            "source_registry",
            "scrape_targets",
            "entity_intake_queue",
            "company_events",
            "funds_instruments",
        ]
    ):
        conn.execute(f"DELETE FROM {table}")


def insert_dict(conn: sqlite3.Connection, table: str, row: dict[str, object]) -> None:
    columns = list(row.keys())
    placeholders = ", ".join("?" for _ in columns)
    conn.execute(
        f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
        [row[col] for col in columns],
    )


def import_csvs(db_path: Path, reset: bool = True) -> dict[str, int]:
    if reset and db_path.exists():
        db_path.unlink()
    with open_db(db_path) as conn:
        exec_script(conn)
        clear_imported_tables(conn)

        counts: dict[str, int] = {}
        for row in read_csv(CSV_PATHS["asset_classes"]):
            insert_dict(conn, "asset_classes", row)
        counts["asset_classes"] = conn.execute("SELECT COUNT(*) FROM asset_classes").fetchone()[0]

        for row in read_csv(CSV_PATHS["industry_entities"]):
            row["fit_score"] = int(row["fit_score"])
            insert_dict(conn, "industry_entities", row)
        counts["industry_entities"] = conn.execute("SELECT COUNT(*) FROM industry_entities").fetchone()[0]

        for row in read_csv(CSV_PATHS["entity_claims"]):
            row["claim_confidence"] = default_claim_confidence(row["evidence_status"])
            row["source_page_id"] = ""
            row["source_text_snippet"] = ""
            row["paper_ready"] = 0
            insert_dict(conn, "entity_claims", row)
        counts["entity_claims"] = conn.execute("SELECT COUNT(*) FROM entity_claims").fetchone()[0]

        for row in read_csv(CSV_PATHS["instrument_provider_map"]):
            insert_dict(conn, "instrument_provider_map", row)
        counts["instrument_provider_map"] = conn.execute("SELECT COUNT(*) FROM instrument_provider_map").fetchone()[0]

        for row in read_csv(CSV_PATHS["source_registry"]):
            insert_dict(conn, "source_registry", row)
        counts["source_registry"] = conn.execute("SELECT COUNT(*) FROM source_registry").fetchone()[0]

        for index, row in enumerate(read_csv(CSV_PATHS["scrape_targets"]), start=1):
            row = {"target_id": f"target-{index:03d}-{slug(row['lane'])}", **row}
            insert_dict(conn, "scrape_targets", row)
            insert_dict(
                conn,
                "query_performance",
                {
                    "query_id": f"query-{row['target_id']}",
                    "target_id": row["target_id"],
                    "query": row["query"],
                    "run_id": "seed-import",
                    "results_found": 0,
                    "candidates_added": 0,
                    "claims_added": 0,
                    "accepted_count": 0,
                    "rejected_count": 0,
                    "notes": "Seeded from scrape_targets.csv.",
                    "last_run_at": now_iso(),
                },
            )
        counts["scrape_targets"] = conn.execute("SELECT COUNT(*) FROM scrape_targets").fetchone()[0]

        for row in read_csv(CSV_PATHS["entity_intake_queue"]):
            insert_dict(conn, "entity_intake_queue", row)
        counts["entity_intake_queue"] = conn.execute("SELECT COUNT(*) FROM entity_intake_queue").fetchone()[0]

        for index, row in enumerate(read_csv(CSV_PATHS["company_events"]), start=1):
            row = {"event_id": f"event-{index:04d}-{slug(row['company_name'])}", **row}
            row["confidence_score"] = int(row["confidence_score"])
            insert_dict(conn, "company_events", row)
        counts["company_events"] = conn.execute("SELECT COUNT(*) FROM company_events").fetchone()[0]

        for row in read_csv(CSV_PATHS["funds_instruments"]):
            insert_dict(conn, "funds_instruments", row)
        counts["funds_instruments"] = conn.execute("SELECT COUNT(*) FROM funds_instruments").fetchone()[0]

        conn.commit()
        return counts


def validate_database(
    db_path: Path,
    strict_verified_sources: bool = False,
    exact_csv_counts: bool = False,
) -> list[str]:
    errors: list[str] = []
    with open_db(db_path) as conn:
        exec_script(conn)
        for table, path in CSV_PATHS.items():
            csv_count = len(read_csv(path))
            db_count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            if exact_csv_counts and csv_count != db_count:
                errors.append(f"{table} count mismatch: csv={csv_count}, sqlite={db_count}")
            if not exact_csv_counts and db_count < csv_count:
                errors.append(f"{table} lost rows relative to csv: csv={csv_count}, sqlite={db_count}")

        for row in conn.execute("SELECT entity_id, name, website FROM industry_entities"):
            if not is_url(row["website"]):
                errors.append(f"invalid entity website for {row['entity_id']}: {row['website']}")

        instrument_primary = conn.execute(
            """
            SELECT entity_id, name
            FROM industry_entities
            WHERE primary_asset_class = 'Instrument'
            """
        ).fetchall()
        for row in instrument_primary:
            errors.append(f"Instrument cannot be a primary entity class: {row['entity_id']} {row['name']}")

        instrument_mapped_class = conn.execute(
            """
            SELECT instrument_id, provider_entity_id, provider_name
            FROM instrument_provider_map
            WHERE asset_class = 'Instrument'
            """
        ).fetchall()
        for row in instrument_mapped_class:
            errors.append(
                "Instrument cannot be the mapped provider asset_class: "
                f"{row['instrument_id']} {row['provider_entity_id']} {row['provider_name']}"
            )

        instrument_targets = conn.execute(
            """
            SELECT target_id, lane
            FROM scrape_targets
            WHERE target_asset_class = 'Instrument'
            """
        ).fetchall()
        for row in instrument_targets:
            errors.append(f"Instrument cannot be a scrape target_asset_class: {row['target_id']} {row['lane']}")

        instrument_intake_targets = conn.execute(
            """
            SELECT lead_id, name
            FROM entity_intake_queue
            WHERE target_asset_class = 'Instrument'
            """
        ).fetchall()
        for row in instrument_intake_targets:
            errors.append(f"Instrument cannot be an intake target_asset_class: {row['lead_id']} {row['name']}")

        atlas_names = {slug(row["name"]) for row in conn.execute("SELECT name FROM industry_entities")}
        claim_names = {slug(row["entity_name"]) for row in conn.execute("SELECT entity_name FROM entity_claims")}
        for row in conn.execute("SELECT lead_id, name, website, source_urls, review_status FROM entity_intake_queue"):
            if not is_url(row["website"]):
                errors.append(f"invalid intake website for {row['lead_id']}: {row['website']}")
            for source_url in [part.strip() for part in row["source_urls"].split(";") if part.strip()]:
                if not is_url(source_url):
                    errors.append(f"invalid intake source URL for {row['lead_id']}: {source_url}")
            if row["review_status"] not in {"promoted", "duplicate"} and slug(row["name"]) in atlas_names:
                errors.append(f"intake lead already exists in industry_entities: {row['lead_id']} {row['name']}")
            if row["review_status"] not in {"promoted", "duplicate"} and slug(row["name"]) in claim_names:
                errors.append(f"intake lead already exists in entity_claims: {row['lead_id']} {row['name']}")

        missing_claims = conn.execute(
            """
            SELECT entity_id, name
            FROM industry_entities e
            WHERE NOT EXISTS (
                SELECT 1 FROM entity_claims c WHERE c.entity_id = e.entity_id
            )
            """
        ).fetchall()
        for row in missing_claims:
            errors.append(f"entity has no claims: {row['entity_id']} {row['name']}")

        missing_providers = conn.execute(
            """
            SELECT provider_entity_id, provider_name
            FROM instrument_provider_map m
            WHERE NOT EXISTS (
                SELECT 1 FROM industry_entities e WHERE e.entity_id = m.provider_entity_id
            )
            """
        ).fetchall()
        for row in missing_providers:
            errors.append(f"instrument mapping has unknown provider: {row['provider_entity_id']} {row['provider_name']}")

        if strict_verified_sources:
            verified_without_text = conn.execute(
                """
                SELECT c.claim_id, c.source_url
                FROM entity_claims c
                WHERE c.evidence_status = 'verified_fact'
                  AND NOT EXISTS (
                    SELECT 1
                    FROM source_pages p
                    WHERE p.source_url = c.source_url
                      AND p.fetch_status = 'ok'
                      AND LENGTH(TRIM(p.raw_text)) > 0
                  )
                  AND NOT EXISTS (
                    SELECT 1
                    FROM claim_reviews r
                    WHERE r.claim_id = c.claim_id
                      AND LENGTH(TRIM(r.direct_evidence)) > 0
                  )
                """
            ).fetchall()
            for row in verified_without_text:
                errors.append(f"verified claim lacks fetched source text: {row['claim_id']} {row['source_url']}")
    return errors


def ranked_rows_from_db(db_path: Path, limit: int) -> list[dict[str, str]]:
    with open_db(db_path) as conn:
        rows = [dict(row) for row in conn.execute("SELECT * FROM industry_entities")]
    for row in rows:
        row["fit_score"] = str(row["fit_score"])
        row["atlas_priority_score"] = str(entity_score(row))
    rows.sort(key=lambda item: int(item["atlas_priority_score"]), reverse=True)
    if limit and limit > 0:
        return rows[:limit]
    return rows


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames = ["atlas_priority_score"] + [
        key for key in rows[0].keys() if key != "atlas_priority_score"
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_rankings(db_path: Path, limit: int) -> None:
    rows = ranked_rows_from_db(db_path, limit)
    write_csv(EXPORTS / "ranked_industry_entities_sqlite.csv", rows)
    write_csv(EXPORTS / "ranked_industry_entities_top150_sqlite.csv", ranked_rows_from_db(db_path, 150))
    by_class_dir = EXPORTS / "asset_class_rankings_sqlite"
    by_class_dir.mkdir(parents=True, exist_ok=True)
    for stale_csv in by_class_dir.glob("*.csv"):
        stale_csv.unlink()
    all_rows = ranked_rows_from_db(db_path, 100000)
    for asset_class in sorted({row["primary_asset_class"] for row in all_rows}):
        class_rows = [row for row in all_rows if row["primary_asset_class"] == asset_class]
        safe_name = asset_class.lower().replace("/", "-").replace(" ", "_")
        write_csv(by_class_dir / f"{safe_name}.csv", class_rows)


def export_table(conn: sqlite3.Connection, table: str, path: Path) -> None:
    rows = [dict(row) for row in conn.execute(f"SELECT * FROM {table}")]
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def export_csvs(db_path: Path, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with open_db(db_path) as conn:
        for table in MIRRORED_TABLES:
            export_table(conn, table, output_dir / f"{table}.csv")


def summary(db_path: Path) -> str:
    lines = [f"SQLite atlas: {db_path}"]
    with open_db(db_path) as conn:
        for table in [
            "asset_classes",
            "industry_entities",
            "entity_claims",
            "instrument_provider_map",
            "source_pages",
            "entity_intake_queue",
            "intake_promotion_reviews",
            "review_feedback",
            "claim_reviews",
            "query_performance",
            "evolution_proposals",
        ]:
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            lines.append(f"- {table}: {count}")
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()[:12]
    lines.append(f"- summary_hash: {digest}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(DEFAULT_DB), help="SQLite database path")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("import-csv")
    build = sub.add_parser("build")
    build.add_argument("--rank-limit", type=int, default=0, help="Rows for the main ranked export; 0 means all entities")

    validate = sub.add_parser("validate")
    validate.add_argument("--strict-verified-sources", action="store_true")

    rank = sub.add_parser("rank")
    rank.add_argument("--limit", type=int, default=0, help="Rows for the main ranked export; 0 means all entities")

    export = sub.add_parser("export-csv")
    export.add_argument("--output-dir", default=str(EXPORTS / "sqlite_csv_export"))

    sub.add_parser("summary")

    args = parser.parse_args()
    db_path = Path(args.db)

    if args.command == "import-csv":
        counts = import_csvs(db_path)
        for table, count in counts.items():
            print(f"{table}: {count}")
        return 0

    if args.command == "build":
        counts = import_csvs(db_path)
        export_rankings(db_path, args.rank_limit)
        errors = validate_database(db_path, exact_csv_counts=True)
        if errors:
            print("SQLite validation failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("SQLite build complete")
        for table, count in counts.items():
            print(f"- {table}: {count}")
        print(f"- db: {db_path}")
        return 0

    if args.command == "validate":
        errors = validate_database(
            db_path,
            strict_verified_sources=args.strict_verified_sources,
            exact_csv_counts=False,
        )
        if errors:
            print("SQLite validation failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("SQLite validation passed")
        print(summary(db_path))
        return 0

    if args.command == "rank":
        export_rankings(db_path, args.limit)
        print(f"Wrote SQLite ranked exports with limit {args.limit}")
        return 0

    if args.command == "export-csv":
        export_csvs(db_path, Path(args.output_dir))
        print(f"Exported SQLite mirrored tables to {args.output_dir}")
        return 0

    if args.command == "summary":
        print(summary(db_path))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
