# Audit & Fund-Level Rebuild — 2026-06-18

A complete audit of the Phase-0 study (including the Codex takeover) plus the corrective rebuild it triggered.

## Trigger

The thesis owner flagged that the pilot compared **unicorn *companies* vs employee-owned *companies*** — when
the study is meant to compare **unicorn-chasing *funds* vs non-unicorn-chasing *funds*.** Correct catch.

## Audit findings

1. **Unit-of-analysis conflation (the core flaw).** The company-level pilot's rows were operating companies,
   and the "post-unicorn" group was a grab-bag of three incompatible things: mega-PE buyout portfolio
   companies (KKR/Blackstone — not atlas allocators), one VC-backed company (Thielen Meats via Teamshares),
   and standalone employee-owned firms with no fund at all (Publix, Mondragón, John Lewis, W.L. Gore…). The
   VC side was likewise unicorn companies, not VC funds. → Not a fund-vs-fund study.
2. **Codex's work: clean and honest.** Codex's `pilot_data_quality_audit.md` independently caught the
   heterogeneous-denominator problem and correctly blocked any group-level per-dollar result; it added an
   exception ledger (Bob's Red Mill, Warby Parker), did housekeeping (argparse build, `data/raw/` source with
   a SHA-256, a `backups/` snapshot, ruff), and reconciled the stale "20-vs-20" wording. No fabrications.
   **It did not catch the unit conflation** — that was outside its handoff scope.
3. **Unaffected artifacts retained.** The mechanism catalog (`02`), evidence synthesis (`03`), and data
   strategy (`04`) concern mechanisms, literature, and providers — not the fund comparison — so they were
   kept as-is.

## Resolution (decided with the thesis owner, 2026-06-18)

- **Unit = funds** (rows are funds; portfolio companies roll up).
- **Non-unicorn side = atlas funds + a labeled worker-ownership group** (Teamshares, Apis & Heritage, Mosaic).
- **Unicorn side = matched VC funds.**
- **Deleted** the company-level pilot (`pilot_companies.csv`, `pilot_first_cuts.md`,
  `vc_backed_comparison_set.md`); the full pre-rebuild state is preserved in `backups/`.
- **Rebuilt** at the fund level via a verified research workflow: 13 funds, 93 sampled portfolio companies,
  every datapoint source-cited, an adversarial verify pass per fund (all 13 retained).

## New finding (caveated)

Broad employee participation (ESOP / broad ownership) by group, in the sampled portfolios:

| Group | Funds | Portfolio cos | Broad/ESOP | None/standard-VC | Unknown |
|---|--:|--:|--:|--:|--:|
| Worker-ownership allocators | 3 | 26 | 26 | 0 | 0 |
| Atlas (non-unicorn-chasing) | 5 | 28 | 1 | 3 | 24 |
| Unicorn-chasing VC | 5 | 39 | 0 | 19 | 20 |

**Reading:** worker value-sharing is real but lives in a *small dedicated worker-ownership niche*; it has
**not** diffused into the broader atlas/post-unicorn capital this project catalogs. That is a direct, honest
answer to Ethan's original question ("is capital innovation extending into ESOPs/participation?") — *not yet,
except in that niche.*

**Caveats (binding):** portfolios are documented samples; "unknown" (dominant for atlas) is absence of public
evidence, not proven absence; the worker-ownership 100% is definitional; **no per-dollar comparison is
asserted** — capital denominators remain heterogeneous and whole-portfolio data needs Phase-2 licensed data.

## Still open

- The per-dollar denominator problem (funding-raised vs acquisition/EV vs missing) — Phase 2 + licensed data.
- Atlas portfolio-company participation data is thin; confirming true absence needs primary-source checks.

## Files changed this rebuild

- Added: `data/funds_pilot.csv`, `data/fund_portfolio_companies.csv`, `analysis/fund_level_first_cuts.md`,
  `data/raw/fund_level_output_2026-06-18.json`, `build_fund_level.py`, this audit.
- Deleted: `data/pilot_companies.csv`, `analysis/pilot_first_cuts.md`, `data/vc_backed_comparison_set.md`.
- Updated: `00_scoping_brief.md`, `01_comparison_methodology.md`, `05_questions_for_ethan.md`, `README.md`,
  `build_phase0.py` (company-pilot section neutralized), `HANDOFF_CODEX.md`.
- Retained historical record: `analysis/pilot_data_quality_audit.md` (Codex's audit of the now-superseded
  company-level pilot) and `backups/` (full pre-rebuild snapshot).
