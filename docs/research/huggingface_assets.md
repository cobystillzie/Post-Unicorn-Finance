# Hugging Face Research Assets

Hugging Face is useful as a discovery and infrastructure layer, not as authoritative truth for company funding histories.

## Candidate Assets

### opensporks/crunchbase

URL: https://hf.co/datasets/opensporks/crunchbase

Possible use:

- seed company names,
- identify funding/acquisition records,
- build matching jobs against public web sources.

Risk:

- mirror provenance and freshness need inspection,
- Crunchbase-derived data may have licensing and completeness constraints,
- should not be cited as final proof without independent source.

### tor24/indian-startup-funding-2015-2024

URL: https://hf.co/datasets/tor24/indian-startup-funding-2015-2024

Possible use:

- India startup funding lead generation,
- compare funded versus bootstrapped Indian companies,
- identify sectors for SMV research.

Risk:

- dataset card notes may include synthetic entries,
- must not be treated as authoritative company history.

### calebheinzman/Crunchbase_People

URL: https://hf.co/datasets/calebheinzman/Crunchbase_People

Possible use:

- seed founder, executive, and investor names,
- connect people to firms or company histories for later verification,
- build entity-resolution tests for people and organizations.

Risk:

- people data may be stale or incomplete,
- Crunchbase-derived lineage may create licensing constraints,
- should not be used as final proof without independent source review.

### aggubandar/startup-funding-llm-data

URL: https://hf.co/datasets/aggubandar/startup-funding-llm-data

Possible use:

- LLM-ready startup funding examples,
- extraction pipeline testing.

Risk:

- schema and provenance must be inspected before use.

### XJCEO/Bloomberg_Financial_News

URL: https://hf.co/datasets/XJCEO/Bloomberg_Financial_News

Possible use:

- historical financial-news mining,
- acquisition headline extraction,
- company and acquirer entity extraction.

Risk:

- old range, reportedly 2006-2013,
- large corpus,
- not SMV-specific.

### zeroshot/twitter-financial-news-topic

URL: https://hf.co/datasets/zeroshot/twitter-financial-news-topic

Possible use:

- topic-classification examples,
- classifier development for finance-related discourse.

Risk:

- not a startup/company database,
- useful for modeling workflow, not evidence.

## Inspection Command

```powershell
python scripts/inspect_hf_assets.py
```

The output is written to `data/exports/huggingface_asset_inspection.json`.
