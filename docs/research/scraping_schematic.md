# Scraping Schematic

## Goal Function

Maximize coverage of real firms, funds, platforms, instrument providers, and ecosystem entities across Post-Unicorn Finance asset classes, with one source URL per claim, evidence status, asset-class fit score, and no unsourced assertions. Instruments are tracked as financing mechanisms, not primary entity asset classes. Company examples support the atlas but do not drive it.

## Database Priority

Primary tables:

- `asset_classes.csv`
- `industry_entities.csv`
- `entity_claims.csv`
- `instrument_provider_map.csv`
- `scrape_targets.csv`

Supporting tables:

- `company_events.csv`
- `funds_instruments.csv`
- `seed_search_queries.csv`

## Source Tiers

1. Public web: official firm websites, fund pages, acquisition marketplaces, blogs, communities, press, and investor essays.
2. Open datasets: Hugging Face datasets, GitHub lists, public directories, and open Crunchbase-like mirrors.
3. Optional paid/proprietary later: Crunchbase Pro, PitchBook, CB Insights, Preqin, Tracxn, Dealroom, and other licensed private-market databases.

Open datasets are seed material only. They should create leads, not final proof.

## Scrape Lanes

### SMV

Queries:

- acquisition-first venture fund
- profitable SaaS fund
- non-unicorn venture capital
- strategic acquisition startup fund
- smaller exit venture fund
- middle outcome startup capital
- bootstrapped SaaS capital provider

Targets:

- capital providers,
- smaller-exit funds,
- SaaS acquirers,
- strategic middle-market tech acquirers,
- micro-PE software firms,
- platforms serving acquisition-oriented founders.

### Patient Capital

Queries:

- evergreen startup fund
- permanent capital software companies
- patient capital startups
- founder-friendly permanent equity
- hold forever software companies

Targets:

- evergreen funds,
- permanent-capital firms,
- family-office-backed vehicles,
- holding companies,
- long-duration founder capital providers.

### LMV

Queries:

- indie hacker fund
- solo founder fund
- AI micro venture fund
- tiny team startup capital
- micro SaaS investor
- automation-native startup fund

Targets:

- indie-founder funds,
- micro-SaaS capital providers,
- AI-native tiny-team platforms,
- communities that finance or acquire LMV-style companies.

### Search / ETA

Queries:

- search fund investor
- entrepreneurship through acquisition investor
- ETA community
- SMB acquisition platform
- self funded search capital

Targets:

- search-fund investors,
- ETA accelerators,
- SMB acquisition marketplaces,
- operator-first acquisition funds,
- acquisition debt/equity providers.

### Portfolio Capital

Queries:

- software holding company
- SaaS holding company
- vertical software acquirer
- venture studio
- startup foundry
- AI startup studio

Targets:

- venture studios,
- startup foundries,
- SaaS acquirers,
- buy-and-hold software platforms,
- repeatable company-creation platforms.

### Sovereign Capital

Queries:

- sovereign innovation fund
- national technology fund
- strategic technology investment fund
- government backed venture fund
- regional innovation capital

Targets:

- sovereign-backed innovation funds,
- strategic public capital,
- national tech funds,
- regional development capital,
- industrial-policy innovation vehicles.

### Instruments

Queries:

- revenue based financing startup
- royalty financing startups
- shared earnings agreement startups
- capped return startup investing
- milestone tranche startup financing
- non dilutive SaaS financing

Targets:

- revenue-share providers,
- royalty-finance providers,
- shared-earnings providers,
- capped-return investors,
- milestone-tranche capital,
- non-dilutive SaaS financing.

## Batch Workflow

1. Generate raw leads from `scrape_targets.csv`.
2. Normalize entity name, website, geography, role, and candidate asset bucket.
3. Create or update one `industry_entities.csv` row.
4. Create at least one `entity_claims.csv` row with a source URL.
5. Register the source in `source_registry.csv`.
6. Set `evidence_status` conservatively:
   - `candidate_evidence` for discovered leads with relevant source context,
   - `verified_fact` only after source text review,
   - `needs_verification` when the source is weak or ambiguous,
   - `inference` only for clearly marked research judgment,
   - `user_thesis` only for project framing.
7. Run validation.
8. Run entity ranking.
9. Review top-ranked entities per asset class.

## Validation Rules

Every entity must have:

- normalized name,
- valid website URL,
- canonical asset bucket,
- ecosystem role,
- geography,
- active status,
- source tier,
- evidence status,
- fit score,
- at least one source-backed claim.

Every claim must have:

- entity ID,
- source URL,
- source type,
- source quality,
- evidence status,
- claim text,
- verification notes.

## Hugging Face Use

Use Hugging Face as a seed and tooling layer:

- `opensporks/crunchbase`
- `calebheinzman/Crunchbase_People`
- financial-news datasets
- financial NER models

Do not cite Hugging Face datasets as authoritative proof unless provenance, license, freshness, schema, and source lineage have been independently reviewed.

## Expansion Targets

Wave 1:

- 100+ atlas entities,
- one source-backed claim per entity,
- ranked exports by asset class.

Wave 2:

- 250+ atlas entities,
- source text reviewed for the top 50,
- stronger SMV proof lane.

Wave 3:

- 1,000+ raw candidate leads,
- duplicate clusters resolved,
- optional licensed database enrichment if available.
