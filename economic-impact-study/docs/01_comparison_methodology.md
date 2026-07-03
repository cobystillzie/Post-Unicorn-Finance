# Comparison Methodology — The Fairness Engine

How we make the **unicorn-chasing VC** stack and the **post-unicorn** stack comparable despite enormous
differences in scale, timing, and survivorship. This is the analytical core of the study. All illustrative
numbers below are **synthetic, clearly labeled** — they show the arithmetic, not findings.

---

## 1. The comparability problem

A single unicorn can create thousands of jobs with billions of dollars. A small SMV or search fund cannot
match that in absolute terms — and pretending it could would be dishonest and would fail the project's
"never overclaim" rule. So a raw, company-to-company or fund-to-fund impact comparison is invalid.

The study's answer is **not to compare absolute size** but to compare:
1. **Impact per dollar deployed** (efficiency of impact), and
2. **Distribution of that impact** (who captures the value).

We *also* report absolute impact, so the unicorns' genuine scale is acknowledged.

## 2. The three normalizations + the honesty rule

**N1 — Per-dollar deployed.** For each outcome `X`, report `X / capital_deployed`. The denominator is
**capital deployed across the entire fund/portfolio, including failures** — not just the capital behind
surviving companies. This is the single most important fairness lever: VC's power-law model produces many
write-offs, and excluding them would massively flatter VC by hiding the dollars that produced no impact.

> *Synthetic illustration.* Fund A (VC) deploys $1,000M across 20 companies; 17 fail, 3 survive creating
> 6,000 jobs total → **6.0 jobs per $1M**. Fund B (post-unicorn) deploys $100M across 20 companies; 16
> survive creating 1,800 jobs → **18.0 jobs per $1M**. Absolute jobs favor A (6,000 vs 1,800); per-dollar
> favors B (18 vs 6). Both numbers are reported.

**N2 — Distribution share.** For created or realized value `V`, report the fraction reaching non-executive
workers vs. founders and investors:
`worker_share = value_to_workers / total_value_realized`.
A unicorn may create more total value yet route ~90% to a few; a post-unicorn firm may create less yet
spread it widely. Distribution share captures exactly that.

**N3 — Per-year (annualized).** Because unicorn exits arrive years later than post-unicorn liquidity, divide
cumulative impact by years of operation (`X / firm_age_years`) so slower/later outcomes are not unfairly
penalized — *and* state the raw timing difference as a caveat (N3 is an adjustment, not a cure).

**Honesty rule.** Every normalized figure is published **alongside its absolute counterpart**. The headline
is the normalized comparison; the absolute is always visible next to it.

## 3. The nine-difference confounder framework

Each structural difference between the two stacks biases a naïve comparison. Each is handled explicitly.

| # | Difference | How it biases the comparison | Handling |
|---|---|---|---|
| 1 | **Capital scale** | VC deploys far more per company → larger absolute impact | N1 per-dollar normalization |
| 2 | **Survivorship** | VC power-law: most fail; comparing survivors hides write-offs and flatters VC | Whole-portfolio denominator (failures counted) |
| 3 | **Exit timing** | VC realizes value in 7–10y; post-unicorn faster/permanent | N3 annualize + timing caveat |
| 4 | **Build vs buy** | VC builds from zero (jobs *created*); holdcos/search buy existing firms (jobs *preserved*) | Count both, labeled separately; never sum blindly |
| 5 | **Value distribution** | VC concentrates equity; post-unicorn uses broad ownership | N2 distribution share (the thesis metric) |
| 6 | **Paper vs realized wealth** | Employee equity is often illiquid paper that never pays out | Realized wealth is primary; paper/granted shown as context |
| 7 | **Sector & geography** | VC clusters in coastal tech; post-unicorn spreads across sectors/regions | Match on sector + country; treat the *spread itself* as a regional-externality finding |
| 8 | **Spillovers** | Unicorns spawn ecosystems ("alumni mafias"); post-unicorn spillovers are more local | Qualitative in pilot; quantify in the Phase-3 macro layer |
| 9 | **Additionality / counterfactual** | Would the firm have existed/grown anyway? | Acknowledged as an honest limitation; no causal-additionality claim |

## 4. Metric definitions

**Per-dollar (N1) metrics**
- `jobs_per_$1M` = total jobs (created + preserved, labeled) ÷ capital deployed (whole portfolio).
- `worker_equity_value_per_$1M` = realized employee equity/profit-share value ÷ capital deployed.
- `surviving_firms_per_$1M` = count of going concerns ÷ capital deployed.

**Distribution (N2) metrics**
- `worker_value_share` = value to non-exec workers ÷ total value realized.
- `ownership_breadth` = share of employees who hold any ownership/upside (0–100%).
- `concentration` = founder+investor+exec share of realized value (the complement view).

**Time (N3)**
- Any stock metric may be annualized by firm age (or fund vintage) where age is known.

**Absolute (honesty rule)** — raw totals for every metric, reported next to the normalized version.

## 5. Matching strategy

Per the 2026-06-17 decision, match the two groups on **sector/industry** and **country** (not on revenue or
size — size matching is precisely what the per-dollar normalization replaces, since an SMV firm cannot be
revenue-matched to a unicorn without distortion). Matching equalizes the *context* (industry economics,
labor market) while normalization equalizes *scale and timing*.

## 6. Estimating the chain (A1 / A2 / A3)

- **A1 (capital → sharing):** within the matched set, compare `ownership_breadth` and the presence of
  value-sharing mechanisms across post-unicorn vs VC-backed firms.
- **A2 (sharing → outcomes):** answered primarily by the **graded evidence synthesis** (`03_…`), not by our
  own causal estimation in Phase 0 — the identification problem (selection bias) is too severe for a
  20-firm pilot to settle.
- **A3 (full chain, net comparison):** combine N1 + N2 across the matched set to produce the headline
  "impact per dollar, and its distribution" comparison, with absolute figures alongside.

## 7. Pilot feasibility (public data only, Phase 0)

With public/compliant sources, expect reliable coverage of: headcount, founding year, sector, country,
broad ownership *presence* (especially for ESOP/EOT/co-op firms via filings), and many capital figures.
Expect gaps in: precise cap-table splits, private-company realized-value distributions, and wage detail.
The pilot computes every metric **only where sourced data exists**, marks the rest "not public," and treats
the gap map as a deliverable that motivates licensed-data integration in Phase 2 (`04_data_strategy.md`).

## 8. Threats to validity (restated for the methods reader)

- **Endogeneity / selection** (A2): the firms that adopt broad ownership may already differ. Mitigated by
  leaning on causally identified studies in `03`; *not* claimed from the pilot's cross-section.
- **Survivorship if denominator slips** (A3): the whole-portfolio denominator must include failures on both
  sides; partial portfolio data biases toward whichever side is better documented. Flagged per firm via
  `data_confidence`.
- **Realized-value opacity** (N2): private realized distributions are often undisclosed; distribution share
  may rest on disclosed ownership *breadth* as a proxy in the pilot, with the proxy stated.
- **Ecological inference** (Phase 3): country-level correlation ≠ firm-level causation; the macro layer is
  designed, not asserted.

## 9. Ideas parked for further brainstorming (per 2026-06-17 request)

Additional ways to handle the two-stack difference, to discuss with Ethan before Phase 2:
- **Risk-adjusted per-dollar:** weight by capital-at-risk to reflect VC's higher loss rate.
- **Cohort/vintage bands:** compare same-vintage cohorts as an alternative to annualization.
- **Counterfactual jobs:** for buy-and-hold acquirers, estimate jobs *preserved* against a base-rate SMB
  failure counterfactual (carefully; additionality is hard).
- **Distribution Gini:** a within-firm Gini of equity ownership as a single distribution statistic.
- **Multiplier accounting:** a structured (still qualitative) treatment of local vs ecosystem spillovers.
