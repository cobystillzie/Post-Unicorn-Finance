# Pilot — First Cuts (Phase 0)

Deep, small, matched seed: **15 post-unicorn** vs **16 VC-backed** companies (matched by sector + country). Every record is source-cited and was adversarially verified (all 31 retained). Data: `../data/pilot_companies.csv`.

> **Read this as a methodology demonstration, not a result.** A 31-firm purposive sample cannot establish causation; selection into the sample is deliberate, not random. The value here is (a) showing the fairness engine runs, and (b) mapping exactly which data are publicly available vs missing — the gap that justifies licensed-data integration in Phase 2.


## 1. Sample composition

- Sectors represented: Industrial / manufacturing (garage & overhead doors) (1), Tech-enabled hardware (direct liquid cooling for AI data centers / computing) (1), Industrial / manufacturing (machinery & equipment for automotive, construction, energy) (1), Industrial / manufacturing (HVAC & refrigeration compressors / climate technology) (1), Healthcare data analytics / technology (SaaS-style payment-accuracy & analytics for payers) (1), Industrial / advanced manufacturing (precision optics; aerospace, defense, semiconductor) (1), Consumer / services (meat market / butcher shop; small business) (1), Grocery / supermarket retail (1), Grocery / warehouse supermarket retail (1), Food manufacturing / whole-grain milling (CPG) (1), Craft beer / beverage manufacturing (1), Advanced materials / diversified manufacturing (e.g., GORE-TEX, medical, industrial) (1), Tree care / environmental & field services (1), Retail (department stores John Lewis + Waitrose supermarkets) (1), Industrial / diversified worker cooperative federation (industry, retail, finance, knowledge) (1), DevOps / developer-tools SaaS (1), Data cloud / horizontal enterprise SaaS (1), Food-delivery marketplace (on-demand logistics) (1), Grocery-delivery marketplace (on-demand logistics) (1), Fintech / buy-now-pay-later (consumer lending) (1), Consumer internet / social media (1), Robotic process automation (RPA) / enterprise automation SaaS (1), Travel / short-term-lodging marketplace (1), Consumer (footwear / apparel, direct-to-consumer) (1), Consumer (eyewear, direct-to-consumer retail) (1), Food (fast-casual restaurants / food service) (1), Food (plant-based dairy alternatives, oat milk; CPG) (1), Industrial (additive manufacturing / metal 3D printing hardware) (1), Services (software for trades / home & commercial services contractors) (1), Services / Consumer (shared electric-scooter micromobility) (1), Services / Consumer (shared electric-scooter and e-bike micromobility) (1)
- Countries represented: United States (25), Canada (1), United Kingdom (1), Spain (1), United States (remote-first; incorporated Delaware) (1), United States (founded in Bucharest, Romania) (1), Sweden (1)

## 2. Public-data coverage (the honest gap map)

| Field | Post-unicorn covered | VC-backed covered |
|---|---|---|
| Headcount | 14/15 | 15/16 |
| Capital raised/deployed | 7/15 | 11/16 |
| Both (enables per-dollar) | 6/15 | 11/16 |

_Where capital figures are missing it is usually because the firm is privately held / employee-owned and does not disclose capital deployed — precisely the gap a licensed provider fills._


## 3. A1 signal — does the capital model coincide with value-sharing?

Caveat: this reflects how the sample was *constructed* (value-sharing exemplars vs VC-backed firms), so it is illustrative of the contrast, not a prevalence estimate.

- Post-unicorn firms with a documented broad value-sharing mechanism: **15/15**
- VC-backed firms with a documented broad value-sharing mechanism: **1/16**

## 4. Per-dollar first cut (illustrative only)

Computed only where BOTH headcount and capital are public. **Heavy caveats apply** (headcount today vs capital over time; whole-portfolio denominator not yet applied; no matching).

| Company | Group | Headcount | Capital ($) | Jobs per $1M |
|---|---|---|---|---|
| Ingersoll Rand (incl. legacy Gardner Denver) | post-unicorn | 16,000 | 150,000,000 | 106.67 |
| Sweetgreen, Inc. | vc-backed | 5,000 | 479,000,000 | 10.44 |
| Instacart (Maplebear Inc.) | vc-backed | 3,486 | 563,800,000 | 6.18 |
| UiPath Inc. | vc-backed | 2,863 | 494,200,000 | 5.79 |
| Warby Parker Inc. | vc-backed | 2,651 | 535,000,000 | 4.96 |
| Reddit, Inc. | vc-backed | 2,013 | 472,600,000 | 4.26 |
| Allbirds, Inc. | vc-backed | 710 | 202,500,000 | 3.51 |
| Oatly Group AB | vc-backed | 550 | 200,000,000 | 2.75 |
| GitLab Inc. | vc-backed | 1,350 | 610,600,000 | 2.21 |
| Copeland | post-unicorn | 18,000 | 14,000,000,000 | 1.29 |
| DoorDash, Inc. | vc-backed | 3,279 | 3,270,000,000 | 1.0 |
| New Belgium Brewing | post-unicorn | 300 | 350,000,000 | 0.86 |
| Cotiviti | post-unicorn | 9,000 | 11,000,000,000 | 0.82 |
| Desktop Metal, Inc. | vc-backed | 337 | 438,000,000 | 0.77 |
| Airbnb, Inc. | vc-backed | 2,390 | 3,300,000,000 | 0.72 |
| C.H.I. Overhead Doors | post-unicorn | 800 | 3,000,000,000 | 0.27 |
| CoolIT Systems | post-unicorn | 650 | 4,750,000,000 | 0.14 |

- **No group median or comparison is reported.** The capital figures are not comparable across groups: for VC-backed firms they are *funding raised*, for post-unicorn buyout deals they are *acquisition / enterprise value*, and for employee-owned firms they are often absent. Comparing jobs-per-$1M across these denominators would be apples-to-oranges.
- **Do not quote these as findings.** The table proves the metric computes on real, sourced firms; it is not a result. A like-for-like denominator (capital deployed across the whole fund portfolio) requires the licensed data in Phase 2.

## 5. What the pilot establishes

- The fairness engine (`../docs/01_comparison_methodology.md`) is implementable on real firms.
- Public data reliably yields **headcount, value-sharing presence, sector, country, founding**; it is thin on **capital deployed** and **ownership splits** for private firms.
- Therefore Phase 2 needs one licensed provider (see `../docs/04_data_strategy.md`) to compute whole-portfolio per-dollar and distribution metrics credibly.


_Generated 2026-06-17 from the verified Phase-0 research workflow._
