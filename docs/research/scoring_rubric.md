# Scoring Rubric

## Two Different Scores

`fit_score` is the seed research judgment attached to an entity. It answers:

> How strongly does this entity appear to fit its assigned Post-Unicorn Finance bucket?

`atlas_priority_score` is a ranking score computed by `scripts/atlas_scoring.py`. It answers:

> Which entities should be reviewed, verified, and featured first?

Neither score is an investment score.

## Fit Score

The `fit_score` range is 0-100.

- 90-100: direct category anchor with obvious non-unicorn relevance.
- 80-89: strong candidate, but needs more source-text verification or narrower framing.
- 70-79: relevant infrastructure or allocator, but broader than the exact category.
- 50-69: weak or boundary candidate; retain only if it helps explain category edges.
- below 50: should normally stay out of the atlas unless used as a negative benchmark.

## Atlas Priority Score

The ranking formula is:

```text
atlas_priority_score =
  fit_score
+ evidence_status weight
+ active_status weight
+ source_tier weight
+ ecosystem_role weight
+ non-unicorn thesis bonus
- seed-row penalty
```

Weights:

- `verified_fact`: +14
- `candidate_evidence`: +7
- `inference`: +1
- `user_thesis`: +0
- `needs_verification`: -8
- `active`: +8
- `historical`: +3
- `inactive`: +1
- `unknown`: -4
- `public_web`: +7
- `open_dataset`: +3
- `paid_optional`: +0

Selected ecosystem-role weights:

- `SMV capital provider`: +12
- `software acquirer`: +12
- `capital provider`: +10
- `SaaS acquirer`: +10
- `search fund investor`: +10
- `acquisition marketplace`: +9
- `venture studio`: +8
- `sovereign wealth investor`: +7

Rows with the standard seed note lose 2 points because they still need source-text review.

## Examples

TinySeed:

- `fit_score`: 93
- `evidence_status`: `verified_fact`
- `active_status`: `active`
- `source_tier`: `public_web`
- `ecosystem_role`: `accelerator and capital provider`
- `atlas_priority_score`: 120

Formula:

```text
93 + 14 + 8 + 7 - 2 = 120
```

Khazanah Nasional:

- `fit_score`: 74
- `evidence_status`: `candidate_evidence`
- `active_status`: `active`
- `source_tier`: `public_web`
- `ecosystem_role`: `sovereign investor`
- `atlas_priority_score`: 94

Formula:

```text
74 + 7 + 8 + 7 - 2 = 94
```

Khazanah is lower because it is a broad sovereign allocator. It belongs in the Sovereign Capital lane, but it needs more direct evidence before it can be framed as post-unicorn startup-finance infrastructure.
