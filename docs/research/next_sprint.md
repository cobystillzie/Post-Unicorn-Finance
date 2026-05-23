# Next Research Sprint

## Sprint Goal

Expand from the seed database into a broad global **industry atlas** while preserving evidence quality.

## Sprint 1: Industry Atlas Expansion

Target:

- 250 raw industry-entity candidates.
- 100 reviewed entity-claim rows.
- 25-40 high-confidence flagship entities across asset classes.
- 10-15 high-confidence SMV-specific firms, funds, platforms, or acquirers.

Inputs:

- `data/evidence/scrape_targets.csv`
- `data/evidence/industry_entities.csv`
- `data/evidence/entity_claims.csv`
- `data/evidence/entity_intake_queue.csv`
- `data/evidence/instrument_provider_map.csv`
- `data/exports/search_queue.csv`
- `data/exports/ranked_industry_entities.csv`
- Hugging Face seed assets listed in `docs/research/huggingface_assets.md`

Tasks:

1. Work through SMV firm/fund/platform queries first.
2. Research queued intake leads such as OneSixOne Ventures before promoting them into the atlas.
3. Add one row per sourced entity claim.
4. Use `needs_verification` for leads without enough support.
5. Add every source to `source_registry.csv`.
6. Run validation after each batch.
7. Run entity ranking and review the top 150.
8. Only then expand company-event proof rows.

Commands:

```powershell
python scripts/validate_evidence.py
python scripts/rank_industry_entities.py
python scripts/scrape_seed_searches.py
```

## Sprint 2: SMV Proof Lane

Target:

- 50 SMV-specific capital providers, acquirers, studios, or platforms.
- 25 reviewed claims.
- 10 flagship entities for the paper market map.

Focus:

- acquisition-first venture,
- smaller-exit venture,
- profitable SaaS or vertical-software funds,
- software acquirers,
- micro-PE SaaS,
- strategic middle-market tech acquirers,
- non-unicorn founder-friendly capital.

## Sprint 3: Founder / Investor Discourse

Target:

- 50 discourse sources.
- 20 quote candidates.
- 10 paper-ready founder/investor examples.

Rules:

- Do not use discourse as proof of acquisition/funding history unless it directly states the fact.
- Use discourse to explain language, motivation, and category formation.
- Prefer founder essays, company blogs, investor memos, podcasts with transcripts, and credible interviews.

## Sprint 4: Instruments Map

Target:

- 50 funds/platforms/instruments.
- 10 high-confidence market-map categories.
- 5 instrument families explained clearly enough for non-finance readers.

Categories:

- revenue-based financing,
- shared earnings,
- royalty financing,
- capped returns,
- milestone tranches,
- acquisition-first venture,
- search / ETA,
- acquisition marketplaces,
- SaaS acquirers,
- venture studios,
- patient capital.

## Sprint 5: Paper Draft

Target:

- 3,000-5,000 word v0.1 paper draft.
- Source-backed taxonomy table.
- Industry atlas excerpt.
- Market-map table.
- SMV proof-set excerpt.
- Pegasus/SWC appendix draft with no endorsement claims.

Draft order:

1. Thesis and VC complementarity.
2. Taxonomy.
3. Industry atlas and market map.
4. SMV chapter.
5. Company proof as supporting evidence.
6. Liquidity support section.
7. Strategic appendix.

## Stop Conditions

Stop and review before expanding automation if:

- more than 20% of candidate rows fail validation,
- source_registry coverage falls behind,
- rankings over-prioritize famous boundary cases over true SMVs,
- or many rows require the same new classification field.
