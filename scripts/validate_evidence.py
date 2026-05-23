"""Validate Post-Unicorn Finance evidence and atlas tables."""

from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "data" / "evidence"
SCHEMA_PATH = EVIDENCE_DIR / "schema.json"

PATHS = {
    "asset_classes": EVIDENCE_DIR / "asset_classes.csv",
    "industry_entities": EVIDENCE_DIR / "industry_entities.csv",
    "entity_claims": EVIDENCE_DIR / "entity_claims.csv",
    "instrument_provider_map": EVIDENCE_DIR / "instrument_provider_map.csv",
    "scrape_targets": EVIDENCE_DIR / "scrape_targets.csv",
    "entity_intake_queue": EVIDENCE_DIR / "entity_intake_queue.csv",
    "company_events": EVIDENCE_DIR / "company_events.csv",
    "funds_instruments": EVIDENCE_DIR / "funds_instruments.csv",
    "source_registry": EVIDENCE_DIR / "source_registry.csv",
}


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def split_tags(value: str) -> list[str]:
    return [tag.strip() for tag in value.split(";") if tag.strip()]


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def require_columns(table: str, rows: list[dict[str, str]], required: list[str]) -> list[str]:
    if not rows:
        return [f"{table}.csv has no rows"]
    missing = [col for col in required if col not in rows[0]]
    if missing:
        return [f"{table}.csv missing columns: {', '.join(missing)}"]
    return []


def require_values(table: str, rows: list[dict[str, str]], required: list[str]) -> list[str]:
    errors: list[str] = []
    for index, row in enumerate(rows, start=2):
        for col in required:
            if not row.get(col, "").strip():
                errors.append(f"{table}.csv:{index} missing value for {col}")
    return errors


def validate_asset_classes(schema: dict) -> list[str]:
    errors: list[str] = []
    rows = read_csv(PATHS["asset_classes"])
    required = schema["asset_classes"]["required_columns"]
    errors.extend(require_columns("asset_classes", rows, required))
    if errors:
        return errors
    errors.extend(require_values("asset_classes", rows, required))

    allowed_assets = set(schema["common"]["allowed_asset_classes"])
    allowed_statuses = set(schema["asset_classes"]["allowed_classification_statuses"])
    seen = set()
    for index, row in enumerate(rows, start=2):
        label = f"asset_classes.csv:{index}"
        asset = row["asset_class"]
        if asset not in allowed_assets:
            errors.append(f"{label} invalid asset_class: {asset}")
        if asset in seen:
            errors.append(f"{label} duplicate asset_class: {asset}")
        seen.add(asset)
        if row["classification_status"] not in allowed_statuses:
            errors.append(f"{label} invalid classification_status: {row['classification_status']}")
    return errors


def validate_industry_entities(schema: dict) -> list[str]:
    errors: list[str] = []
    rows = read_csv(PATHS["industry_entities"])
    required = schema["industry_entities"]["required_columns"]
    errors.extend(require_columns("industry_entities", rows, required))
    if errors:
        return errors
    errors.extend(require_values("industry_entities", rows, required))

    allowed_assets = set(schema["common"]["allowed_asset_classes"])
    non_primary_classes = set(schema["common"].get("non_primary_entity_classes", []))
    allowed_statuses = set(schema["common"]["allowed_evidence_statuses"])
    allowed_tiers = set(schema["common"]["allowed_source_tiers"])
    allowed_active = set(schema["common"]["allowed_active_statuses"])
    seen_ids = set()
    seen_name_site = set()

    for index, row in enumerate(rows, start=2):
        label = f"industry_entities.csv:{index}"
        entity_id = row["entity_id"]
        if entity_id in seen_ids:
            errors.append(f"{label} duplicate entity_id: {entity_id}")
        seen_ids.add(entity_id)

        pair = (normalize(row["name"]), normalize(row["website"]))
        if pair in seen_name_site:
            errors.append(f"{label} duplicate normalized name+website: {row['name']}")
        seen_name_site.add(pair)

        if row["primary_asset_class"] not in allowed_assets:
            errors.append(f"{label} invalid primary_asset_class: {row['primary_asset_class']}")
        if row["primary_asset_class"] in non_primary_classes:
            errors.append(
                f"{label} non-primary class used as primary_asset_class: {row['primary_asset_class']}"
            )
        for asset in split_tags(row.get("secondary_asset_classes", "")):
            if asset not in allowed_assets:
                errors.append(f"{label} invalid secondary_asset_class: {asset}")
        if row["active_status"] not in allowed_active:
            errors.append(f"{label} invalid active_status: {row['active_status']}")
        if row["source_tier"] not in allowed_tiers:
            errors.append(f"{label} invalid source_tier: {row['source_tier']}")
        if row["evidence_status"] not in allowed_statuses:
            errors.append(f"{label} invalid evidence_status: {row['evidence_status']}")
        if not is_url(row["website"]):
            errors.append(f"{label} invalid website: {row['website']}")
        try:
            score = int(row["fit_score"])
        except ValueError:
            errors.append(f"{label} fit_score is not an integer")
        else:
            if not 0 <= score <= 100:
                errors.append(f"{label} fit_score out of range: {score}")

    if len(rows) < 100:
        errors.append(f"industry_entities.csv has {len(rows)} rows; expected at least 100")
    return errors


def validate_entity_claims(schema: dict) -> list[str]:
    errors: list[str] = []
    rows = read_csv(PATHS["entity_claims"])
    entities = {row["entity_id"] for row in read_csv(PATHS["industry_entities"])}
    required = schema["entity_claims"]["required_columns"]
    errors.extend(require_columns("entity_claims", rows, required))
    if errors:
        return errors
    errors.extend(require_values("entity_claims", rows, required))

    allowed_statuses = set(schema["common"]["allowed_evidence_statuses"])
    allowed_qualities = set(schema["common"]["allowed_source_qualities"])
    allowed_tiers = set(schema["common"]["allowed_source_tiers"])
    seen_claims = set()
    claim_entity_ids = set()

    for index, row in enumerate(rows, start=2):
        label = f"entity_claims.csv:{index}"
        claim_id = row["claim_id"]
        if claim_id in seen_claims:
            errors.append(f"{label} duplicate claim_id: {claim_id}")
        seen_claims.add(claim_id)

        if row["entity_id"] not in entities:
            errors.append(f"{label} unknown entity_id: {row['entity_id']}")
        claim_entity_ids.add(row["entity_id"])
        if row["evidence_status"] not in allowed_statuses:
            errors.append(f"{label} invalid evidence_status: {row['evidence_status']}")
        if row["source_quality"] not in allowed_qualities:
            errors.append(f"{label} invalid source_quality: {row['source_quality']}")
        if row["source_tier"] not in allowed_tiers:
            errors.append(f"{label} invalid source_tier: {row['source_tier']}")
        if not is_url(row["source_url"]):
            errors.append(f"{label} invalid source_url: {row['source_url']}")

    missing_claims = sorted(entities - claim_entity_ids)
    if missing_claims:
        errors.append(f"entities without claims: {', '.join(missing_claims[:20])}")
    return errors


def validate_instrument_provider_map(schema: dict) -> list[str]:
    errors: list[str] = []
    rows = read_csv(PATHS["instrument_provider_map"])
    entities = {row["entity_id"] for row in read_csv(PATHS["industry_entities"])}
    required = schema["instrument_provider_map"]["required_columns"]
    errors.extend(require_columns("instrument_provider_map", rows, required))
    if errors:
        return errors
    errors.extend(require_values("instrument_provider_map", rows, required))

    allowed_assets = set(schema["common"]["allowed_asset_classes"])
    non_primary_classes = set(schema["common"].get("non_primary_entity_classes", []))
    allowed_statuses = set(schema["common"]["allowed_evidence_statuses"])
    for index, row in enumerate(rows, start=2):
        label = f"instrument_provider_map.csv:{index}"
        if row["provider_entity_id"] not in entities:
            errors.append(f"{label} unknown provider_entity_id: {row['provider_entity_id']}")
        if row["asset_class"] not in allowed_assets:
            errors.append(f"{label} invalid asset_class: {row['asset_class']}")
        if row["asset_class"] in non_primary_classes:
            errors.append(f"{label} non-primary class used as mapped asset_class: {row['asset_class']}")
        if row["evidence_status"] not in allowed_statuses:
            errors.append(f"{label} invalid evidence_status: {row['evidence_status']}")
        if not is_url(row["source_url"]):
            errors.append(f"{label} invalid source_url: {row['source_url']}")
    return errors


def validate_scrape_targets(schema: dict) -> list[str]:
    errors: list[str] = []
    rows = read_csv(PATHS["scrape_targets"])
    required = schema["scrape_targets"]["required_columns"]
    errors.extend(require_columns("scrape_targets", rows, required))
    if errors:
        return errors
    errors.extend(require_values("scrape_targets", rows, required))

    allowed_assets = set(schema["common"]["allowed_asset_classes"])
    non_primary_classes = set(schema["common"].get("non_primary_entity_classes", []))
    allowed_tiers = set(schema["common"]["allowed_source_tiers"])
    allowed_priorities = set(schema["scrape_targets"]["allowed_priorities"])
    for index, row in enumerate(rows, start=2):
        label = f"scrape_targets.csv:{index}"
        if row["target_asset_class"] not in allowed_assets:
            errors.append(f"{label} invalid target_asset_class: {row['target_asset_class']}")
        if row["target_asset_class"] == "Instrument":
            errors.append(f"{label} Instrument cannot be a target_asset_class; use a real entity class")
        if row["source_tier"] not in allowed_tiers:
            errors.append(f"{label} invalid source_tier: {row['source_tier']}")
        if row["priority"] not in allowed_priorities:
            errors.append(f"{label} invalid priority: {row['priority']}")
    return errors


def validate_entity_intake_queue(schema: dict) -> list[str]:
    errors: list[str] = []
    rows = read_csv(PATHS["entity_intake_queue"])
    required = schema["entity_intake_queue"]["required_columns"]
    errors.extend(require_columns("entity_intake_queue", rows, required))
    if errors:
        return errors
    errors.extend(require_values("entity_intake_queue", rows, required))

    allowed_assets = set(schema["common"]["allowed_asset_classes"])
    non_primary_classes = set(schema["common"].get("non_primary_entity_classes", []))
    allowed_statuses = set(schema["common"]["allowed_evidence_statuses"])
    allowed_tiers = set(schema["common"]["allowed_source_tiers"])
    allowed_active = set(schema["common"]["allowed_active_statuses"])
    allowed_priorities = set(schema["entity_intake_queue"]["allowed_priorities"])
    allowed_review = set(schema["entity_intake_queue"]["allowed_review_statuses"])
    registry_urls = {row["source_url"].strip() for row in read_csv(PATHS["source_registry"])}
    atlas_names = {normalize(row["name"]) for row in read_csv(PATHS["industry_entities"])}
    claim_names = {normalize(row["entity_name"]) for row in read_csv(PATHS["entity_claims"])}
    seen_ids: set[str] = set()
    seen_name_site: set[tuple[str, str]] = set()

    for index, row in enumerate(rows, start=2):
        label = f"entity_intake_queue.csv:{index}"
        lead_id = row["lead_id"]
        if lead_id in seen_ids:
            errors.append(f"{label} duplicate lead_id: {lead_id}")
        seen_ids.add(lead_id)

        pair = (normalize(row["name"]), normalize(row["website"]))
        if pair in seen_name_site:
            errors.append(f"{label} duplicate normalized name+website: {row['name']}")
        seen_name_site.add(pair)

        if row["review_status"] not in {"promoted", "duplicate"} and normalize(row["name"]) in atlas_names:
            errors.append(f"{label} intake lead already exists in industry_entities.csv: {row['name']}")
        if row["review_status"] not in {"promoted", "duplicate"} and normalize(row["name"]) in claim_names:
            errors.append(f"{label} intake lead already exists in entity_claims.csv: {row['name']}")
        if not is_url(row["website"]):
            errors.append(f"{label} invalid website: {row['website']}")
        for source_url in split_tags(row["source_urls"]):
            if not is_url(source_url):
                errors.append(f"{label} invalid source_url: {source_url}")
            if source_url not in registry_urls:
                errors.append(f"{label} source not in registry: {source_url}")
        if row["target_asset_class"] not in allowed_assets:
            errors.append(f"{label} invalid target_asset_class: {row['target_asset_class']}")
        if row["target_asset_class"] == "Instrument":
            errors.append(f"{label} Instrument cannot be a target_asset_class; use a real entity class")
        if row["active_status"] not in allowed_active:
            errors.append(f"{label} invalid active_status: {row['active_status']}")
        if row["source_tier"] not in allowed_tiers:
            errors.append(f"{label} invalid source_tier: {row['source_tier']}")
        if row["priority"] not in allowed_priorities:
            errors.append(f"{label} invalid priority: {row['priority']}")
        if row["evidence_status"] not in allowed_statuses:
            errors.append(f"{label} invalid evidence_status: {row['evidence_status']}")
        if row["review_status"] not in allowed_review:
            errors.append(f"{label} invalid review_status: {row['review_status']}")
    return errors


def validate_company_events(schema: dict) -> list[str]:
    errors: list[str] = []
    rows = read_csv(PATHS["company_events"])
    required = schema["company_events"]["required_columns"]
    errors.extend(require_columns("company_events", rows, required))
    if errors:
        return errors
    errors.extend(require_values("company_events", rows, required))

    allowed_assets = set(schema["common"]["allowed_asset_classes"])
    allowed_pathways = set(schema["company_events"]["allowed_pathways"])
    allowed_statuses = set(schema["common"]["allowed_evidence_statuses"])
    allowed_qualities = set(schema["common"]["allowed_source_qualities"])
    seen_keys: set[tuple[str, str, str]] = set()

    for index, row in enumerate(rows, start=2):
        label = f"company_events.csv:{index}"
        key = (
            row["company_name"].strip().lower(),
            row["event_type"].strip().lower(),
            row["source_url"].strip().lower(),
        )
        if key in seen_keys:
            errors.append(f"{label} duplicate company/event/source key")
        seen_keys.add(key)
        if row["asset_bucket"] not in allowed_assets:
            errors.append(f"{label} invalid asset_bucket: {row['asset_bucket']}")
        for pathway in split_tags(row["pathway"]):
            if pathway not in allowed_pathways:
                errors.append(f"{label} invalid pathway tag: {pathway}")
        if row["evidence_status"] not in allowed_statuses:
            errors.append(f"{label} invalid evidence_status: {row['evidence_status']}")
        if row["source_quality"] not in allowed_qualities:
            errors.append(f"{label} invalid source_quality: {row['source_quality']}")
        if not is_url(row["source_url"]):
            errors.append(f"{label} invalid source_url: {row['source_url']}")
        try:
            score = int(row["confidence_score"])
        except ValueError:
            errors.append(f"{label} confidence_score is not an integer")
        else:
            if not 0 <= score <= 100:
                errors.append(f"{label} confidence_score out of range: {score}")
    return errors


def validate_funds_table(schema: dict) -> list[str]:
    errors: list[str] = []
    rows = read_csv(PATHS["funds_instruments"])
    if not rows:
        return ["funds_instruments.csv has no rows"]
    required = [
        "name",
        "entity_type",
        "category",
        "claim",
        "source_url",
        "source_quality",
        "evidence_status",
        "why_it_matters",
        "last_verified_at",
    ]
    errors.extend(require_columns("funds_instruments", rows, required))
    if errors:
        return errors
    errors.extend(require_values("funds_instruments", rows, required))

    allowed_statuses = set(schema["common"]["allowed_evidence_statuses"])
    allowed_qualities = set(schema["common"]["allowed_source_qualities"])
    for index, row in enumerate(rows, start=2):
        label = f"funds_instruments.csv:{index}"
        if not is_url(row["source_url"]):
            errors.append(f"{label} invalid source_url: {row['source_url']}")
        if row["evidence_status"] not in allowed_statuses:
            errors.append(f"{label} invalid evidence_status: {row['evidence_status']}")
        if row["source_quality"] not in allowed_qualities:
            errors.append(f"{label} invalid source_quality: {row['source_quality']}")
    return errors


def validate_registry_coverage() -> list[str]:
    errors: list[str] = []
    registry_urls = {row["source_url"].strip() for row in read_csv(PATHS["source_registry"])}
    table_names = [
        "company_events",
        "funds_instruments",
        "entity_claims",
        "instrument_provider_map",
    ]
    for table_name in table_names:
        for index, row in enumerate(read_csv(PATHS[table_name]), start=2):
            url = row.get("source_url", "").strip()
            if url and url not in registry_urls:
                errors.append(f"{table_name}.csv:{index} source not in registry: {url}")
    return errors


def main() -> int:
    schema = load_schema()
    errors = []
    errors.extend(validate_asset_classes(schema))
    errors.extend(validate_industry_entities(schema))
    errors.extend(validate_entity_claims(schema))
    errors.extend(validate_instrument_provider_map(schema))
    errors.extend(validate_scrape_targets(schema))
    errors.extend(validate_entity_intake_queue(schema))
    errors.extend(validate_company_events(schema))
    errors.extend(validate_funds_table(schema))
    errors.extend(validate_registry_coverage())

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Validation passed")
    print(f"- asset_classes: {len(read_csv(PATHS['asset_classes']))}")
    print(f"- industry_entities: {len(read_csv(PATHS['industry_entities']))}")
    print(f"- entity_claims: {len(read_csv(PATHS['entity_claims']))}")
    print(f"- instrument_provider_map: {len(read_csv(PATHS['instrument_provider_map']))}")
    print(f"- scrape_targets: {len(read_csv(PATHS['scrape_targets']))}")
    print(f"- entity_intake_queue: {len(read_csv(PATHS['entity_intake_queue']))}")
    print(f"- company_events_supporting: {len(read_csv(PATHS['company_events']))}")
    print(f"- source_registry: {len(read_csv(PATHS['source_registry']))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
