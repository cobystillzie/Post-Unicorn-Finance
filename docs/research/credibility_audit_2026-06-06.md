# Credibility Audit — Post-Unicorn Finance Atlas (2026-06-06)

**Status: flag-only review artifact.** Per CLAUDE.md (flag misclassifications, do not auto-edit), **no CSVs were
modified.** This is step 2 of the operator directive ("make the list more credible") and the input to step 3
("find in-disguise funds outside blatant anti-unicorn VC"). Method = rubric v5, judged on each firm's own live
page (raw bytes via `curl | data/runtime/strip_page.py` — no summarizer in the loop).

## 1. Locked denominator (provable; resolves the prior 75 vs 84 vs "49+24" drift)

- **Deliverable `funds_verified.csv` = 75 admits** = **60 strict self_id (Tier 1) + 15 in-disguise (Tier 2)**.
  Status: 72 verified, 2 pending_verification, 1 held_for_review.
- **Classification `atlas_asset_class_audit.csv` = 84 rows** = 73 admits-in-both + 8 anchors + 2
  Excluded-Traditional + Ascendant. **Active classified = 81.**
- **Anchors `funds_anchors.csv` = 11** (Ethan-graph provenance), 8 of which appear in the audit.

## 2. Composition — the central credibility problem (denominator = 81 active)

| Asset class | Count | Share |
|---|---:|---:|
| Permanent | 53 | 65% |
| Nimble | 21 | 26% |
| SMV | 2 | 2.5% |
| Studio | 2 | 2.5% |
| Reserved | 3 | 3.7% |

Two classes hold **91%**; SMV+Studio = 4 rows (5%); Operator + Sovereign unpopulated. A prior advisor-sharpened
blueprint note (2026-06-03) already reached this independently: the strict gate, as operationalized, keys on
ONE dialect ("we never sell" software holdcos), so **yield-decline and archetype-concentration are the same
problem.** An atlas that is ~two-thirds buy-and-hold software holdcos invites the skeptic's dismissal — "this is
the Constellation-imitator niche, not a broad post-unicorn industry." This is the load-bearing issue → fork §7.

## 3. Data-integrity gaps (flag)

- **Unclassified admits:** `finis-ventures`, `five19-holdings` are in the 75-admit deliverable but have NO row
  in the classification audit → no asset_class/tier. Need classification or removal.
- **Contradictory tags:** `ascendant-ventures` is tagged BOTH `Excluded-Traditional` AND `in_disguise` (see §4②).

## 4. Low-confidence row re-grounding (live own-page, raw bytes, 2026-06-06)

**① 5X Capital — UPGRADE (credibility win).** Site is now live (was a maintenance placeholder on 2026-06-02).
The own page now carries an explicit Tier-1 model-rejection, verbatim: *"Compounding beats exits. We don't
operate on a fund clock. Profitable and sustainable companies — compounding value and paying dividends — are
worth more than a forced exit."* Allocator ✓ (equity into LatAm B2B SaaS/AI), tech-enabled ✓.
→ Recommend promote `provenance → self_id`, confidence `low → high`. The earlier unverifiable WebFetch line is
now confirmed on the raw page (anti-hallucination satisfied).

**② Ascendant Ventures — RESOLVE CONTRADICTION → Excluded-Traditional.** Own page: *"a private investment
company focused on acquiring and running small businesses in the South East of the UK with EBITDA £0.3–2M…
low-risk businesses with enduring profitability."* Priority sectors: business services, energy & environment,
healthcare services, construction, engineering & manufacturing, distribution & logistics, facilities management.
→ A **non-tech, traditional UK SMB ETA buyer.** The `in_disguise` tag is wrong; `Excluded-Traditional` is right.
**Methodological flag:** rubric v5 uses Ascendant as its S2 "structurally-SMV deal profile" *floor example* — but
Ascendant is a traditional-economy firm, so the S2 signal as illustrated risks admitting non-tech SMB holdcos
(sieve). The S2 example should be replaced with a tech-enabled firm.

**③ The Perpetuity Project — FLAG (same leak).** Own page: *"a holding company dedicated to acquiring and
growing solid small and medium-sized businesses across Europe, with a long-term, perpetual investment horizon"*;
contrast table "perpetual home / decades not quarters" vs "Traditional Investors: short-term mindset." The
permanent-hold language is genuine and it is an allocator ✓ — BUT it is a **generalist European SMB-succession
holdco with no stated tech focus** (tech-enablement unconfirmed). → Same pattern as Ascendant; recommend re-tag
flagged-traditional pending a tech-enablement check.

**④ Capacity Capital — UNVERIFIABLE.** `curl` of capacitycapital.co returned an empty body (JS-only, blocked, or
dead). The "revenue-based" in_disguise signal cannot be confirmed on the own page. → Stays `pending_verification`;
needs a browser fetch or removal. A low-confidence in_disguise admit whose page will not even fetch is not
credible as-is.

## 5. Systemic finding — the tech-enablement leak

2 of 4 low-conf rows (Ascendant, Perpetuity) are **generalist/traditional SMB-succession holdcos** that pass the
anti-unicorn *philosophy* test (permanent-hold / acquires-profitable-businesses) but FAIL the atlas's
**tech-enabled** requirement (CLAUDE.md "global and tech-enabled"; the Ethan Gate tech-enabled filter). The
in_disguise S2 signal ("acquires enduringly-profitable businesses") structurally overlaps with traditional
ETA/search-fund SMB buyers. **This is the highest-value credibility hole found:** the in_disguise tier likely
contains more non-tech traditional holdcos that should be Excluded-Traditional. Any in-disguise discovery round
(step 3) MUST add a tech-enablement gate, or it will pull in traditional ETA.

## 6. Queued worklist (next chunk — same method, flag-only)

Re-ground on live own-page + explicit tech-enablement check:
- **Remaining 12 in_disguise:** cornerstone-ventures, pemba-capital, 4d-ventures, buentrip-ventures,
  camel-ventures-egypt, henq, saasholic, startup-ignition-ventures, sts-ventures, upsidedown-vc, software-circle,
  + the two Reserved/zebra rows below.
- **Excluded-Traditional confirm:** collab-holdings, emikoly (+ ascendant per §4②).
- **Reserved (Sovereign-candidates, parked):** village-capital, zebra-impact-ventures, zebras-and-company.
- **Unclassified:** finis-ventures, five19-holdings.

## 7. STRATEGIC FORK — needs operator decision (do not assume)

The §2 concentration admits two opposite remediations, which assert different things about the industry:

- **(A) Diversify** — mine in-disguise allocators into the empty classes (SMV, Studio, Nimble breadth, later
  Operator/Sovereign) to demonstrate a broad industry. RISK: the rubric's own warning — widening for breadth can
  make the gate a *sieve*; the §5 leak shows the in_disguise S2 signal already over-admits traditional holdcos.
- **(B) Report the concentration honestly** — "the strict anti-unicorn / camel industry today clusters in
  permanent-capital software holdcos + capital-efficient equity" may be the more *defensible* empirical finding,
  with the other classes documented as thin/emerging.
- **(C) Both** — keep hunting in-disguise breadth but never soften the S1/S2/S3 verbatim bar (add the §5
  tech-enablement gate), AND report the true distribution honestly. Most intellectually honest; slowest.

Per the blueprint this axis has never been put to the operator. The "look outside blatant anti-unicorn VC"
directive leans (A)/(C) — but it must be confirmed, not assumed.
