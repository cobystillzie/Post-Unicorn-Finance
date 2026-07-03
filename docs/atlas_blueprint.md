# Post-Unicorn Economy Atlas — Blueprint & Implementation Plan

> Status: PLAN (no execution until usage resets). Source of truth for the rebuild.
> Origin: Ethan's blueprint graphic "Success is Being Rewritten — the post-unicorn
> economy is already happening." Every node in that graphic is a **verified anchor**.

## Thesis

The Atlas is a **three-layer knowledge graph** of capital operating outside the
unicorn / power-law model:
1. **Movements** — the culture (communities + philosophies/methods).
2. **Funds & Firms** — the allocators.
3. **Instruments** — the financial mechanisms.

The product is a **viewer-optimal atlas built for a non-technical audience (the boss)**.
Presentation quality is a first-class requirement, not an afterthought.

## Locked decisions (2026-06-02)

- **Three separate layers, no cross-links yet** (no "intermingling"). Each cataloged comprehensively, standalone.
- **Funds & Firms gate = self-identification.** A firm qualifies only if it **states, in its own words, a thesis explicitly alternative to unicorn-chasing**, with a verbatim quote. Two admission paths (updated 2026-06-02; see the funds-anchors update at the end of this doc): (a) explicit self-ID with a verbatim quote, or (b) a genuine behavioral camel signal admitted WITH a `not_outright_anti_unicorn` flag for transparency. Size alone is never the test. Ethan: *"identify firms who have self-identified theses alternate to unicorn chasing."*
- **Count flexes (Gap 1 = B).** 1,000 is an aspiration, not a quota. Gate integrity beats the number. Report the true size of the universe as a finding.
- **Build Funds & Firms fresh (Gap 2 = B).** The current 866 entities become a **background research reservoir** (preserved, nothing deleted). Find ~50-100 verified self-identified firms to start. (Reversible: the 866 can be re-adjudicated against the gate anytime if we later want option A.)
- **Movements + Instruments inclusion bar:** real + documented + post-unicorn-relevant (a citable org, philosophy, or financial structure). NOT the self-ID gate; that bar is funds-only.
- **Camel VC sub-class (named, not carve-outs).** Firms that are structurally VC/seed/angel allocators but self-identify an explicit anti-unicorn/camel thesis ('in disguise') form their own named allocator sub-class - working name **Camel VC** (confirm/rename freely) - beside SMV, LMV, Patient Capital, Search/ETA, Portfolio Capital, Sovereign Capital. Founding members: Gorilla Capital, Kickstart. Per Ethan: there is more than one, so it is a class, not a carve-out.
- **Microacquire → background** (a marketplace, not a fund).
- **Storage = CSV** (sidecar pattern). **Deliverable = a presentation-quality visual atlas** in the blueprint's style.
- **Toolkit designed in, invoked only after reset.**
- Engineering style: Karpathy — smallest end-to-end thing that works first, verifiable steps, no premature abstraction, human in the loop at each gate.

## Layer 1 — Movements (`data/evidence/movements.csv`)

Columns: `movement_id, name, kind(org|philosophy|method), origin_year, origin_place,
originator, ethos, key_voices, examples, evidence_url, evidence_quote, status(verified_anchor|researched|candidate), notes`

Verified anchors (from the blueprint):
- **Orgs:** Zebras Unite, Indie Hackers, MicroConf.
- **Philosophies/methods:** Jugaad, Onça-córnios, Camels, Seedstrapping.
(Zebras Unite, Indie Hackers, MicroConf already exist as discourse nodes in `seed_industry_atlas.py` — reuse.)

## Layer 2 — Funds & Firms (`data/evidence/industry_entities.csv`, re-gated)

Reuse existing columns. Repurpose `non_unicorn_thesis` to hold the firm's **real
self-identified thesis** (no more boilerplate). Add/track: `self_id_quote` (verbatim),
`gate_status(self_id_pass|manual_carveout|background|rejected)`, `layer(funds_core|background)`.

**Verified anchors — 11 funds/firms from Ethan's graph** (verified by provenance:
they are in Ethan's authoritative blueprint, so none is dropped): Earnest Capital,
Indie.vc, Calm Company Fund, Indie Fund I, Lighter Capital, TinySeed, 5X Capital,
Village Capital, Gorilla Capital (gorilla.vc), Kickstart, Microacquire. **Ten are Funds & Firms `funds_core` anchors;
Microacquire is a verified anchor classified to the `background` layer** (it is a
marketplace, not an allocator) — verified and kept, not discarded. Plus **Gorilla Capital** and **Kickstart** are the
founding members of the **Camel VC** sub-class (a named allocator class, not one-off carve-outs).

## Layer 3 — Instruments (`data/evidence/instruments.csv`)

Columns: `instrument_id, name, kind(named_instrument|generic_category), family,
mechanics, pioneered_by, examples, pros, cons, evidence_url, evidence_quote, status, notes`

Families: revenue-linked non-dilutive · earnings-based · capped/structured equity · debt · staged · equity-rights.

Verified anchors (from the blueprint): Revenue share, Milestone tranches, SEAL / Shared
earnings (Earnest), Royalty financing, Capped returns, Venture debt, Comm. warrants, SAFE variants.
(Schema already has an `Instrument` asset class, `instrument_provider_map`, `instrument_types` — reuse later when layers link.)

## The Funds & Firms gate — self-identification judge (rebuilt)

For a candidate firm: WebFetch its site (WebSearch if thin/JS-only). Decide one thing:
**does the firm explicitly state, in its own words, a thesis that positions it as an
alternative to unicorn-chasing?** (e.g., "non-unicorn," "camel," "calm company,"
"profitable / default-alive," "we reject the VC treadmill," non-dilutive-by-design.)
- PASS → requires a `self_id_quote` copied verbatim. → Funds & Firms.
- No explicit self-identified alternative thesis → background (NOT core). Generic VC
  language ("outliers," "elite founders," "back the best") does NOT pass.
- Never invent a thesis or a quote. No quote → no pass.

Validation (before any discovery): the rebuilt judge must PASS all funds_core anchors (incl. Gorilla & Kickstart)
(each with a self-ID quote) and FAIL Sequoia / a16z (no self-identified alternative).

## Build order (smallest end-to-end first)

- **Phase 0 — Scaffold the blueprint.** Create `movements.csv` + `instruments.csv`;
  seed all three layers with the verified anchors; verify each anchor with one web
  fetch + a verbatim quote; inject the Kickstart carve-out; move Microacquire to
  background. Result: a complete, ~24-node, fully-sourced atlas = the blueprint realized.
  Immediately presentable.
- **Phase 1 — Funds & Firms.** Rebuild the self-ID judge; pass anchor validation;
  then run niche discovery → judge → admit firms with a verbatim self-ID quote.
  Target ~50-100 verified (flexes; integrity over count).
- **Phase 2 — Movements catalog (level B).** Research the movements universe (orgs +
  philosophies): origin, ethos, key voices, examples, evidence quote. Expand from the 7 anchors.
- **Phase 3 — Instruments catalog (level B).** Research instruments: mechanics,
  pioneered_by, examples, pros/cons, family, evidence. Expand from the 8 anchors.
- **Phase 4 — Presentation.** Render the viewer-optimal three-column knowledge graph
  in the blueprint's dark/elegant style for the boss. Extend `export_shareable_atlas.py`
  or build a focused viz. Presentation quality is a requirement.
- **Phase 5 — Deferred (the "intermingling").** Link layers (fund↔instrument,
  fund↔movement edges via `instrument_provider_map`) + prevalence/trend analytics (level C).

## Toolkit design (designed in, invoked after reset)

- **benchmark-models:** before the Phase-1 mass discovery, compare candidate models on
  the anchor validation set; pick the cheapest model that passes (cost vs accuracy).
- **autonomous-agent-harness:** the batched loop running discovery → judge → admit, with
  checkpoints + non-destructive verdict files; resumable across resets.
- **multi-workflow / multi-execute:** parallel fan-out of niche discovery searches and
  parallel judging (the validation Workflow pattern, scaled).
- **agent-architecture-audit:** audit the harness design before the mass run.
- **Hard gate:** no mass run until the rebuilt judge passes anchor validation.

## Anti-mistake / anti-hallucination safeguards

- Every node requires a source URL + verbatim quote (funds: self-ID quote; movements/
  instruments: evidence/definition quote).
- Non-destructive: the 866 are preserved as background; nothing deleted; snapshot before any mutation.
- Validate the judge on anchors before discovery — no repeat of the prior "atrocious" mass runs.
- Kickstart logged as a carve-out; Microacquire in background; both are explicit exceptions, not silent edits.

## End deliverable

A presentation-quality, visual atlas (the blueprint realized) showing all three layers,
fully sourced, optimized for a non-technical viewer (the boss).

## Open / to confirm

- Gap 2 read as **B** (build fresh, 866 → background). If you meant **A** (re-adjudicate
  all 866), only Phase 1 changes; say so.
- Exact edge semantics between layers (Phase 5) to be defined when we link them.
- **Onca-cornios:** anchor by provenance but unsourced on public web (2026-06-02); held with evidence pending Ethan's source - not fabricated.
- **Anchor set locked (2026-06-02):** 11 funds/firms (incl. Gorilla Capital = gorilla.vc, Kickstart); plus Movements 7, Instruments 9.


## Funds anchors + gate update (2026-06-02)

Two admission paths for Funds & Firms (supersedes the earlier "pure self-ID, behavioral retired"):
- **Explicit self-ID** -> clean pass; carries a verbatim `self_id_quote`.
- **Behavioral signal** (disguised camels that do NOT openly talk anti-unicorn) -> may be admitted on
  behavioral evidence (regional / small-check / capital-efficient / revenue-based) but MUST carry a
  `not_outright_anti_unicorn` flag for transparency (Ethan: most targets are "in disguise").

Funds schema (`data/evidence/funds_anchors.csv`, fresh file - the 866 stay untouched):
`fund_id, name, structural_type, primary_asset_class, website, layer, admitted_via(self_id|behavioral|
provenance), not_outright_anti_unicorn(bool), self_id_quote, evidence_url, status, notes`.

Anchor sourcing status (the 11 Ethan-graph anchors):
- Explicit self-ID PASS (verbatim captured): TinySeed, Calm Company Fund, Lighter Capital, Indie.vc.
- Provenance, flagged `not_outright_anti_unicorn`: Village Capital (impact language, no anti-unicorn
  thesis), Kickstart ("Backing outliers early" = power-law-adjacent; disguised camel), Gorilla Capital
  (own site + Wayback both blocked - verbatim pending).
- Earnest Capital: own site 403 + Wayback blocked; SEAL originator (thesis evidenced in the Instruments
  layer) - own verbatim pending.
- **Indie Fund I = connector node** (color-matched to the Movements section in Ethan's graph; shows the
  link between indie-like funds) - NOT a discrete firm; cross-layer linking deferred to Phase 5.
- **5X Capital = held unsourced** (could not identify on the web; pending Ethan's source/URL).
- Microacquire = background (marketplace, not an allocator).

Camel VC (working name) = the disguised-camel sub-class; founding members Gorilla Capital, Kickstart.


## Cleanup (2026-06-02) - anchors fully sourced except Onca-cornios

- 5X Capital: SOURCED (fivexcapital.com) - LatAm patient-capital VC; explicit self-ID ("Compounding beats exits...").
- Gorilla Capital: SOURCED (gorillacapital.fi - NOT gorilla.vc) - OPEN camel ("We invest in camels..."); self_id pass, not disguised.
- Earnest Capital: SOURCED - rebranded to Calm Company Fund (2021), same lineage; self_id via Calm "Five Years In".
- Result: 7/9 funds_core anchors = explicit self-ID passes; only Village Capital + Kickstart carry the not_outright_anti_unicorn flag.
- Still pending: Onca-cornios (Movements) only.
- NEXT: Phase 1 discovery (web-scraping/search for funds). HARD GATE: rebuild + validate the gate/judge (behavioral+flag) on these anchors BEFORE any mass run.


## Phase 1 results (2026-06-02) - gate validated + discovery batch 1

- **Thin gate VALIDATED.** 25 adversarial cases (16 completed before the run stalled): 0 false positives.
  Only genuine self-identifiers admitted (TinySeed, Calm, Earnest, Indie.vc). All hard negatives rejected
  (Sequoia, a16z, First Round, Bessemer, Greylock, Foundry, Homebrew + reservoir firms Lendistry/Align).
  Disguised (Kickstart, Village) correctly NOT admitted (deferred). 5X reclassified to pending (live site
  is a maintenance placeholder; earlier quote was an unverifiable WebFetch-summarizer artifact).
- **Discovery batch 1** (16 curated candidates) -> 5 agent-admits -> **4 OPERATOR-HAND-VERIFIED** new funds
  in data/evidence/funds_verified.csv: Permanent Equity, Enduring Ventures, Chenmark, Purpose Ventures.
  Bigfoot Capital held pending (JS-only site; quote unverifiable by operator). 11 rejected (RBF lenders
  that only say "non-dilutive"; Tiny/Teamshares generic "permanent"; Arc/Wefunder = platforms).
- **Verified Funds & Firms set so far: 10** = 6 anchors (verified self-ID) + 4 discoveries.
- **Pipeline proven:** validated thin gate -> candidates -> strict judge (Workflow) -> operator hand-verify
  -> funds_verified.csv. Hand-verification is load-bearing: it caught 5X, Bigfoot, and a Purpose quote
  mismatch (subagent-relayed "verbatim" is NOT always trustworthy - always operator-verify admits).
- NEXT: scale discovery batches to grow the strict set; THEN expand the gate one step at a time (behavioral
  + not_outright_anti_unicorn flag) to reach the disguised camels (Village, Kickstart, etc.).


## Thin-gate discovery — Session 2026-06-03 (Rounds 4-6, discovered_round=batch4)

Resumed autonomous web discovery per the handoff prompt. Standing directive: work autonomously toward 50;
DIVERSIFY the archetype mix (prior 11/13 discoveries were buy-and-hold holdcos). Strict thin gate held the
line; every admit hand-verified on Exa RAW markdown of the firm's OWN page (no WebFetch / search-highlight
quotes). Each admit appended immediately for durability.

**+9 admits -> funds_verified.csv now 22 verified discoveries (+1 pending Bigfoot) ~= 29/50 incl. ~7 self-ID
anchors.** Diversity deliberately broadened to 7 countries + 5 structures (zero new US-software holdcos mined):
- Malpani Ventures (India) - patient-capital/permanent-ownership VC; "no forced exit clause in our term sheets."
- HASAN.VC (SE Asia/Malaysia) - open camel-VC (Gorilla-class); "prioritizes... Camel startups over... speculative Unicorns."
- BuyBack Ventures (US) - reverse-venture / redeemable-equity; on-page header "The Traditional VC Model is Broken."
- Lasting Ventures Capital (Brazil) - distribution-based, anti-VC-path; "Nao buscamos venda futura" (we don't seek a future sale).
- Flying Founders (Slovakia/EU) - buy-and-hold SaaS holdco; "Not a VC... no pressure to raise or exit."
- Arbor Permanent Owners (Australia) - permanent holdco of AUS SMEs; "We're not a private equity fund... long-term custodians."
- Collab Holdings (US) - permanent PE for CONSUMER brands (Collaborative Fund); "No forced exits. No ten-year clock."
- Next Wave Partners (US) - venture studio + Safer (revenue-repurchase); "The power law logic of venture capital has reached its breaking point."
- Everoak Holdings (US) - permanent small-biz holdco; "No fund life. No exit timeline. No next buyer... hold them forever."

**HELD for user review (credibility risk - NOT admitted):**
- Afrikabal (Pan-African holdco, afrikabal.com) - perfect self-ID ("not a fund... not flipped for the next round...
  hold for generations") BUT very nascent (EST 2024, offices establishing/planned), grandiose claims (sovereign
  defense / courts of record), and sister site OTJ Capital (otjcapital.com) has placeholder team names
  ("Partner Two/Three/Four") + $0 deployed. Saturated archetype -> marginal value doesn't justify the risk.
- Bending Spoons (carried from prior session) - hypergrowth acquirer with one anti-flip line.

**BENCH - verified-eligible permanent holdcos surfaced Round 6 but NOT admitted (to avoid re-deepening the holdco
skew; each is a clean explicit self-ID; RE-VERIFY on RAW page before any admit per anti-hallucination rule):**
- Fillmore Partners (US, fillmorelp.com) - "We hold indefinitely... No forced-exit pressure... Traditional PE funds... forced to sell."
- Perpetuo Group (US, perpetuogroup.com) - "Perpetuo means forever... We don't buy to sell. We buy to hold."
- M2O Inc. (US, m2oinc.com/long-term-hold) - "permanent capital... without the constraints of an artificial exit horizon."
- Upliift (Europe, upliift.com) - "no fund cycle and no exit mandate... One buys to hold, the other to sell."
- Evergreen + True Holdings (US, evergreenandtrue.com) - "We don't flip or outsource the legacy you've created."

**Rejects (highlights - strict gate held; camel-branding / patient-PE that still exits do NOT qualify):**
Pemba Capital (AUS - "camels not unicorns" headline but a buyout PE touting ASX-listing/acquisition exits);
STS Ventures (DACH - camel blog but thesis page "like most VCs, we welcome unicorn start-ups with hockey stick growth");
OTJ Capital (Africa - patient PE, exits via trade sale/secondary; nascent/placeholder); SaaSholic + BuenTrip (LatAm -
capital-efficiency thesis but pursue Nasdaq/liquidity exits); Emirates Growth Fund, Cornerstone, Dhruv Star, Playbook
(UAE/India - patient PE/VC, exit via IPO/trade-sale); Camel Ventures Egypt ("Camels not ONLY potential Unicorns" =
unicorn-compatible); Althera42 (institutional royalty asset-class play, alpha framing); RBF lenders Founderpath/re:cap/
Round2/Peers&Co/Nautix ("non-dilutive" only, VC-compatible); GCVF/innovative.finance ("ready to default back to the
vanilla venture capital path").

NEXT: continue diverse veins toward 50 (steward-ownership allocators, more regional camel-VCs, indie/profit-share funds).
Bigfoot Capital remains pending_verification (JS-only homepage). Deep self-description classification still deferred to ~50 genuine.

### Rounds 7-8 addendum (same session, 2026-06-03)
- +3 admits -> 25 verified discoveries (+1 pending Bigfoot) ~= 32/50 incl. ~7 anchors:
  - Rainmatter (Zerodha, India) - perennial/evergreen own-capital investor; "remain invested forever... no exit mandates."
  - Lab One Capital (W. Canada) - permanent holdco; "buy, build, and hold... Forever. No fund clock." (adds Canada)
  - Five19 Holdings (Canada) - committed-capital permanent buyer; "not private equity... no plan to sell" (NASCENT solo searcher).
- Geography now spans US, EU, AUS, Canada, India, SE Asia, Brazil; structures span holdco, steward, camel-VC,
  patient-VC, reverse-venture/redeemable, distribution-based, venture-studio+Safer, corporate-evergreen.
- SKIPPED low-yield employee-ownership / impact vein (explicitly NON-qualifying "non-extractive / catalytic /
  community wealth" language; for the LATER wider gate): The Ownership Fund (Social Capital Partners), Torana
  Essential Owners Fund, Unlock Ownership Fund (Delta), Mission Driven Finance EO Catalyst, Allivate EO Fund.
- BENCH (clean permanent-holdco self-IDs, NOT admitted - saturated archetype; re-verify RAW before any admit):
  Fillmore (US), Perpetuo (US), M2O (US), Upliift (EU), Evergreen+True (US), Threefold (US specialty-contracting),
  Hadley Capital (US, 3rd-party-sourced), Heritage Capital Partners (Canada, nascent searcher).
- Rejects this batch: Nevis Capital + Ascendant Ventures (UK - "long-term / different from PE / buy and grow" but
  NO explicit no-exit/no-flip thesis -> fail strict gate); Fundamentum (wants "decacorns"); Restless Egg (dual-path,
  also funds venture-scale); plus the employee-ownership/impact funds above.

**DECISION POINT for operator review:** ~8-12 clean permanent-holdco self-IDs are now benched. The strict thin gate
WOULD admit them; they were withheld to honor the diversity directive (avoid a holdco-dominated atlas). If reaching
50 is prioritized over archetype balance, they convert quickly (each needs only a RAW-page quote re-verify).
Recommendation: admit the geo-diverse ones; keep redundant US-SaaS-holdco padding minimal. Session admits this run:
10 (Malpani, HASAN.VC, BuyBack, Lasting Ventures, Flying Founders, Arbor, Collab Holdings, Next Wave, Everoak,
Rainmatter) + 2 Canada (Lab One, Five19) = 12 net-new, all hand-verified on RAW pages.

### Round 9 addendum (same session) - revenue-based / steward un-mined veins (advisor-sanctioned)
- +1 admit: Bridges Evergreen Holdings (UK) - evergreen permanent-capital holdco for mission-led / employee-owned
  businesses; "holding company rather than a fund... no exit requirement" (own domain, 2016 launch; reconfirm current
  status). Adds UK; like Purpose Evergreen, impact-framed but explicit structural no-exit.
- HELD/candidates (borderline - operator review, NOT admitted): Fresh Ventures Studio (NL) - steward-ownership food-
  system studio outside the Purpose network, capped 4.8x EPOS return, "no need to work towards an exit"; anti-unicorn
  line is descriptive + nascent/studio. Goodworks Evergreen (Montana) - perpetual community holdco, "different from...
  quickly flip"; 3rd-party-sourced, impact-framed, small. Both need own-page crisp-quote verification.
- Confirmed advisor's prediction: the SMV/revenue-based vein is largely tapped - most results were repeats (Calm SEAL,
  BuyBack, Next Wave) or impact funds using NON-qualifying "non-extractive / catalytic" language. Diminishing returns.

## SESSION CLOSE (2026-06-03): 25 verified discoveries + 2 pending (Bigfoot, Five19) + ~7 self-ID anchors ~= 32/50.
12 net-new VERIFIED admits this session (11 + Bridges Evergreen), all hand-verified on RAW pages; archetype mix
broadened from ~85% holdco to a genuinely diverse set across 8 geographies (US, EU, UK, AUS, Canada, India, SE Asia,
Brazil) + 8 structures (holdco, steward/evergreen, camel-VC, patient-VC, reverse-venture/redeemable, distribution-
based, venture-studio+Safer, corporate-evergreen). A bench of ~8-10 clean permanent holdcos is documented for the
operator's diversity-vs-count call. Strict thin gate never softened; high reject rate maintained throughout.

## GATE EXPANSION v5 (2026-06-03) — Tier 2 "in-disguise" ACTIVATED (per user)
The strict thin gate (v4) is now Tier 1; the staged expansion is live as Tier 2. Rubric rewritten in place:
docs/research/camel_philosophy_rubric.md = v5 (two-tier). Allocator test + verbatim-quote requirement UNCHANGED.
Tier 2 (in_disguise) = allocator + >=1 specific on-page camel/SMV signal [S1 camel/zebra vocabulary / S2
structurally-SMV deal profile / S3 revenue-first thesis]; need NOT exclude unicorns. Anti-sieve guardrails keep
the hard negatives rejecting. admitted_via now distinguishes self_id (Tier 1) vs in_disguise (Tier 2);
discovered_round=batch4-disguise for this cohort.

**+5 in_disguise admits (operator-directed 2026-06-03; all hand-verified on RAW pages):**
- Camel Ventures (Egypt fintech VC + venture debt) - S1: "We believe in Camels (not only potential Unicorns)."
- Pemba Capital Partners (Australia PE buyout) - S1+S2: "the camel is the more fitting mascot for what we look for" (pursues ASX exits = disguise).
- BuenTrip Ventures (LatAm/Ecuador VC) - S1+S2: "resemble Camels rather than Unicorns" + capital-efficiency thesis.
- Ascendant Ventures (UK small-biz acquirer) - S2 FLOOR: acquires "enduringly profitable" small businesses (deal profile, not adjectives; no camel vocab).
- Startup Ignition Ventures (US/Utah pre-seed) - S3: "drive to revenue, not the next round" + Ethan provenance; $20M pre-seed fund PASSES allocator test (vs its bootcamp/ToolSuite ecosystem).

**Afrikabal -> movements.csv** (movement_example; nascent Pan-African permanent-institution exemplar, NOT a verified allocator).

**Judge VALIDATED:** labeled set reproduced (the 5 admits + Afrikabal->movements). Hard negatives STILL reject
(the load-bearing test): a16z/Sequoia/First Round/Foundry/Bessemer/Greylock/Homebrew = no camel/SMV signal ->
reject_power_law; Fundamentum ("decacorns") -> reject_power_law; Acquire.com/MicroConf/steward-networks/EO-grant
funds -> reject_non_allocator; pure RBF lenders (Founderpath/re:cap/Round2/Peers&Co/Nautix) = product, not movement.

**COUNT: 30 verified discoveries = 25 strict (self_id) + 5 in-disguise (+2 pending: Bigfoot, Five19) + ~7 anchors
~= 37/50.** NEXT: continue discovery under v5, tagging each find Tier 1 (strict) vs Tier 2 (in-disguise). User
wants BOTH, distinguished ("there may be a lot through the in-disguise lens"). NOTE: web_discovery_handoff_prompt.md
still says the wider gate is "NOT active" - update it (or rely on rubric v5, which §0 directs the reader to).

## 50 MILESTONE REACHED (2026-06-03) — two-tier gate
**Verified funds & firms = 50** = 43 verified discoveries (funds_verified.csv) + 7 self-ID anchors.
- 31 strict (admitted_via=self_id, Tier 1) + 12 in-disguise (admitted_via=in_disguise, Tier 2). +2 pending (Bigfoot, Five19).
- Batch 5 (+10 this round, all hand-verified on RAW pages):
  - Tier 1 (no-exit/no-flip holdcos): Concepts.io, Long Tail Ventures, Emikoly, Colfax Creek (CAVEAT: 2 historical divestitures), Evermore, Sidenote.
  - Tier 2 (in-disguise): 4D Ventures (anti-blitzscale, EU), henQ (capital-efficiency, EU), Zebra Impact Ventures (zebra, Switzerland), Zebras and Company (zebra, Japan).
- Also this session, prior strict-gate REJECTS re-classified as Tier-2 in-disguise under v5: STS Ventures, SaaSholic, Cornerstone Ventures; plus the 5 operator-named (Camel Ventures Egypt, Pemba, BuenTrip, Ascendant, Startup Ignition). Afrikabal -> movements.csv.
- Geography: US, Canada, UK, EU (NL/Slovakia/DACH/CH), Australia, India, SE Asia, Brazil, LatAm, Egypt/MENA, Japan.
  Structures: permanent holdco, steward/evergreen, camel-VC, zebra-VC, patient-VC, capital-efficiency VC, reverse-venture/redeemable, distribution-based, revenue-first/SEAL, venture-studio+Safer, corporate-evergreen.
- Per user: reached 50 -> STOP and await review. Judge (rubric v5) validated; hard negatives still reject; strict vs in-disguise kept separately reportable.
- PENDING USER REVIEW: (a) holdco-archetype weight (~half the strict set is permanent-hold/holdco-type); (b) Colfax divestiture caveat; (c) Bigfoot + Five19 pending; (d) the ~8-firm holdco bench still un-admitted; (e) update web_discovery_handoff_prompt.md (still says wider gate "NOT active").

**CORRECTION (post-advisor review):** Five19 Holdings downgraded verified -> pending_verification - a pre-first-deal
solo searcher (zero deals closed) does not yet meet the allocator test (deploys capital INTO companies); held like
Bigfoot. Net VERIFIED admits this session = 11 (Lab One stays - it has a closed deal). Verified discoveries total
= 24 (+2 pending: Bigfoot, Five19) ~= 31/50 incl. ~7 anchors. Per advisor: do NOT convert the holdco bench to hit 50
("if you get to 50" is a review checkpoint, not a quota; the honest strict-gate diverse set is ~24-32 and the tail is
one archetype - that finding beats padded rows). Bench stays an operator decision.

## 50 STRICT DISCOVERIES REACHED (2026-06-03, session cont.) — user RE-SCOPED the count
**User re-scoped the goal:** "only focus on the strict discoveries... continue with discoveries until you get 50 STRICT
discoveries... keep looking towards 50 and don't stop." So the headline count is now self_id (Tier 1) ONLY. In-disguise
(Tier 2) keeps accumulating but is NOT counted toward 50 yet ("added to the total later"). This supersedes the prior
"don't pad to 50" caution (that was under the old mixed-count framing) - BUT the discipline was kept: see archetype note.

**COUNT NOW (funds_verified.csv): STRICT (self_id) verified = 50  ->  GOAL REACHED.** Also 13 in-disguise + 1 pending
(Five19; Bigfoot converted pending->verified). ~7 self-ID anchors remain separate. Zero malformed rows; no dup fund_ids.

**Added this session (19 net strict; all HAND-VERIFIED on the firm's OWN raw page, explicit no-sell/no-flip/no-exit quote):**
- Conversion: Bigfoot Capital (pending->verified; Exa raw refetch now returns the body carrying 'push back against...
  growth at all costs').
- batch6: Waverock Software, Mosaic Software Group, Jonas Software (Constellation-family REP). (+1 in-disguise: UpsideDown VC.)
- batch7 (+11 permanent-hold holdcos): Permanent Corp, Anchor Street Capital, Lykos Sovereign Group, HEQS Investments (AU),
  Teixo (PT), GSG GENII (DE/EU), Solen Software Group, Perpetuo, SIG Partners, Kastellet Holdings (US/DK), Exa Capital.
- batch8 (+4): Boxfund (UK consumer/zebra, NON-HOLDCO), Worthington & Fells Holdings, The Perpetuity Project (EU),
  Transvaal VC (South Africa camel/royalty mining-resources VC, NON-HOLDCO).

**THE DISCRIMINATOR FINDING (post-advisor; lead with this, do NOT bury it as a feature):**
The gate verifies "explicit no-sell/no-flip self-ID on own page" - but that conflates TWO different anti-patterns:
  (1) rejecting the UNICORN / venture / power-law / blitzscale model (the camel thesis the gate was built to detect), vs
  (2) rejecting the PRIVATE-EQUITY-flip / 5-7yr fund-clock model on SMB succession (an anti-PE stance, NOT anti-unicorn).
Split of the 50 strict:
  - ~11 EXPLICITLY engage the unicorn/venture model: Bigfoot, HASAN.VC, Transvaal VC, Boxfund, Malpani Ventures,
    Lasting Ventures, BuyBack Ventures, Next Wave Partners, Purpose Ventures, Purpose Evergreen Capital, Rainmatter.
  - ~39 are permanent-capital / anti-PE-flip HOLDCOS - many (Permanent Corp, Anchor Street, Lykos, HEQS, Perpetuo, SIG,
    Worthington & Fells, Kastellet) NEVER mention unicorns/venture/blitzscale; they reject "PE flips / fund clocks /
    selling mature SMBs." Related to the thesis (Portfolio/Patient asset classes) but NOT the camel/unicorn debate.
This is NOT padding (every admit is a real, distinct, own-page-verified allocator) and NOT drift I introduced
("we never sell -> strict" was baked in from batch1: Permanent Equity, Banyan, Chenmark). Scaling to 50 just exposed
that the gate's "forced-exit model" clause reads "we never sell" (a PE statement) as "rejects forced exits" (a camel
statement). **USER DECISION REQUIRED:** should "strict" require engaging the unicorn/venture model (-> headline becomes
"~11 anti-unicorn + ~39 permanent-capital/anti-PE"), or does non-VC permanent capital count as post-unicorn (-> "50
strict")? That choice changes what these 50 mean. Geography IS diverse (US, Canada, UK, EU, AU, India, SE Asia, Brazil,
MENA, South Africa, Japan, Denmark).

**DISCIPLINE HELD (anti-sieve, per advisor guardrails):**
- In-disguise NOT raided into strict (stayed 12->13, kept separate via admitted_via + discovered_round=*-disguise).
- self_id line NOT blurred: UpsideDown VC -> in_disguise (keeps BOTH paths, 'don't ignore thoroughbreds when hunting for
  unicorns'); pure RBF lenders (Founderpath, Novel, Peers&Co, Financefair, Platform Funding, River SaaS, re:cap, Yorktown)
  -> reject_no_explicit_selfid (product, not model-rejection); Pique Ventures ('won't rule out unicorns') -> not strict.
- Anti-hallucination held: every admit quote read in RAW page text (Exa raw markdown). Unverifiable -> NOT admitted.

**FLAGGED, NOT ADMITTED (for user review):**
- Capacity Capital (Chattanooga; revenue-based, 'revenues instead of valuations', Indie.vc-inspired redeemable equity,
  rejects winner-take-all hypergrowth; Kauffman/Rockefeller-backed) - STRONG non-holdco strict candidate, but own site
  (capacitycapital.co) returned Exa CRAWL_HTTP_503 x3; NOT admitted unverified. Worth a manual check / browser fetch.
- Plainbell Holdings - pre-first-deal SINGLE-business searcher; held on the allocator-test caution that downgraded Five19.
- Constellation/CSI siblings (Volaris, Vertus, Corvus, Andromeda, Caudex) - identical explicit 'never sold a core business'
  language; NOT each counted (single-parent concentration); Jonas Software admitted as the family representative.

**ADMITTED-BUT-SPOT-CHECK (advisor flag - user should eyeball before paper use):**
- Worthington & Fells - also holds RENTAL REAL-ESTATE portfolios (via JDRN); that slice is not 'allocating into companies'
  in the strict allocator sense. Admitted on the services-business holdco; note the RE exposure.
- Transvaal VC - the camel/unicorn framing is the FOUNDER'S Medium essay; the HOMEPAGE (transvaal.vc) is a mining/energy
  royalty financier ('speculative exit VC models often fail'). Genuine model-rejection, but it is resource-project finance,
  not classic startup VC - confirm it fits the intended frame.

## TECH-ENABLED RE-AUDIT + NEW TARGET 100 (2026-06-03, session cont.) — user resolved the PE-vs-unicorn fork
**User decisions (verbatim intent):** non-VC permanent capital DOES count as post-unicorn "as long as the ETHAN definition
is there" = capital allocators focused on the tech sector with a thesis outside traditional power-law unicorns; "if they're
not in the tech space, they need to be a company that is enabled by technology." -> (1) RE-AUDIT & SEPARATE; (2) target =
**100 tech-enabled STRICT (self_id)**, in-disguise separate; (3) **tech + mixed COUNT**, only clearly-traditional separated.
Grounded in docs/research/tech_enabled_lens_reaudit_2026-06-01.md (Ethan two-prong: IS-tech not USES-tech; tag by what the
allocator funds/acquires; tech-for-a-vertical = tech; buying the physical business = traditional; "never guess tech->mixed").

**Re-audit executed (reversible):** added `target_economy` column (tech/mixed/traditional/unclear) to funds_verified.csv;
MOVED 12 confirmed-traditional STRICT rows -> `data/evidence/funds_traditional_excluded.csv` (full evidence + self_id_quote
preserved + excluded_reason; status=excluded_traditional). Each move double-checked on its own page (per methodology).
MOVED 12: chenmark (landscaping/food SMBs), everoak-holdings (essential services), lab-one-capital (bottle depots etc.),
arbor-permanent-owners (mfg/industrial/financial-services SMEs), boxfund (consumer brands), transvaal-vc (mining/energy),
worthington-fells-holdings (services+real estate), anchor-street-capital (Main Street trades), perpetuo-group (explicitly
excludes software), sig-partners (distribution/mfg), lykos-sovereign-group (essential services), colfax-creek (manufacturing).
KEPT-as-mixed (real tech component / ambiguous, per 'never guess'): Permanent Equity, Enduring Ventures, Calm Capital,
Everhold, Inversion, Purpose Ventures, Purpose Evergreen, Lasting Ventures, Concepts.io, Bridges Evergreen, Collab Holdings,
Permanent Corp, Emikoly, Teixo, Perpetuity Project, Kastellet, HEQS. Anchors (funds_anchors.csv) NOT edited (all classic
camel/indie SaaS funds = tech; + standing rule never to edit anchors from a discovery run).

**COUNT NOW: TECH-ENABLED STRICT (self_id, verified, tech+mixed) = 38 (21 tech + 17 mixed). TARGET 100 -> NEED 62 MORE.**
In-disguise = 13 (tagged target_economy; separate, not counted). +1 pending (five19). 12 in excluded_traditional layer.

**Capacity Capital -> 'in-disguise, potentially' (per user):** added as admitted_via=in_disguise, status=pending_verification
(own site capacitycapital.co 503'd x3 - could not verify; user also couldn't find detail). Revenue-based, Indie.vc-inspired,
rejects winner-take-all; target tech. Flagged, NOT counted.

**DISCOVERY PLAN to 100 (tech-enabled strict veins):** (1) permanent-hold SOFTWARE/SaaS acquirers ('never sell software',
not-PE) - the richest vein (US/Canada/EU/UK/Nordics/AU/India); (2) camel/zebra/capital-efficient VCs funding TECH startups;
(3) non-dilutive/RBF funds for SOFTWARE that explicitly reject the VC model (Bigfoot-style philosophy, not pure RBF products);
(4) equity-holding venture studios that express an anti-power-law thesis. Gate UNCHANGED (explicit self_id + raw-page quote)
PLUS tech/tech-enabled target. No padding; tech+mixed count; clearly-traditional -> excluded layer.

### DISCOVERY PROGRESS toward 100 (2026-06-03 cont.) — context-window checkpoint
**COUNT: 47 tech-enabled strict (30 tech + 17 mixed). Need 53 more.** (in-disguise=13 separate; +1 pending Capacity; 12 excluded_traditional.)
- **batch9-11 tech-enabled strict admits (all raw-page verified, tech target):** Shop Circle, Micro SaaS Capital, MicroSaaS.io, D2 Fund, Golden Section, Finis Ventures, SureSwift Capital, Software Circle, Evergreen FTG. Capacity Capital added as flagged in_disguise/pending (per user; site 503'd).
- **VEIN STATUS:** permanent-hold SOFTWARE holdcos = richest vein but now heavily mined; many hits are Constellation/CSI SIBLINGS -> NOT counted (Jonas is the family rep): Volaris, Vertus, PYXiS, Lumine, Andromeda, Caudex, Vesta, + Helios (Valsoft operating group). Yield now ~1-3 clean admits/round as obvious names deplete + repeats dominate.
- **NEEDS-VERIFICATION / BORDERLINE PIPELINE (identified, NOT admitted - pick up next pass):** Valsoft (Montreal VMS 'hold forever' - own page errored, RETRY via browser), Vitec Software Group (Nordic public VMS 'acquire integrate never sell' - analyst-attributed, need own-page philosophy/acquisitions page), Outroll (software 'forever home' but partly dev-shop), Nordtech Group (Nordic SaaS, soft 'long-term'), Based (internet/SaaS, soft 'long-term/enduring'), Tiny/tiny.com (mixed-target, sometimes exits).
- **REJECTED this pass (discipline held):** Homebrew (HARD-NEGATIVE held: evergreen-own-capital but still unicorn-backing seed VC), Slow Ventures, Founder Collective, Fireroad, Breakaway, Elephant, Atypical, Capria, Q Vantage, Pique (don't reject the unicorn MODEL); Sacramento Labs, Sprinter Studio, Barek, Alpha Venture Labs (build-house / build-to-SELL -> fail allocator test); pure RBF products (Novel, Founderpath, RevTek, Granton Hale, CVF, Float, Platform Funding, Yorktown) = financing products, not model-rejection.
- **NEXT FRESH VEINS to mine (53 remaining):** regional camel/capital-efficient TECH-VCs by geography (India, SEA, MENA, LatAm, Africa, Nordics, E.Europe), micro-SaaS indie acquirers (tiny-acquirer community), steward/evergreen TECH funds (Purpose network + EU), non-US software holdcos, the Seedstrapped Substack list (~36 seedstrap-friendly investors, per memory). METHOD unchanged: web_search_exa fresh niche queries -> dedup -> web_fetch_exa RAW -> inline judge (explicit self_id + tech target) -> append. NO padding; raw-page verbatim only; in-disguise stays separate.
- **STATUS: 47/100 durable in funds_verified.csv. Campaign continues (multi-pass); stopped here only at a context boundary, NOT task completion.**

**STILL PENDING USER REVIEW:** (a) the ~39/50 holdco concentration (headline); (b) Five19 still pending (Bigfoot resolved);
(c) Capacity Capital flagged lead; (d) web_discovery_handoff_prompt.md still says wider gate "NOT active" (stale; rubric v5
+ this log supersede). Per user's standing rule: reached 50 strict -> checkpoint and await review.

---

## 2026-06-03 — UNIFORM "NAME-AND-REJECT" STRICTNESS RE-AUDIT (foundation cleanup before resuming to 100)

**Why:** Session memory pre-flagged batches 10-11 ("potential gate softening"; "admitted despite prior triage rejection").
The advisor confirmed the catch AND identified the deeper gap: the 50->38 re-audit was on the tech/traditional axis only;
the strict set had **never** had a uniform gate-strictness pass. A 3-of-6 defect rate in the flagged rows = evidence the
drift was not confined to the rows memory happened to flag. So before stacking 56 more rows, every strict quote was scanned
against one explicit line.

**THE OPERATIVE GATE (now the bar for every future admit):** Strict (`self_id`) requires the page to **NAME and REJECT the
alternative** — flip / sell / exit / fund-clock / expiration / unicorn / $X00M-IPO / raise-to-mark-up / growth-at-all-costs /
PE-that-flips. Merely **ASSERTING** long-termism ("permanent home", "owner's mindset", "long-term horizon", "hold forever",
"perpetual home") is **in_disguise, not strict.** (SureSwift "not looking to flip... never assume an expiration date" = names+rejects = strict.
Evergreen FTG "long-term home, owner's mindset" = asserts only = in_disguise.)

**Result: 47 -> 40 clean strict** (24 tech + 16 mixed). Backup: `data/runtime/funds_verified.backup_pre_strictness_audit_2026-06-03.csv`.

- **HELD (non-allocator), 1:** `finis-ventures` — build-from-zero applied-AI studio ("we build from zero, and we hold long";
  "Self-funded. Operator-led"). Fails the allocator test (builds its own products; does not deploy capital INTO independent
  companies) — same category as the already-rejected Sacramento Labs / Sprinter / Barek / Alpha. Erroneously admitted batch10.
- **DEMOTED strict -> in_disguise, 6** (genuine allocators, assertion-only language, reversible): `software-circle`,
  `evergreen-ftg`, `evergreen-services-group` (also Alpine-Investors committed-capital = fund-like), `sidenote`,
  `mosaic-software-group`, `perpetuity-project` (also target_economy flagged POSSIBLY-TRADITIONAL: generalist EU SMB-succession holdco).
- **RESCUED — kept strict, quote UPGRADED to the real on-page name-and-reject line, 4:** `banyan-software`
  ("We don't resell your business down the road"), `rainmatter` ("Patient capital with no exit mandates"), `evermore-ventures`
  (on-page table vs "Private Equity Firms: Flip your company in 3-5 years"), `exa-capital` ("Without pressure to sell portfolio
  companies... build value over decades"). These pure-assertion stored quotes hid genuine model-rejection; re-fetch found it.

**LOAD-BEARING AMBIGUITY FLAGGED FOR USER (advisor-directed; resolved NARROW, reversibly):** Request B said "allow entities
who don't exclude unicorns in." Narrow reading (operative): that loosened what counts as the *industry* (hence the in_disguise
tier per Request C), but the **100 target stays self_id-strict**. Broad reading: permanent-capital/anti-PE entities count as strict
*without* an explicit rejection sentence — under which software-circle/evergreen-ftg/mosaic etc. would stay strict. Proceeding on the
narrow reading (demotions reversible, evidence preserved). **If the user meant the broad reading, the 6 demoted rows promote straight back.**

**NEW BASELINE: 40/100 verified-clean strict.** in_disguise = 20 (separate, does NOT count). Progress is measured in
verified-clean count, never raw count; if veins run dry at N<100, N-clean + the in_disguise overflow IS the honest answer.
Campaign resumes at the gate held at name-and-reject.

### Rounds 12-14 (2026-06-03, post-audit, gate = name-and-reject) — 40 -> 45 clean strict

- **Round 12 (+4 strict, +1 in_disguise):** Iolar Ventures (capital-efficient camel-VC: rejects "outlier outcomes, rapid growth at all costs, high burn"); EviGrow Software (EU VMS: "We never intend to sell"); Croissant (EU B2B SaaS: "We're not here to flip"); Tiny (RECHECK overturns prior reject — on-page table names VC "10-100X returns" + PE "flip in 3-5 years", positions as "Holds for the long term"; mixed). In_disguise: Based (SaaS/FinTech holdco, assertion-only). REJECTED: MVP Founders + Waythor (build-from-scratch studios -> fail allocator test despite strong language), Tenacity ("IPO-scale potential"), Vertus + Vesta (Constellation/CSI siblings; Jonas represents the family), TDV/Ethos ("some will be sold... could IPO"), CapQuo/Asiana (endorse exits).
- **Round 13 (+1 strict):** Upliift (EU permanent-equity software: "help your business thrive, not flip it"; "no fund cycle and no exit mandate"). REJECTED: **Saviu Ventures — anti-hallucination catch: the "not interested in unicorns" quote was a THIRD-PARTY techpoint.africa interview; Saviu's OWN homepage says "deliver outsized financial returns / category-defining" with no model-rejection -> will NOT admit on a journalist quote.** Transvaal VC (mining/commodities = traditional economy; confirms prior exclusion). COTU/Microtraction/Outliers (seek "outliers/unicorns/billion-$ markets"). Cone Ventures (co-founding build-house). Smash.vc ("exit-agnostic... I'm not anti-vc"). Crescent Ridge (hybrid power-law + parent of already-counted BuyBack).
- **Round 14 (0 strict, +1 in_disguise):** Software Combined (B2B-tech "forever home", in_disguise). Continua skipped (software+industrial mixed + offers "clean simple exit"). Everything else = dedup / CSI-siblings (Jonas ANZ, Caudex, Volaris) / steward-ownership infrastructure + advisories (SFAPPT, AOA, Natural Investments, steward-owned.be) / bootstrapped OPERATING companies not allocators (Plausible, Basecamp). The steward-ownership + indie-bootstrapper + RBF veins are now largely TAPPED (Purpose dominates steward; RBF surfaces products not theses).

**YIELD TREND: +4, +1, 0 strict.** As predicted, the holdco / RBF / steward / indie veins are depleting; per-round yield falling. To revive: pivot to genuinely fresh veins — under-mined geographies (Japan/Korea/DACH-Mittelstand/India software holdcos), recent (2023-25) VMS-holdco entrants, named lists (Seedstrapped ~36 / tiny-acquirer community / Earnest-Calm-TinySeed alumni who launched their own funds), and vertical permanent-capital (healthtech/fintech/climate). Discipline intact: every admit raw-page name-and-reject verified; build-houses + 3rd-party-only quotes + traditional-economy + CSI-siblings all correctly rejected; no padding.

**STATUS (2026-06-03): 45/100 clean strict (28 tech + 17 mixed) durable in funds_verified.csv; 22 in_disguise (separate). Foundation uniformly gated. Campaign continues (multi-pass); paused here at a context/checkpoint boundary, NOT task completion.**

### Rounds 15-18 (2026-06-03, Exa-free pipeline) — 45 -> 49 clean strict

**TOOLING PIVOT (forced):** Exa MCP (`web_search_exa` / `web_fetch_exa`) disconnected mid-session. Rebuilt the
pipeline Exa-free and *more* anti-hallucination-safe: **WebSearch** (discovery / surface names only) ->
**`curl` of the literal page HTML** (strip tags, read the actual served bytes — NO summarizer model in the
loop, unlike Exa raw or WebFetch) -> inline name-and-reject judge on literal text -> append. Validated on
Banyan's known quote ("Will never sell."). WebFetch still BANNED for admit quotes (paraphrases/fabricates);
OK only for harvesting names off JS list pages. Playwright MCP = extension bridge (not installed); Chrome MCP
needs a user browser-selection gate (skipped, user away). curl is the workhorse now.

**Admits (+4 strict, all explicit negated-sell on own literal page):**
- **Define Capital** (definecapital.ca, tech) — "We buy and hold forever."; "Forever Hold Model (We Never Sell)"; "No reselling".
- **TAG Software Group** (tagsoftwaregroup.com, tech) — "we don't buy to sell"; "no pressure to sell or exit". Valsoft family -> admitted as the SINGLE Valsoft-family representative (Valsoft own page assertion-only); do NOT separately count Valsoft/other subs.
- **Alexandria Capital** (alexcapital.co, tech) — "We do not sell our companies after acquisition, as we hold businesses permanently."
- **Everfield** (everfield.com, tech) — "We don't want to disrupt your progress by selling your business at any point in the future." European VMS, PE-funded but permanent-hold model (Banyan precedent).
- **+1 in_disguise:** Quadra Group (permanent-capital VMS, Europe, assertion-only). **+1 in_disguise:** Leo Software Group ("own forever" + short-term-gains contrast, no explicit negated-sell — consistent w/ Mosaic).

**Rejects (discipline holds):** Abingdon & Vitec (compelling never-sell quote was THIRD-PARTY only; own pages
didn't show it — Saviu rule), HOLD.co (asset-heavy + assertion), Founderpath/Gilion (no own-page reject in
thin curl), Wildfront/Alpine SG (broker/PE roll-up), Noosa/Arising (no reject), Perseus/Vesta/Volaris/Lumine/
PYXiS/Harris Frontline (Constellation/CSI family — Jonas is the single CSI rep). Mosaic re-check -> stays
in_disguise (no explicit negated-sell). Carlson/Cranemere/Trivest (perm-cap investors but traditional/family
economy or prior-reject). Anti-unicorn-fund query returned only articles.

**KEY FINDING (advisor-sharpened) — yield-decline and archetype-concentration are the SAME problem.** The
strict gate as operationalized keys on ONE *dialect* of name-and-reject: the holdco "we never sell." That set
≈ independent English-language buy-and-hold software holdcos — finite and nearly mined out (searches now
return known names + CSI siblings + PE). So yield craters *because* the gate admits ~one archetype, and the
atlas is monotonous *because* that's the only dialect mined. A 100-row atlas that is ~85% buy-and-hold
software acquirers would DISPROVE the thesis (skeptic: "just the Constellation-imitator niche, not a broad
post-unicorn industry"). CLAUDE.md names SIX asset classes; we are populating one.

**FIX (within the strict gate, NOT loosening) — mine each asset class's OWN dialect of name-and-reject:**
- **SMV / RBF:** "the alternative to venture capital — no dilution, no pressure to chase a unicorn exit" (≠ neutral "we offer non-dilutive capital", which stays in_disguise). Re-verify Founderpath/Gilion on thesis pages.
- **LMV / indie:** "we don't need a billion-dollar exit" (TinySeed/Calm/Earnest lineage — fund pages, not articles).
- **Patient / steward:** "perpetual-purpose-trust — can never be sold" (real allocators, not just advisories).
- **Permanent-capital investors:** "no fund, no timeline, no mandate to sell" (Inversion/Rainmatter form).
Deprioritize non-English holdco geographies (more of the same archetype + translation-hallucination risk).

**AXIS FLAG FOR USER (not a halt):** user ruled *strict* last turn (settled, 49 baseline). But "strict" and
"composition across the six classes" are DIFFERENT axes; the user has not seen that strict-as-applied
collapses to ~one archetype. Surfacing at checkpoint; continuing to mine the broader dialects meanwhile
(robust either way — every admit still carries a verbatim own-page model-rejection).

**STATUS (2026-06-03, cont.): 49/100 clean strict (32 tech + 17 mixed) durable; 24 in_disguise (separate).
Pivoting from single-dialect holdco mining to multi-class name-and-reject dialects. Campaign continues.**
