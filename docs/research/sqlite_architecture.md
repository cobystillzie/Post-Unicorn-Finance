# SQLite Architecture

## Database

Default path:

```text
data/atlas.sqlite
```

The SQLite database is generated from CSV and ignored by git. CSV and Markdown remain the transparent review surface.

## Mirrored Tables

- `asset_classes`
- `industry_entities`
- `entity_claims`
- `instrument_provider_map`
- `source_registry`
- `scrape_targets`
- `entity_intake_queue`
- `company_events`
- `funds_instruments`

## Agent Tables

- `source_pages`: fetched source text and fetch status.
- `discovery_candidates`: raw leads from scrape targets.
- `classification_suggestions`: proposed classification updates.
- `intake_promotion_reviews`: audit trail for intake verification and promotion decisions.
- `agent_runs`: stage-level audit log.
- `review_feedback`: human decisions and labels.
- `claim_reviews`: claim-level review evidence.
- `query_performance`: query and scrape-lane performance metrics.
- `evolution_proposals`: non-mutating improvement proposals.

## Validation

SQLite validation checks:

- SQLite has not lost rows relative to CSV.
- every entity has a valid website URL,
- every entity has at least one claim,
- every queued intake lead has valid source URLs and does not already exist as an atlas entity or claim,
- every instrument mapping points to an existing entity,
- strict mode requires verified claims to have fetched source text or direct review evidence.

Import/build mode also checks exact CSV parity before agents add new rows.

## Export

Ranked SQLite exports are written to:

```text
data/exports/ranked_industry_entities_sqlite.csv
data/exports/ranked_industry_entities_top150_sqlite.csv
data/exports/asset_class_rankings_sqlite/
```

The default ranked SQLite export includes all atlas entities sorted by `atlas_priority_score`. The top-150 file is only a review triage view.

Mirrored table exports can be generated with:

```powershell
python scripts/atlas_sqlite.py export-csv
```
