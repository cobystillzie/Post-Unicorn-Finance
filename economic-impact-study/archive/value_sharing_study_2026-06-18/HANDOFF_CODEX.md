# Codex Handoff — Economic Impact Study (Post-Unicorn Finance)

Copy everything below the line into Codex CLI to continue this study. It is self-contained: Codex has no
memory of the session that created Phase 0.

---

## Who you are / what this is

You are continuing an **economic impact research study** inside the Post-Unicorn Finance project at
`C:\Users\cobys\projects\post-unicorn-finance`. The study lives in its own folder,
`economic-impact-study/`, deliberately isolated from the atlas in `data/evidence/` (do NOT write to the
atlas). Read `economic-impact-study/README.md` first, then `docs/00_scoping_brief.md` and
`docs/01_comparison_methodology.md`. Read the root `CLAUDE.md` for project rules.

**The thesis:** *Does the post-unicorn capital model deliver more worker value-sharing — and
better-distributed economic impact, per dollar deployed — than the unicorn-chasing VC model?* It is a new
**lens** (how created value is shared with workers), orthogonal to the project's input/output model. NOT a
new atlas asset class.

## Governing rules (do not violate)

1. **Never hallucinate.** Every factual/numeric claim needs a real source URL. If unknown, write "not
   public" — never estimate or invent a number, company, citation, or URL. This mirrors the project's
   "classification credibility is everything" rule.
2. **No ToS-violating scraping.** Public/compliant sources only (SEC EDGAR, DOL Form 5500, NCEO, Companies
   House, company disclosures, official reports). Social platforms are discovery-only; do not bypass site
   protections. Licensed data providers are integrated **only after Ethan greenlights** (see below).
3. **Balanced posture.** Grade evidence honestly; separate correlation from causal identification and
   independent research from advocacy. Report absolute impact alongside normalized impact.
4. **Log changes** to a dated note and keep the study isolated from the atlas CSVs.
5. **A `GateGuard` hook may block file writes** — it asks you to state (a) what references the file, (b) that
   no existing file duplicates it, (c) any data fields/structure, (d) the user instruction — then retry the
   same write. Just present those facts and retry.

## What Phase 0 already produced (DONE — verify, don't redo)

All under `economic-impact-study/`:
- `README.md`, `docs/00_scoping_brief.md` — study definition + abstract.
- `docs/01_comparison_methodology.md` — the **fairness engine**: per-dollar + distribution, whole-portfolio
  denominator (failures counted), annualization, the 9-difference confounder framework.
- `docs/02_mechanism_catalog.md` — **48 source-cited value-sharing mechanisms** (US + international), with a
  "likely unfamiliar to a generalist VC" index.
- `docs/03_evidence_synthesis.md` — **47 graded findings** across shared-capitalism (Rutgers/NBER), ESOP/NCEO,
  UK EOT, co-op survival, and the skeptical literature, with an evidence-grade ladder.
- `docs/04_data_strategy.md` — public-first approach + a **provider × metric × cost matrix** (17 sources) for
  licensed-data integration.
- `docs/05_questions_for_ethan.md` — 14 decisions to confirm with the thesis owner.
- `docs/06_phasing_roadmap.md` — Phase 0→3 with gates.
- `data/funds_pilot.csv` + `data/fund_portfolio_companies.csv` — **FUND-LEVEL pilot (corrected 2026-06-18):
  13 funds (5 atlas + 3 worker-ownership + 5 matched VC), 93 portfolio companies rolled up, all adversarially
  verified and source-cited.** Rows are FUNDS. The earlier company-level `pilot_companies.csv` was retired
  because it conflated companies with funds — see `analysis/2026-06-18_audit_and_rebuild.md`.
- `analysis/fund_level_first_cuts.md` — employee-participation by group (worker-ownership 26/26, atlas 1/28,
  VC 0/39) + jobs, with binding caveats ("unknown" ≠ absent; no per-dollar claim).
- `visuals/study_architecture.html` — one-page diagram.
- `build_fund_level.py` — regenerates the fund-level pilot from the verified fund workflow JSON.
- `build_phase0.py` — regenerates `02/03/04` only; its company-pilot section was retired (early-exits).
  NOTE: `docs/04_data_strategy.md` still contains two stale references emitted by it (the phrase
  "first 20-vs-20" and a link to the deleted `pilot_first_cuts.md`) — fix the generator text + regenerate.

## Known issues / the real methodological frontier (this is your job)

1. **Heterogeneous denominators (the central unsolved problem).** In the pilot, "capital" means *funding
   raised* for VC firms but *acquisition / enterprise value* for post-unicorn buyout deals, and is missing
   for employee-owned firms. These are NOT comparable. Until this is fixed, **no cross-group per-dollar
   comparison or median is valid** (the first-cuts file correctly refuses to report one). Solving this —
   defining a like-for-like "capital deployed across the whole fund portfolio" denominator — is the core
   Phase-2 task.
2. **Public data is thin on capital and ownership splits** for private firms (coverage ~7/15 post-unicorn,
   11/16 VC). This is the documented justification for licensed data.
3. **Selection bias.** The pilot sample is purposive, not random; it demonstrates the method, it is not a
   result. The causal question ("does sharing tip the odds?") is answered by the graded literature, not by
   the 31-firm cross-section.

## Next steps, in priority order

1. **Take `docs/05_questions_for_ethan.md` to Ethan** and record his answers (especially: confirm the
   comparative thesis; the public-first/licensed-later sequence + any budget + preferred provider; whether
   the Phase-3 country/wellbeing layer is worth designing toward). Do not start Phase 2 spend before this.
2. **Phase 1 — deepen and verdict.** Extend the mechanism catalog where Ethan wants depth; complete the
   evidence synthesis into an explicit, confidence-rated verdict on "does value-sharing tip the odds?"
   (lead with the causally-identified studies; be honest about the rest).
3. **Phase 2 — the real comparison.** Solve the denominator problem (whole-portfolio capital deployed,
   like-for-like across groups); expand the matched sample well beyond 20-vs-20 (still matched by sector +
   country); integrate ONE licensed provider from `docs/04_data_strategy.md` to fill headcount-history,
   funding, and ownership; compute per-dollar + distribution + annualized metrics with absolute figures
   alongside and confidence intervals.
4. **Phase 3 (design only, do NOT claim).** The country/wellbeing macro layer (World Happiness Report + OECD
   Better Life + HDI). Per Ethan's explicit ruling, make **no country-level causal claim** — ecological
   inference + confounders (national wealth, welfare state, culture) forbid it until firm-level mechanisms
   are independently established. Design it; do not run or assert it.

## Practical notes

- To regenerate the research files after editing source data: `cd economic-impact-study && python build_phase0.py`.
- Keep the atlas (`data/evidence/`) untouched. Append any manual decisions to a dated log.
- Match the project's evidence discipline: show the quote, cite the URL, flag uncertainty.
