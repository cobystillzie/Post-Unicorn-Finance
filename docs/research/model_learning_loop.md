# Model Learning Loop

## Purpose

The atlas now has a learning-ops layer, but it is intentionally not a live fine-tune yet. The current system turns human review decisions into training data, measures a deterministic baseline, and blocks fine-tuning until the project has enough labels to evaluate a model safely.

This keeps the research operation honest:

- discovery and promotion can keep expanding the atlas,
- human review supplies the ground truth,
- learning ops converts review labels into a supervised corpus,
- fine-tuning waits until the corpus is large enough and has an evaluation split.

## What Counts As Learning

True model learning starts only when review labels exist in `review_feedback` and `claim_reviews`.

Useful labels are:

- `accepted`
- `rejected`
- `needs_more_source`
- `wrong_bucket`
- `duplicate`
- `too_broad`
- `paper_ready`

The learning loop does not infer these labels by itself. It queues claims for review and exports labels only after a human or explicit reviewer command records them.

## Commands

Build a claim review queue:

```powershell
python scripts/learning_ops.py build-review-queue --limit 250
```

Run the full local learning pass:

```powershell
python scripts/learning_ops.py learning-loop --review-limit 250
```

`learning-loop` uses the shared Post-Unicorn automation lock, so it will not run while the research, promotion, or packet-publish loop owns the local writer lock.

Export reviewed examples into training and eval JSONL:

```powershell
python scripts/learning_ops.py export-training
```

Evaluate the deterministic baseline:

```powershell
python scripts/learning_ops.py evaluate-baseline
```

Check whether fine-tuning is allowed:

```powershell
python scripts/learning_ops.py prepare-fine-tune
```

## Outputs

Generated learning outputs are local operational files under `data/learning`:

- `review_queue.csv`
- `training/claim_review_all.jsonl`
- `training/claim_review_train.jsonl`
- `training/claim_review_eval.jsonl`
- `metrics/baseline_claim_review.json`
- `fine_tune_manifest.json`
- `learning_status.json`
- `learning_status.md`

These are ignored by Git because they change as the atlas changes. The implementation and docs are tracked; the generated queues and corpora are local run artifacts.

## Fine-Tune Gate

The default gate is:

- at least 1,000 reviewed claim examples,
- at least 100 eval examples,
- a non-empty baseline evaluation,
- no automatic paper-ready promotion.

Until those thresholds are met, `prepare-fine-tune` writes a manifest with `status=blocked`. It does not call OpenAI, Hugging Face, or any other fine-tuning provider.

## What The Model Would Learn Later

The first fine-tune candidate is claim review classification:

- whether a source-backed claim should be accepted,
- whether it needs more source support,
- whether it is too broad,
- whether it is the wrong bucket,
- whether it is a duplicate,
- whether it is paper-ready after explicit review.

This is the safest first task because the input and output are already structured around source text, claim text, entity role, source quality, and human labels.

## What Fine-Tuning Should Not Do

Fine-tuning should not:

- discover entities directly,
- bypass source requirements,
- mark claims paper-ready without human review,
- rewrite the taxonomy,
- replace evidence validation,
- classify instruments as asset classes.

The trained model, when allowed later, should act as a reviewer assistant. It should improve triage and consistency, not become the source of truth.

## Current Bottleneck

If `claim_reviews=0`, the project has no supervised training corpus. In that state, the highest-value action is not model tuning. It is reviewing the highest-priority rows in `data/learning/review_queue.csv` and recording labels through:

```powershell
python scripts/research_agents.py feedback --target-type claim --target-id CLAIM_ID --label accepted --rationale "Source supports the claim." --direct-evidence "Relevant source text."
```
