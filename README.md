# Post-Unicorn Finance

This repo is the research operating system for establishing **Post-Unicorn Finance** as an emerging industry category: the capital stack around venture capital for valuable companies that are not optimized for unicorn outcomes.

The first research priority is the **industry atlas**: a source-backed map of firms, funds, platforms, acquirers, studios, communities, instruments, and capital providers operating outside or adjacent to classic unicorn VC.

Company examples still matter, but they are supporting evidence. The first proof layer is the existence of an industry: the entities, vehicles, instruments, and infrastructure already organizing around non-unicorn outcomes.

## Operating Principle

No claim enters the paper as fact unless it is tied to a source. The database separates:

- `verified_fact`: source directly supports the claim.
- `candidate_evidence`: source supports a related fact, but the classification still needs review.
- `inference`: research judgment derived from sourced evidence.
- `user_thesis`: concept from the project thesis, not an external factual claim.
- `needs_verification`: lead retained for follow-up.

## Current Artifacts

- `data/evidence/asset_classes.csv`: canonical taxonomy buckets and classification status.
- `data/evidence/industry_entities.csv`: firms, funds, platforms, studios, acquirers, communities, and providers.
- `data/evidence/entity_claims.csv`: one source-backed claim per atlas entity.
- `data/evidence/instrument_provider_map.csv`: financing mechanisms and the entities associated with them. Instruments are not primary entity asset classes.
- `data/evidence/scrape_targets.csv`: query and source-lane schematic for iterative scraping.
- `data/evidence/entity_intake_queue.csv`: unclassified user/research leads that need source review before atlas promotion.
- `data/evidence/company_events.csv`: supporting company-event evidence rows for later chapters.
- `data/evidence/funds_instruments.csv`: legacy supporting table retained for continuity.
- `data/evidence/source_registry.csv`: source metadata and quality labels.
- `docs/00_project_brief.md`: locked project direction.
- `docs/01_taxonomy.md`: category logic and classification rules.
- `docs/research/scraping_schematic.md`: scraping plan and batch workflow.
- `docs/paper/post_unicorn_finance_outline.md`: paper architecture.
- `scripts/validate_evidence.py`: schema and source validation.
- `scripts/seed_industry_atlas.py`: seed and refresh the industry atlas tables.
- `scripts/atlas_sqlite.py`: import CSVs into SQLite, validate, export, and rank.
- `scripts/research_agents.py`: staged local research-agent loop.
- `scripts/rank_industry_entities.py`: ranked exports by global score and asset class.
- `scripts/rank_candidates.py`: ranked SMV proof-set export.
- `scripts/inspect_hf_assets.py`: Hugging Face asset inspection helper.

## Quick Start

```powershell
python scripts/seed_industry_atlas.py
python scripts/validate_evidence.py
python scripts/atlas_sqlite.py build
python scripts/research_agents.py hourly-loop --fetch-limit 5
python scripts/research_agents.py promotion-loop --limit 10
python scripts/rank_industry_entities.py
python scripts/rank_candidates.py --limit 25
```

The atlas export is written to `data/exports/ranked_industry_entities.csv`, with per-asset-class exports in `data/exports/asset_class_rankings/`. The default ranked export includes all entities sorted by review priority. Top-150 triage exports are also generated for focused review.

The public atlas packet is published from `site/` through GitHub Pages. The local daily publisher regenerates `site/` from the live SQLite atlas, commits changes only when the packet changes, and pushes to `main` so GitHub Pages redeploys.

The seed atlas is not a publication-ready claim set. It is a structured candidate base: every row must stay tied to a source URL, and source text should be reviewed before any claim enters the paper as verified fact.

Queued intake leads become atlas rows only through the intake promotion path. Promotion requires fetched source text and creates `candidate_evidence` rows, never `paper_ready` rows.

SQLite is the local operational store at `data/atlas.sqlite`. It is generated from CSV and ignored by git to avoid binary churn; CSV and Markdown remain the transparent review surface.
