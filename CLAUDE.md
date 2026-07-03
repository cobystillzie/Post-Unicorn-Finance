# CLAUDE.md — Post-Unicorn Finance (operational source of truth)

This is the single "heart of the project" file. Read it first. The README is the human-facing repo
description; this file is how the atlas is actually built, what the gates are, and the traps to avoid.

## Mission

Prove **Post-Unicorn Finance** is a real emerging industry: a source-backed atlas of capital allocators
operating OUTSIDE classic unicorn venture capital. We are pioneering the category, so **classification
credibility is everything** — a junky or miscategorized row is worse than a missing one.

## Asset classes (entity `primary_asset_class`)

Auto-promotable non-unicorn buckets: **SMV** (Strategic Middle Ventures / revenue-based + non-dilutive growth),
**Patient Capital** (permanent equity, evergreen, steward-ownership, family offices, mission/impact long-hold),
**LMV** (solo-GP / micro / indie funds, accelerators, fellowships), **Search/ETA** (search funds, ETA,
independent/fundless sponsors), **Portfolio Capital** (VMS serial acquirers, holdcos, studios, roll-ups),
**Sovereign Capital** (sovereign wealth, public investment banks, DFIs, catalytic/blended/climate finance).
**UVC** (classic unicorn VC) is the baseline we contrast against and is **never auto-promoted**.

## Data model — atlas.csv is the authority (updated 2026-07-02)

- **`data/evidence/atlas.csv` is the authoritative atlas** (149 entities, Schema B). Columns:
  `entity_id, name, asset_class, liquidity_band, horizon_years, tech_enabled, tier, confidence,
  website, exit_quote, audit_flag, source_note`. Log every manual row change to
  `data/evidence/manual_changes_*.log`.
- **`data/evidence/industry_entities.csv` is DELETED (2026-07-01)** — legacy 890-row, PE-bloated,
  pre-audit corpus. Backups: `data/runtime/backup_2026-07-01/`, `backup_2026-07-02/`, `backup_2026-07-02b/`,
  `backup_2026-07-02c/`. Any doc/script still calling it "the atlas" is stale — ignore that claim.
- `data/atlas.sqlite` is a rebuildable legacy cache (gitignored); the other `data/evidence/*.csv` files
  (claims, source registry, intake queue) are supporting evidence layers, not the atlas itself.

## Pipeline (how a lead becomes an entity)

1. **Inject** curated leads → `entity_intake_queue.csv` (`review_status=queued`). Use
   `scripts/inject_and_promote.py <firms.json> <round_tag>` — it injects (dedup vs existing), syncs the DB,
   fetches, extracts, promotes, and runs the identity audit in one shot.
2. **fetch-sources** HTTP-fetches each lead's website into `source_pages`.
3. **extract-claims** pulls keyword-bucket claims from the fetched text.
4. **Gate** (`source_supports_intake` in `research_agents.py`): promotes only if the fetched homepage
   supports the name + domain AND yields `>= PROMOTION_MIN_BUCKET_CLAIMS` (=2) non-unicorn vocabulary claims
   (`CLASS_KEYWORDS`). Dead domains / 403 / thin pages / UVC-dominant pages correctly do NOT promote.
   **Do not lower this threshold to hit a number — that re-imports junk.**
5. **Identity audit** (`inject_and_promote.py`): every *newly* promoted entity must have a DISTINCTIVE
   (non-generic, non-vocabulary) name token present in a substantial (>=400 char) homepage; failures →
   `needs_review`. Thin/JS-only pages are NOT demoted (unverifiable ≠ fabricated). NEVER run this
   retroactively over the whole atlas.

## Discovery workflow

`scripts/discovery_workflow.js` (run via the Workflow tool) fans out ~20 niche agents that **web-verify**
real firms (each returns an exact homepage quote), returns a deduped candidate set → feed that JSON to
`inject_and_promote.py`. The gate + identity audit are the anti-hallucination filter for AI-sourced leads.

## Known traps (learned the hard way 2026-05-28)

- **DB/CSV contamination:** `purge_atlas_junk.py` cleans CSVs only, not the DB; a stale `atlas.sqlite` can
  re-promote purged junk. Always rebuild the DB from clean CSVs before promoting.
- **Orphan claims:** purging entities leaves `entity_claims` rows whose `entity_id` is gone → breaks the DB
  FK so it won't rebuild. Sweep claims whenever you remove entities.
- **Sovereign vs impact keyword overlap:** Sovereign Capital's vocabulary shares "impact / mission-driven /
  global investment" with Patient Capital, so impact funds & family offices get mislabeled Sovereign
  (e.g. Capricorn Investment Group — corrected to Patient Capital 2026-05-28). Classification by keyword
  count is crude; treat every auto-assigned class as "needs human review before paper use."

## Roadmap / current focus

1. **Gate integrity over count (revised 2026-06-07).** The 500/1000 entity targets are retired: under the
   hardened thin gate (`data/runtime/gate_checks.py`) the credible verified universe is ~105 and the
   searchable vein is saturated. **The true size of the credible universe IS the finding** — do not pad to a
   number. Keep a *soft* ~150 near-term checkpoint for momentum via curated discovery + the gate (the count
   flexes; gate integrity does not).
2. Then **re-analyze the intake queue**: purge leads that won't make the cut.
3. Finally **self-description classification**: dissect how each entity describes itself to produce truly
   credible asset-class assignments. (This is the deep classification phase — not done piecemeal earlier.)

## Operating rules

- Never claim a row is a verified fact unless the source text was reviewed (see `docs/00_project_brief.md`).
- When you find a misclassified/junky entity, **flag it for review — do not auto-edit** unless the user
  directs a specific fix. Log manual changes to `data/evidence/manual_changes_*.log`.
- Social platforms (TikTok/IG/LinkedIn) are **discovery only** — surface firm names, then verify via the
  firm's official website through the gate. Do not bypass site protections.
- Back up the evidence CSVs (e.g. to `data/runtime/`) before any bulk promotion run.

## Entity genuineness — the allocator test (added 2026-05-29)

The atlas catalogs **capital allocators**: entities that **deploy their OWN (or LPs') capital into companies**
via equity, debt, revenue-share, or acquisition. The 6 asset classes are all *allocator types*. The gate
(name + 2 vocabulary words on a live page) **cannot tell an allocator from a lookalike**, so it admits:
- **Non-entities:** article/blog/listicle pages scraped as if firms (e.g. "Solo Founder AI Tools",
  "Roll-Up Strategy 2026"). → remove.
- **Ecosystem non-allocators:** marketplaces/brokers (Acquire.com, Microns — "for buyers/for sellers,
  asking price"), industry networks (The GIIN), pure advisories/nonprofits (Purpose US), accelerators that
  deploy NO capital (CodeLaunch). Real parts of the *industry* but NOT allocators → either drop or move to a
  separate **Ecosystem/Infrastructure** layer (NOT an asset class); never force into SMV/Patient/etc.

A measured random sample (30/530, 2026-05-29) found ~30% non-allocators + ~20% misclassified — "passed the
gate" ≠ "genuine". **Verification = web-judge each entity's homepage for (1) is it an allocator and (2) does
its self-description match its class.** This IS the self-description classification phase (they converge).

**Double-check protocol (learned the hard way — false positives cut BOTH ways):**
- An "embedded financing platform" CAN be a real allocator: YouLend says "Our capital" + revenue-based
  funding → genuine SMV, even though it looks like SaaS. Audit first flagged it junk; that was WRONG.
- A firm that "looks like financing" can be a marketplace: Microns is "Micro Startups For Sale" → broker.
- So: auto-remove ONLY unambiguous non-entities (articles/listicles). For any "junk" call on a real firm,
  run an **adversarial second check** (try to refute it — does it deploy its own capital?) before removing.
  Show borderline/financing cases to the user with page evidence. Reclassifications stay flag-only.

## Allocator test - build-their-own studios DO count (ratified 2026-06-08)

User ruling 2026-06-08: **venture studios that build and own their OWN products are valid allocators** - company creation IS the investment activity (they deploy their own capital to create + own companies). This ratifies taxonomy rule #3 and **supersedes** the older reading that held build-from-scratch studios (e.g. Finis Ventures, Sacramento Labs) as non-allocators 'for removal'. Do NOT re-hold a studio merely because it builds its own products instead of funding independent third parties. Footprint caveats (e.g. no announced portfolio) still lower confidence but do not disqualify.

## Ethan's directives (2026-06-07) - report structure + thesis-based classification (AUTHORITATIVE)

Captured verbatim in `docs/research/ethan_guidance_2026-06-07.md`. From the thesis owner; these govern the report:

1. **Report = two sections: "Active Experiments" (classes with real funds) + "Trends / things to look out for"
   (classes with NO funds yet).** Empty classes are PARKED in the watch section, never dropped - so the
   **Reserved** classes (Operator, Sovereign) live in Trends/Watch; the populated SMV/Nimble/Permanent/Studio
   are Active Experiments.
2. **Classify by ACTUAL FUND THESES, not our invented boxes** ("hypothetical... helping to give search terms";
   "ultimately the report needs to include what is actually out there"). Use the **INPUT -> OUTPUT model**:
   Traditional VC = large markets -> unicorn in 7-10y; **SMV** = large-ish markets -> sub-unicorn liquidity at
   similar-or-better timing; **Nimble** = SMALLER markets -> 3-5yr fast liquidity event.
3. **Nimble != camels/zebras/elephants** (those are startup metaphors, not fund classes). Per Ethan, Nimble =
   "small companies designed for fast liquidity events" and currently has **no funds yet** in his view.
4. **Tech-enabled scope confirmed** (Ethan thumbs-up reaction).

**[!] DIVERGENCE TO RECONCILE (do NOT auto-reclassify):** Ethan separates SMV/Nimble by **market-size +
liquidity speed**; the current `docs/01_taxonomy.md` separates them by **instrument** (equity vs revenue-based).
The 22 current Nimble rows were classed by the instrument rule and may not be "Nimble" in Ethan's sense.
Reconcile the definition with Ethan, THEN re-validate the 22 Nimble + 16 SMV rows. Flagged for human review.

## Classification phase timing (decided 2026-05-29)

Trigger the deep self-description cross-reference classification **now (~105 genuine entities), NOT at 500/1000**
(those targets retired 2026-06-07: gate integrity beats the number; report the true universe size as the finding).
Errors still compound at scale (junk doubles as you scale); clustering needs clean input; validate the method +
fix the curation exclusion gap first (method validated 2026-06-07 -> docs/research/classification_validation_2026-06-07.md),
THEN scale only as far as genuine credible allocators actually exist, with a proven classifier and junk-resistant
pipeline. Curation MUST exclude non-allocators explicitly (marketplaces, brokers, networks, embedded-finance
products, advisories, no-capital accelerators, articles) or a rebuild regenerates the same ~1/3 junk.
