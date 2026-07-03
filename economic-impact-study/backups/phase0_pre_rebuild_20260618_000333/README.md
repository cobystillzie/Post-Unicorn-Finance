# Economic Impact Study — Per-Dollar Impact of Post-Unicorn Capital

A self-contained research study inside the Post-Unicorn Finance operation, commissioned by Ethan
(2026-06-17). It is **deliberately isolated from the atlas** (`../data/evidence/`) so that exploratory
impact research cannot contaminate the classification corpus. The atlas is the *population we test*, not
the place this study lives.

## The one-sentence thesis

> **Does the post-unicorn capital model deliver more worker value-sharing — and better-distributed
> economic impact, per dollar deployed — than the unicorn-chasing venture-capital model?**

This study is a new **lens**, not a new asset class. It sits *orthogonal* to the project's INPUT→OUTPUT
model: not how companies are funded (inputs) and not how investors exit (outputs), but **how the value
created gets shared with the people who build the company, and whether that sharing changes the odds the
company works** (Ethan's framing, 2026-06-17).

## Two equal halves

1. **Descriptive — "the map."** A broad *and* deep catalog of worker value-sharing mechanisms (ESOPs,
   profit-sharing, warrants/options, phantom equity, EOTs, co-ops, steward-ownership, broad-based equity,
   and mechanisms not yet named). Gives the thesis owner a vocabulary and a landscape.
2. **Analytical — "the claim."** A normalized **unicorn-vs-post-unicorn impact comparison**, plus a graded
   synthesis of the existing empirical evidence (Rutgers/NBER shared-capitalism, NCEO, the UK Ownership
   Effect Inquiry, co-op survival research).

Both halves carry equal weight. Posture is **balanced and evidence-graded** — never overclaimed, never
fabricated (consistent with the project's "classification credibility is everything" rule).

## Folder map

| Path | Contents |
|------|----------|
| `docs/00_scoping_brief.md` | **The centerpiece.** Academic-grade scoping brief Ethan reads. |
| `docs/01_comparison_methodology.md` | The "fairness engine": per-dollar + distribution measurement design and the 9-difference confounder framework. |
| `docs/02_mechanism_catalog.md` | The value-sharing mechanism catalog (broad + deep), source-cited. |
| `docs/03_evidence_synthesis.md` | Graded synthesis of the causal evidence (does value-sharing tip the odds?). |
| `docs/04_data_strategy.md` | Public-data pilot approach + the metric × data-provider × cost matrix (for licensed-provider integration after Ethan's go-ahead). |
| `docs/05_questions_for_ethan.md` | The sharp decision/question set to take into the conversation with Ethan. |
| `docs/06_phasing_roadmap.md` | Phase 0 (today) → Phase 3 (the country/wellbeing macro layer). |
| `data/pilot_companies.csv` | The verified, source-cited pilot dataset (post-unicorn vs VC-backed). |
| `analysis/pilot_first_cuts.md` | First-cut findings from the pilot, with honest data-gap notes. |
| `visuals/` | One-page diagram of the study (for handing to Ethan). |
| `HANDOFF_CODEX.md` | Self-contained prompt to continue the study in Codex CLI (Phases 1–3). |
| `build_phase0.py` | Deterministic builder: regenerates `02/03/04` + pilot CSV + first cuts from the verified research JSON. |

## Governing decisions (locked 2026-06-17, via brainstorming session)

- **Unit of analysis:** the full chain — allocator model → company value-sharing → worker & economic outcomes.
- **Outcomes (reported separately):** worker ownership depth · jobs & quality (created vs preserved) ·
  who captures the upside (distribution) · survival & longevity. Centered on *does value reach workers*.
- **Externalities in scope (all four):** worker outcomes · firm performance/survival · wealth
  distribution/inequality · regional & macro effects.
- **Geography:** US-primary, with UK / Europe / global as comparison.
- **Fairness basis:** **per-dollar deployed + distribution share**; absolute impact also reported honestly.
- **Portfolio basis:** whole-fund-portfolio including failures (not survivors only).
- **Jobs:** created vs preserved, labeled separately. **Wealth:** realized first, paper as context.
- **Timing:** impact annualized + caveated.
- **Matching:** by sector + country.
- **Pilot data (today):** public / compliant sources only — **no ToS-violating scraping**; licensed
  providers integrated only after the first 20-vs-20 is shown to Ethan.
- **Country/wellbeing link:** *designed* as Phase 3; **no country-level causal claim is made today.**

## Status

- **Phase 0 (today): COMPLETE.** Scoping brief, methodology (fairness engine), 48-mechanism catalog,
  47-finding graded evidence synthesis, data-provider/cost matrix, verified 31-company pilot
  (15 post-unicorn vs 16 VC-backed) + first cuts, questions for Ethan, one-page visual, Codex handoff.
- **Open methodological frontier:** capital denominators are heterogeneous (VC funding-raised vs buyout
  enterprise-value vs missing for employee-owned) — so no cross-group per-dollar comparison is asserted yet.
  Solving this + licensed data is the Phase-2 task. See `HANDOFF_CODEX.md`.
- Phases 1–3: see `docs/06_phasing_roadmap.md`.
