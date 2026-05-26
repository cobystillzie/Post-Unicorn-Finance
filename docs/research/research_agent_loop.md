# Research-Agent Loop

## Purpose

The research agents operate the industry atlas before the paper is drafted. Their job is to expand, verify, rank, and improve the directory of Post-Unicorn Finance entities.

The loop is local-first:

- CSV and Markdown stay human-readable.
- SQLite stores operational state.
- Generated exports stay in `data/exports`.
- Human review is required before paper use.

## Commands

Build the SQLite atlas:

```powershell
python scripts/atlas_sqlite.py build
```

Run the hourly-safe loop manually:

```powershell
python scripts/research_agents.py hourly-loop --fetch-limit 5
```

Run the local learning-ops loop:

```powershell
python scripts/learning_ops.py learning-loop --review-limit 250
```

Run stages separately:

```powershell
python scripts/research_agents.py discover
python scripts/research_agents.py fetch-sources --verified-only --limit 3
python scripts/research_agents.py extract-claims --limit 3
python scripts/research_agents.py classify
python scripts/research_agents.py dedupe
python scripts/research_agents.py verify-intake --limit 10
python scripts/research_agents.py promote-intake --limit 10
python scripts/research_agents.py promotion-loop --limit 10
python scripts/research_agents.py evolve
python scripts/research_agents.py validate --strict
```

Reset SQLite from CSV before a one-off loop only when that is intentional:

```powershell
python scripts/research_agents.py run-loop --reset-from-csv --fetch-limit 5
```

Record human feedback:

```powershell
python scripts/research_agents.py feedback --target-type claim --target-id CLAIM_ID --label accepted --rationale "Source supports the claim."
```

Allowed feedback labels:

- `accepted`
- `rejected`
- `needs_more_source`
- `wrong_bucket`
- `duplicate`
- `too_broad`
- `paper_ready`

## Agent Stages

1. Discovery Agent reads `scrape_targets.csv` and creates source-seeking candidate leads.
2. Discovery Agent also ingests queued leads from `entity_intake_queue.csv`; these leads are not atlas entities yet.
3. Source Fetch Agent fetches official pages, queued lead sources, and credible public profiles with URL dedupe and fetch caps.
4. Claim Extraction Agent turns source text into atomic source-backed claims for existing atlas entities only.
5. Classification Agent creates non-destructive asset-class suggestions.
6. Dedupe Agent flags possible duplicate entity pairs for human review.
7. Intake Verification Agent evaluates `entity_intake_queue.csv` leads against fetched source text.
8. Intake Promotion Agent can promote qualified leads into `industry_entities.csv` and `entity_claims.csv` as `candidate_evidence`.
9. Ranking Agent regenerates all-row ranked exports and top-150 triage exports from SQLite.
10. Human Feedback Loop stores accepted/rejected/paper-ready decisions.
11. Evolution Agent proposes scrape, scoring, and coverage improvements.
12. Learning Ops converts reviewed claims into training/eval JSONL, baseline metrics, and a fine-tune readiness manifest.

## Intake Promotion

The promotion path is deliberately stricter than discovery:

- one fetched direct source must support the entity name, website/domain, role, and asset-class fit,
- duplicate names/domains are marked `duplicate`,
- ambiguous leads are marked `needs_more_source`,
- promoted rows are always `candidate_evidence`,
- promoted rows are never `paper_ready`,
- publication still requires human review or a later dual-review gate.

## Safety Rules

- Discovery does not create verified facts.
- Entity-intake leads do not become atlas entities until source text supports a specific claim and classification.
- Agent-extracted claims are source-text observations, not paper-ready claims.
- Intake-promoted claims are candidate atlas evidence, not publication claims.
- `paper_ready` requires human review.
- Evolution proposals do not mutate schema or scoring automatically.
- Fine-tuning waits until there is a large reviewed corpus. The default gate is 1,000 reviewed examples and 100 eval examples.
