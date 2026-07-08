# Ethan Feedback → Implementation Plan (2026-07-04)

Ethan reviewed the live atlas (Netlify: `postunicornfinanceatlas.netlify.app`) and reacted in Slack.
This captures **every** comment verbatim and turns each into a concrete build step. Execute in a
**fresh session** (the session that wrote this was at ~$389). Priority: P0 = do first.

## Verbatim comments (Slack, Today)
1. "WOW!!! As a first attempt this is completely awesome!!!!"
2. "will go into details this week (truth and proof are always in the details) but WOW"
3. "I think it's almost time to make this real"
4. "Of course an atlas also has a map. Is that possible"
5. "do we have impro.ventures" (linked Impro Ventures — "Investing early in talented founders who
   build human-centric solutions that empower human potential and a more sustainable life.")
6. "also i am thinking of an atlas"
7. "and thinking of developing a questionaire for foundrrs - should you pursue venture"

---

## Item-by-item implementation

### A. MAP — "an atlas also has a map. Is that possible" [P0, his marquee ask]
YES. **All 165 entities already carry `country`** (29 distinct: US 74, UK 17, Unknown 17, Canada 11,
India 6, Australia 5, …). Build a geographic view:
- Add a **self-contained inline SVG world map** (no external tiles/CDN — must stay one static HTML file
  for Netlify). Options: (a) dots sized by fund-count per country, or (b) a choropleth shaded by count.
- Color dots by dominant asset class; **click a country → filters the catalog** (reuse the existing
  filter JS). Hover → count tooltip.
- Add it to `scripts/build_atlas_artifact.py` as a new "Where in the world" section near the data charts;
  regenerate + redeploy. Keep the 17 "Unknown"/remote as a labeled off-map tally, not a fake location.
- Source of country→lat/long or country→SVG-path: embed a tiny static lookup in the script (world
  country centroids or a simplified world SVG); do NOT fetch a map library.

### B. impro.ventures — "do we have impro.ventures" [P0, direct question + proof test]
It IS in the atlas (`impro-ventures`) but **parked Reserved / confidence=low / tier=provenance**:
site returned **HTTP 403** (unfetchable), country from third-party Tracxn only, and its own page showed
**no anti-unicorn signal** (Africa/LATAM/SEA sustainability pre-seed→Series A). Action:
- **Re-verify properly**: fetch impro.ventures (try www / about / thesis; a real browser UA may clear the
  403). Confirm (1) allocator (yes — it invests), (2) tech-enabled, (3) does it carry a genuine
  post-unicorn/sustainability/anti-power-law thesis. Its tagline ("human-centric… more sustainable life")
  leans **Impact Capital**, not Reserved.
- **Owner directive (2026-07-04): classify `impro-ventures` as SMV** (tier `in_disguise`) — consistent
  with Ethan's original in-disguise vouch (added 2026-06-06 alongside Startup Ignition; in-disguise IS the
  SMV structural vein). Still fetch a live quote (retry the 403 with a real browser UA / try `www` +
  `/about`) and cite it if found. If the page shows a genuine sub-unicorn / anti-power-law signal, great;
  if it flatly reads pure-Impact with no such signal, KEEP SMV per this directive but set
  `confidence=low` and flag the conflict for the owner — do NOT fabricate a supporting quote.
- Tell Ethan the honest status either way — this is the "truth and proof in the details" test in miniature.

### C. "make this real" [P0] — productionize
- **Merge** branch `codex/complete-atlas-audit-2026-07-02` → main (still unmerged; open a PR).
- Site is live on Netlify ✓. Consider a **custom domain / subdomain on Ethan's site** later.
- Gitignore the stray `ruvector.db`.

### D. "truth and proof are always in the details" [P0] — evidence hardening (he WILL audit this)
- Re-verify the 3 rows resting on third-party interviews but carrying tier=`verified` (Siena, Neo,
  White Whale) → downgrade tier or re-source from the firm's own site.
- Fill the ~17 `Unknown` + remaining blank liquidity bands where evidence exists.
- Spot-check that every row's `exit_quote` still appears live on its cited page.
- Resolve the flagged clusters (secondaries funds in Nimble; the two kept angel groups) — these are the
  soft spots he'll find.

### E. FOUNDER QUESTIONNAIRE — "questionaire for foundrrs - should you pursue venture" [P1, new tool]
A short interactive quiz that routes a founder to the right capital class using **Ethan's INPUT→OUTPUT
model**. Questions ≈ market size, growth ambition, dilution tolerance, desired timeline/liquidity,
control/ownership goals, profitability path. Output: "Venture may/may not fit — here are the
post-unicorn paths that match you," linking into the relevant atlas classes.
- Build as a **self-contained interactive HTML page** (branching logic in vanilla JS), deployed as a
  second page alongside the atlas on Netlify (`/should-you-pursue-venture`). Feeds traffic INTO the atlas.
- Maps 1:1 onto the taxonomy: large market + unicorn appetite + high dilution + 7–10y → Traditional VC;
  large-ish + sub-unicorn → SMV; smaller market + fast exit → Nimble; no-exit/compounding → Permanent;
  build-and-own → Studio; mission-first → Impact.

### F. "also i am thinking of an atlas" [clarify]
Ambiguous — he may mean expanding this atlas (map + questionnaire cover a lot of it) or a second/companion
atlas. **Ask Ethan to clarify** what "an atlas" means beyond what exists before building anything net-new.

---

## Suggested order for the fresh session
1. B (re-verify impro.ventures — answers his question) + D (evidence hardening) — the "proof" he'll check.
2. A (the map — his marquee visual ask), regenerate + redeploy the Netlify file.
3. C (merge to main; gitignore ruvector.db).
4. E (founder questionnaire — the bigger new build).
5. F — one Slack message to Ethan to clarify "thinking of an atlas."

Generator: `scripts/build_atlas_artifact.py` (currently in scratchpad; copy into repo) → produces the
self-contained HTML → wrap with `<!doctype html>` skeleton → `C:\Users\cobys\Downloads\atlas-site\index.html`
→ drag folder to Netlify. Forms already wired (Netlify Forms: `suggest-a-fund`, `atlas-feedback`).

---

## Execution status — 2026-07-07 session

**DONE this session:**
- **B (impro.ventures):** re-fetched via Exa (site still 403s normal fetch; Playwright bridge unavailable).
  Page reads as emerging-markets pre-seed–Series A **impact VC** that screens for "category definer / global
  scalability" with team bios citing "scaling startups to unicorn status" — **no** post-unicorn signal, i.e.
  it flatly contradicts SMV. Per owner directive: reclassified **Reserved → SMV, tier provenance → in_disguise,
  confidence=low**, attached the real (non-supporting) quote, and wrote an honest `audit_flag` marking the
  classification as an owner-directed vouch with the conflict flagged. No quote fabricated.
- **D (re-verify):** **Siena** and **White Whale** re-sourced first-party (Siena `/vision`; White Whale
  `/secondaries-funds`). Siena confidence med→high. White Whale kept med (its 18-mo lower bound is still
  Inc42-only). **Neo** re-verify did not complete (session limit) — still third-party, left unchanged, PENDING.
- **D (bands):** filled `lighter-capital` = SMV (3–4y, first-party FAQ). `d2-fund` and `gorilla-capital`
  researched as SMV-style but that conflicts with their committed `asset_class=Nimble`, so band left Unknown
  and the finding written to `audit_flag` for owner reconciliation (flag-only per repo rules). `pemba`, `henq`,
  `kickstart` correctly left Unknown (no firm-authored horizon exists). All logged to
  `data/evidence/manual_changes_2026-07-07.log` (applied via `scripts/apply_evidence_2026_07_07.py`).
- **A (MAP):** self-contained inline-SVG **choropleth** added to the generator ("Where in the world"): 28
  shaded countries (Natural Earth 110m paths embedded at build time via `scripts/gen_world_map_paths.py` →
  `scripts/world_map_paths.json`; browser fetches nothing), shade = fund count, hover tooltip, **click a
  country → filters the catalog** (`#class=` deep-link support also added), 17 unmapped funds tallied off-map.
- **C (make real):** `ruvector.db` un-tracked + gitignored; branch merged to `main` and pushed.
- **E (questionnaire):** built `should-you-pursue-venture/index.html` — 7-question INPUT→OUTPUT quiz →
  Traditional VC / SMV / Nimble / Permanent / Studio / Impact, deep-links into the atlas, optional Netlify
  email capture (`questionnaire-results`). Linked from the atlas masthead nav.
- **F (clarify):** owner clarified in-session — "also i am thinking of an atlas" == the founder questionnaire,
  not a second/companion atlas. No separate build needed; Ethan message drafted for confirmation.

**PENDING — resume after 8pm America/New_York (session-limit reset):** the big evidence sweep that died on
the limit —
1. **Neo re-verify** (first-party re-source or downgrade).
2. **~20 remaining blank/Unknown liquidity bands:** bigfoot-capital, startup-ignition-ventures, emikoly,
   ascendant-ventures, microsaas-io, village-capital, zebra-impact-ventures, zebras-and-company, delta-fund,
   orbit-ventures, union-group-fund, timia-capital, saas-group, apex-point-equity, xo-capital, acadian-software,
   rhino-impact-fund, long-term-impact, enough-ventures, social-tech-ventures, savana-fund.
3. **137-row exit_quote live sweep** (0/137 ran) — verify each cited quote still appears on its live page.
   Resume by re-running the `evidence-hardening` workflow (script persisted under the session's workflows dir);
   drop the already-completed impro/Siena/White-Whale/lighter/d2/gorilla/pemba/henq/kickstart items.
