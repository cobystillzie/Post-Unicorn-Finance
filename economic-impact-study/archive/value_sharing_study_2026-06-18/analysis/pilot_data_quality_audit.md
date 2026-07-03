# Pilot Data-Quality Audit - 2026-06-18

This audit documents the rebuilt Phase 0 pilot data after the Codex takeover rebuild. It is a QA artifact, not a new empirical finding.

Source boundary: existing Phase 0 source data only. No licensed provider, paid data, ToS-sensitive scraping, or Phase 2 data spend was used.

## Rebuild Source

- Local raw source: `../data/raw/phase0_claude_output_2026-06-17.json`
- Raw source SHA-256: `F61E7B12BAB4DA51A4565AE827CBF62A6ABAE903E2F654EBD16D551756B03252`
- Source contents checked: 31 pilot companies and 31 verification records.

## Row Counts

| Group | Rows |
|---|---:|
| post-unicorn | 15 |
| vc-backed | 16 |
| total | 31 |

The retained Phase 0 pilot is therefore **15 post-unicorn vs 16 VC-backed**, not a completed 20-vs-20 comparison.

## Coverage Audit

| Coverage check | post-unicorn | vc-backed |
|---|---:|---:|
| Rows | 15 | 16 |
| Machine-parseable headcount | 14/15 | 15/16 |
| Machine-parseable capital amount | 7/15 | 11/16 |
| Both parseable, enabling illustrative per-dollar rows | 6/15 | 11/16 |
| Headcount source URL present | 13/15 | 16/16 |
| Capital amount source URL present | 7/15 | 16/16 |
| Value-sharing source URL present | 15/15 | 16/16 |
| Verification exception rows | 1/15 | 1/16 |

Coverage does not mean comparability. The capital fields still mix acquisition value, equity-grant amounts, IPO proceeds, private funding totals, and non-public private-company values. This is why the first-cuts analysis correctly avoids group medians and group comparisons.

## Denominator Gap

The core denominator problem remains open:

- Post-unicorn rows often have employee-ownership or payout evidence but no comparable whole-portfolio capital-deployed denominator.
- VC-backed rows often have IPO proceeds or venture-funding totals, but those are not equivalent to private-equity acquisition values or employee-ownership conversion economics.
- Headcount timing is uneven: some rows are current, some are transaction-era, and some are IPO-era.
- Ownership distribution is still thin in public data and needs either source-specific manual verification or a licensed provider in Phase 2.

Do not quote per-dollar group results from this pilot. The current per-dollar table only proves that the metric can compute on sourced rows when both a headcount and a capital amount are parseable.

## Exception Ledger

| Company | Group | Current flag | Audit disposition | Next action |
|---|---|---|---|---|
| Bob's Red Mill Natural Foods | post-unicorn | `verified_claims_hold=False` | Keep as retained pilot row, but treat as an exception. Verification notes say no fabrication or material error was found, while also noting a paraphrased/composite quote and secondary-only headcount support. | Review primary company page and secondary headcount sources before any row-fact patch. |
| Warby Parker Inc. | vc-backed | `verified_claims_hold=False` | Keep as retained pilot row, but treat as an exception. Verification notes say the company and core thesis are real, while flagging an overstatement around broad-based employee equity and a headcount conflict. | Review SEC S-1/S-8 and current headcount source before any row-fact patch. |

The selected handling rule is **audit first**: keep rebuilt raw rows intact, log exceptions clearly, and only patch facts after targeted source review.

## Acceptance Status

- Pilot row count retained at 31.
- Group counts retained at 15 post-unicorn and 16 VC-backed.
- Source JSON count retained at 31 companies and 31 verification records.
- The stale `20-vs-20` roadmap wording has been corrected.
- The denominator caveat remains intact and blocks any group-level result.

