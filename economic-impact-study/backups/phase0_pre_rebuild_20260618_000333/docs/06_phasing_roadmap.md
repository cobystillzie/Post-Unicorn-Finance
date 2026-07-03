# Phasing Roadmap

Each phase has a **gate**: it does not start until the prior phase's output is reviewed and greenlit by
Ethan. This keeps an ambitious, multi-week study honest and fundable one defensible step at a time.

---

## Phase 0 — Scoping + pilot (today, 2026-06-17)

**Goal:** give Ethan something concrete to understand and greenlight.

Deliverables:
- [x] Scoping brief (`00_scoping_brief.md`)
- [x] Comparison methodology / fairness engine (`01_comparison_methodology.md`)
- [ ] Mechanism catalog, broad + deep, source-cited (`02_mechanism_catalog.md`)
- [ ] Graded evidence synthesis (`03_evidence_synthesis.md`)
- [ ] Data strategy + provider × cost matrix (`04_data_strategy.md`)
- [x] Questions for Ethan (`05_questions_for_ethan.md`)
- [ ] Pilot 20-vs-20 dataset (`data/pilot_companies.csv`) + first cuts (`analysis/pilot_first_cuts.md`)
- [ ] One-page visual (`visuals/`)

**Gate to Phase 1:** Ethan confirms the thesis framing, the fairness basis, and the public-first/licensed-later
data sequence (see `05_questions_for_ethan.md`).

## Phase 1 — Complete the descriptive + causal foundations

**Goal:** a defensible map and a defensible "what's known."
- Finish the mechanism catalog: every major and emerging mechanism, US + international, with primary sources
  and a "likely unfamiliar to a generalist VC" flag.
- Complete the graded evidence synthesis: full coverage of the shared-capitalism, ESOP, EOT, and co-op
  literatures; an explicit evidence-quality ladder (causal-identified → quasi-experimental → correlational →
  advocacy); an honest verdict on A2 ("does value-sharing tip the odds?") with confidence levels.

**Gate to Phase 2:** the evidence verdict is solid enough that the original comparison is worth funding.

## Phase 2 — The full original comparison

**Goal:** scale the pilot into a credible empirical comparison.
- Expand the matched sample well beyond 20-vs-20, still matched on sector + country.
- Integrate a licensed data provider (selected from `04_data_strategy.md`) to fill the headcount-history,
  funding, ownership, and exit gaps the pilot exposed.
- Implement the full fairness engine: whole-portfolio per-dollar metrics, distribution share, annualization,
  with absolute figures alongside.
- Produce the headline result: *per dollar deployed, and by distribution, how the two stacks compare* — with
  confidence intervals and a frank limitations section.

**Gate to Phase 3:** firm-level results are robust enough that a macro extension would add, not distract.

## Phase 3 — Country / wellbeing macro layer (designed now, NOT claimed)

**Goal (future):** explore whether countries shifting toward non-unicorn, broadly-owned capital show more
jobs, more purpose, and higher wellbeing — **proven one step at a time, never asserted prematurely.**

Per Ethan's 2026-06-17 ruling: *"we should not make or claim this country level link. we will need to prove
that one step at a time through weeks of research."* So Phase 3 is **a design, not a result.**

Designed components (to build only after Phases 1–2 hold):
- **Wellbeing data:** World Happiness Report (Gallup) + OECD Better Life Index + UN HDI, triangulated.
- **"Non-unicorn shift" variable (the hard one):** a composite of (a) ownership-structure density (co-ops,
  EOTs, employee ownership per country), (b) capital-mix proxy (patient/alternative vs classic VC), and
  (c) atlas geography (where atlas entities cluster). Each is a weak proxy alone; the composite is exploratory.
- **Explicit confounder ledger:** national wealth, welfare-state generosity, culture, labor law — any of
  which can drive both wellbeing and capital structure. Country-level correlation cannot establish firm-level
  causation (ecological inference).

**Hard rule for Phase 3:** no causal country-level claim is published. Findings, if any, are framed as
"signals to watch," with the confounder ledger attached, until firm-level mechanisms are independently
established.

---

## Cross-phase dependencies

```
Phase 0 (scope + pilot) ──gate──▶ Phase 1 (catalog + evidence)
                                      │
                                      gate
                                      ▼
                              Phase 2 (full comparison, licensed data)
                                      │
                                      gate
                                      ▼
                              Phase 3 (macro/wellbeing — designed, claimed only when proven)
```
