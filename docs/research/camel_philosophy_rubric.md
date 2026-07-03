# Anti-Unicorn Gate — Rubric v5 (TWO-TIER, 2026-06-03)

> Supersedes v4 (the strict thin gate). Per user direction (2026-06-03): **the staged expansion is NOW
> ACTIVE.** The gate is two-tier:
> - **Tier 1 — strict self-ID** (`admitted_via=self_id`): a firm EXPLICITLY rejects the unicorn / power-law /
>   forced-exit model in its own words. (v4, unchanged. The 25 current verified discoveries + 7 anchors.)
> - **Tier 2 — in-disguise** (`admitted_via=in_disguise`): an allocator that is part of the growing
>   camel / anti-unicorn movement, OR is structurally an SMV, **even if it does NOT exclude unicorns.**
>   Carries the `not_outright_anti_unicorn` flag (encoded by `admitted_via=in_disguise`).
>
> Both tiers count toward the 50-fund goal, **but strict vs in-disguise counts stay separately reportable**
> (report as "N strict + M in-disguise"). A high reject rate is still correct; the wider gate is NOT a sieve.

## Allocator test (BOTH tiers — mandatory, unchanged)
Must deploy capital INTO companies (equity / debt / revenue-share / acquisition). Networks, marketplaces,
advisories, conferences, no-capital accelerators, and article/listicle pages → `reject_non_allocator`, even
with perfect camel language. (Allocator types only: SMV, Patient, LMV, Search/ETA, Portfolio, Sovereign,
Camel-VC. UVC = the contrast baseline, never admitted.)

## TIER 1 — strict self-ID (admitted_via=self_id)  [v4, unchanged]
ADMIT only if the firm, in its OWN words on its OWN live page, EXPLICITLY rejects the unicorn / power-law /
forced-exit MODEL. "Anchors are the floor." Every admit needs a verbatim quote + URL, verified on the page.
- **Qualifying:** "not chasing unicorns" / "we invest in camels, not unicorns" / "without the pressure to
  build a unicorn" / "hold forever / we never sell / no mandate to sell / no fund clock" / "we're not a PE
  firm" + permanent hold / "we don't strip and flip" / "compounding beats exits" / "do not risk survival for
  growth" / explicit rejection of "growth at all costs" / blitzscale / VC treadmill / returns capped by
  design / non-dilutive-revenue-based **stated as the explicit alternative to VC**.
- **Non-qualifying (alone):** "sustainable growth", "long-term", "patient", "founder-friendly/first",
  "mission-driven", "impact", "back the best / outliers / ambitious / bold", "we partner for the long run",
  generic "profitability matters" without rejecting the model → `reject_no_explicit_selfid`.

## TIER 2 — in-disguise (admitted_via=in_disguise)  [NEW — ACTIVE 2026-06-03]
ADMIT a Tier-2 (in-disguise) entity if it is **(a) an allocator** AND **(b) shows >=1 SPECIFIC, on-page,
verbatim-quotable camel/SMV signal.** It need NOT reject unicorns; it need only be a credible part of the
movement (open to camels / camel investments) or structurally an SMV "in disguise."

Qualifying Tier-2 signals (>=1, each must be a SPECIFIC on-page quote, never a vibe):
- **S1 — Camel/zebra vocabulary / movement alignment:** explicitly invokes camels (or zebras) vs unicorns,
  or aligns itself with the camel / zebra / seedstrapping / calm / indie movement — *even if unicorns stay
  in scope* (e.g. "we believe in camels, not only unicorns"). [Camel Ventures Egypt, Pemba, BuenTrip]
- **S2 — Structurally-SMV deal profile:** the firm's STATED strategy is to fund/acquire **already-profitable,
  capital-efficient, bootstrapped, enduring, cash-generative** businesses — NOT early high-growth bets hoping
  for power-law outliers. The deal profile itself is the anti-unicorn signal. [Ascendant Ventures]
- **S3 — Revenue-first / profitability-as-thesis:** explicitly orients founders to revenue / profit /
  self-sufficiency over "the next round," as the firm's stated approach. [Startup Ignition Ventures]
- **(provenance)** Ethan-graph vouch is a valid *supporting* path (as for Village/Kickstart), but a Tier-2
  admit still needs its own on-page S1/S2/S3 signal; provenance alone without a signal → flag, surface to user.

### THE DISCRIMINATOR (Tier-2 floor — deal profile, NOT adjectives)
S2/S3 admit on the firm's **deal profile or stated approach, never on adjectives.** A generic seed VC that
backs early high-growth bets hoping for outliers and merely *says* "capital-efficient / long-term /
founder-friendly" does **NOT** qualify. Ascendant qualifies because it ACQUIRES already-profitable, enduring
businesses (no power-law intent). a16z does not — it backs outliers and says nice things. If the written rule
can't separate those two, the gate has no floor.

### Tier-2 STILL REJECTS (anti-sieve guardrails)
- Non-allocators (allocator test above) → `reject_non_allocator`.
- **Generic-only** language ("long-term / patient / founder-friendly / mission / impact / back-the-best /
  sustainable growth") with NO camel vocab AND NO structurally-SMV deal profile AND NO revenue-first thesis
  → `reject_no_explicit_selfid` (still deferred; NOT in-disguise).
- Explicit **power-law / unicorn-hunting** as the core model with no counter-signal → `reject_power_law`.
- Pure financing **PRODUCTS** — RBF lenders offering "non-dilutive capital" to *any* SaaS (incl. VC-backed
  hypergrowth), with no movement thesis and no sustainable-business targeting → reject (a product, not a
  movement-aligned allocator). [Founderpath, re:cap, Round2, Peers & Co, Nautix]

## Verdict taxonomy (v5)
`admit_self_id` (Tier 1) · `admit_in_disguise` (Tier 2, carries not_outright_anti_unicorn) ·
`reject_no_explicit_selfid` · `reject_power_law` · `reject_non_allocator`

## Anti-hallucination (BOTH tiers — mandatory; STRONGER for Tier 2)
Every admit (incl. Tier 2) carries a verbatim quote **seen on the firm's OWN raw page** (web_fetch_exa raw /
browser get_page_text — never a WebFetch summary or a web_search_exa highlight) + the URL. A lower bar = MORE
hand-verification: a Tier-2 admit needs a specific quote showing the ACTUAL signal (the camel word, the
profitable-acquisition deal language, the revenue-first approach) — never a paraphrase or a vibe. Unverifiable
→ `pending_verification`, not admit.

## VALIDATION (v5 — labeled set + hard negatives)
The wider gate's failure mode is becoming a **sieve**, so the load-bearing test is "hard negatives STILL
reject," not "the examples pass."

**Labeled set — must reproduce these exact labels (operator-provided 2026-06-03):**
- Tier-2 ADMIT: Camel Ventures Egypt (S1: "we believe in Camels, not only potential Unicorns"), Pemba (S1+S2:
  "the camel is the more fitting mascot" + backs bootstrapped/profitable), BuenTrip (S1+S2: "resemble Camels
  rather than Unicorns" + capital-efficiency thesis), Ascendant Ventures (**S2 floor**: acquires "enduringly
  profitable" small businesses), Startup Ignition Ventures (S3: "drive to revenue, not the next round" +
  Ethan provenance; $20M pre-seed fund passes allocator test).
- MOVEMENTS (not a fund): Afrikabal (Pan-African permanent-institution example; **nascent, NOT a verified
  allocator** — kept as a movement exemplar only).

**Hard negatives — must STILL reject (proof the gate is not a sieve):**
- a16z, Sequoia, First Round, Foundry, Bessemer, Greylock, Homebrew → `reject_power_law`: back outliers /
  fund-returners; NO camel vocab (S1), NO already-profitable-acquisition deal profile (S2), NO revenue-first
  thesis (S3). "Founder-friendly" adjectives do not create a signal.
- Fundamentum → `reject_power_law` ("we want our portfolio entrepreneurs to [become] decacorns").
- Acquire.com / MicroConf / steward-ownership networks (steward-owned.be) / employee-ownership *grant* funds
  (Steward Market Impact Fund) → `reject_non_allocator`.
- Pure RBF lenders (Founderpath, re:cap, Round2, Peers & Co, Nautix) → reject: a non-dilutive *product* for
  any SaaS, no camel/movement thesis, no sustainable-business-only targeting.

**Tier-1 sanity floor (unchanged):** the 7 self-ID anchors (TinySeed, Calm Company Fund, Lighter Capital,
Indie.vc, Earnest Capital, Gorilla Capital, 5X Capital) must still `admit_self_id`.

## Anchor vs gate (do not conflate)
`funds_anchors.csv` holds **provenance** anchors (Ethan's graph) — a separate, valid admission path. The judge
run never edits the anchors. `funds_verified.csv` holds gate-verified discoveries; `admitted_via` distinguishes
`self_id` (Tier 1) from `in_disguise` (Tier 2). Movements/Instruments live in their own CSVs.

> **Bar history:** v1-v4 = strict self-ID only ("anchors are the floor"). v5 (2026-06-03) activates Tier 2
> (in-disguise) per user direction: entities need not exclude unicorns entirely — they need a specific camel/
> SMV signal and to be a credible part of the movement. Expand deliberately; re-validate against the hard
> negatives after each widening; never soften the allocator test or the verbatim-quote requirement.
