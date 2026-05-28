# Self-Description Taxonomy Findings

_Generated 2026-05-27. Bottom-up test of the placeholder asset classes against how the 169 atlas entities actually describe themselves, plus open-web discovery._

## Method (and its honest limits)

The question driving this work: **do the asset classes we already coined (SMV, LMV, Patient Capital, Sovereign Capital, Search/ETA, Portfolio Capital) actually show up as real commonalities in how entities describe themselves — or are they analyst labels imposed from outside?**

To test this without inventing anything, every input is grounded in text already captured in this repo or fetched live:

- **109 successfully fetched entity web pages** with full `raw_text` in `source_pages` (≈615K characters of entity-authored language; 80 of 169 atlas entities matched a fetched page by domain, 106 unique domains total).
- The structured descriptor fields on each entity (`capital_model`, `target_company_profile`, `sector_focus`, `instrument_types`).
- The 196 sourced `entity_claims`.

The project's own scaffolding language ("candidate supports industry mapping outside or adjacent to classic unicorn VC", "source-backed SMV bucket evidence") and the placeholder class tokens (smv/lmv/uvc) were **stripped** before analysis, so clusters reflect entity self-description, not our labeling. Clustering used multi-word phrases (bi/tri-grams) under TF-IDF + Jaccard single-linkage.

**Limits:** exact-string label counts undercount hyphen/spacing variants; only ~half of entities had a fetched page, so structured fields carry the rest; clustering is the more reliable signal than any single literal count. This is a discovery instrument, not proof.

## Headline finding

The **coined category names are not self-identities.** Across 106 fetched entity pages, the literal strings `strategic middle venture`, `middle venture`, `SMV`, `leveraged micro`, and `LMV` appear **0 times**. No entity calls itself a "Strategic Middle Venture."

By contrast, several **real-world self-labels do appear in entities' own words**: `search fund`, `patient capital`, `revenue-based`, `venture studio`, `steward`, `evergreen`, `sovereign`, `permanent equity` (the last two undercounted by exact matching).

Conclusion: the taxonomy is a mix. Some buckets correspond to genuine self-identities the market already uses; others (notably SMV and LMV) are useful *analyst umbrellas* that fragment into several distinct self-described sub-groups.

## Per-class verdict

| Placeholder class | Emerged as a self-description cluster? | Verdict |
|---|---|---|
| **Search / ETA** | Yes — cluster of 14, 100% pure. Shared language: "search fund", "search capital", "entrepreneurs search funds", "fund investing". | **VALIDATED.** Strongest real self-identity. Keep as-is. |
| **Sovereign Capital** | Yes — cluster of 8, 100% pure. "sovereign wealth", "global investment", "capital allocator". | **VALIDATED** as a source-of-capital identity. Keep. |
| **Portfolio Capital (software acquirers)** | Yes — cluster of 16, 15/16 pure. "software acquisition capital", "vertical software", "permanent equity". | **VALIDATED but mis-named.** The real self-identity is "vertical / serial software acquirer," narrower than "Portfolio Capital." |
| **Portfolio Capital (studios)** | Partial — clusters of 14 + 4. "studio equity", "company creation/formation", "startup studio". | **CROSS-CUTTING.** Studios are a coherent self-identity distinct from acquirers; "Portfolio Capital" conflates two different self-described groups. |
| **Patient Capital** | Partial — overlaps heavily with a stronger permanent/steward/evergreen cluster. "patient capital" (5 pages) co-occurs with "permanent equity / no forced exit / steward / evergreen". | **MERGE CANDIDATE.** Should be reconciled with the Permanent/Steward cluster below. |
| **SMV (Strategic Middle Ventures)** | **No.** The 65 SMV-labeled entities scatter across acquirers, studios, revenue-financing, and embedded-finance clusters. The descriptive *traits* it names (capital-efficient, bootstrapped, profitable) are used by entities; the *name* is used by none. | **ANALYST UMBRELLA, not a self-identity.** Keep as an analytic layer, but the real classes are its sub-groups. |
| **LMV (Leveraged Micro Ventures)** | **No.** Thin (8), no clean cluster; web search confirms the *company archetype* exists (solo AI founders, Pieter Levels' $3M solo portfolio, Base44→Wix $80M) but dedicated *capital-entity* infrastructure barely exists yet. | **PREMATURE as an entity class.** Real as a company archetype; track, don't yet codify as an asset class. |

## The emergent self-description clusters (from the 169)

1. **Vertical / serial software acquirers (16)** — "software acquisition capital", "vertical software", "permanent equity". _Constellation, Volaris, Harris, Topicus, Valsoft, Tiny, Visma, ESW…_
2. **Search-fund / ETA capital (14)** — "search fund", "entrepreneurs search funds". _Pacific Lake, Search Fund Partners, Relay, Trilogy, Anacapa…_
3. **Vertical-SaaS studios + growth equity (14)** — "studio equity", "company formation", "vertical saas growth". _High Alpha, Pioneer Square Labs, Fractal Software, SeedTwo, DWP…_
4. **Revenue-based / non-dilutive financing providers (11)** — "revenue based financing", "recurring revenue". _Capchase, Uncapped, Outfund, GetVantage, Klub, Recur Club…_ (filed under SMV, but self-describe as an instrument-provider class.)
5. **Sovereign-wealth / global allocators (8)** — "sovereign wealth", "global investment". _GIC, Temasek, Mubadala, QIA, PIF, Khazanah…_
6. **SMB ownership / employee-ownership ETA (4)** — "small business owners", "sell business". _Teamshares, Mainshares, Acquira, Common Future._
7. **Embedded finance / working capital (4)** — "embedded finance". _PayPal Working Capital, Liberis, YouLend, Parafin._
8. **Permanent-equity holders (3, + new web entities)** — "permanent equity", "hold forever". _Tiny, Permanent Equity, Tangle Ventures._
9. **Venture/startup studios (4)** — "company creation", "startup studio". _Team8, Expa, Wilbur Labs, Juxtapose._

(91 clusters total; 9 of size ≥3, the rest singletons/pairs — the long tail is where novel or under-covered identities hide.)

## New entities discovered on the open web (grounded, fetched)

A coherent **Permanent / Steward / Evergreen capital** identity emerged that is currently scattered across Patient Capital, Portfolio Capital, and SMV in our placeholders:

- **Everhold** (everhold.com) — verbatim: _"We buy businesses. And hold them forever… We're not a private equity firm… We use permanent capital."_ Founder-led B2B, $500K–$2M EBITDA, vertical SaaS/services.
- **Purpose Evergreen Capital** (purpose-economy.org) — verbatim: _"patient, value-aligned capital… an evergreen investment fund without pressure to force an exit… we invest without voting rights… the investor return rate is capped."_ Steward-ownership, €0.5–5M, €30M raised.
- **HOLD.co** — permanent-capital holding-company strategy (per its own blog).
- **Upliift** — permanent-equity approach.
- **Bending Spoons** — acquires and holds tech brands (Evernote, Vimeo, Meetup) with "no plans to sell."
- **The Fund for Employee Ownership / EVGOH** (evgoh.com) — patient capital, converts SMBs to employee ownership.
- **Evergreen** (evergreensg.com) — "a permanent home for businesses."

Market-discourse signal for the thesis: TechCrunch (Nov 2025), "Why 'hold-forever' investors are snapping up venture-capital 'zombies'"; Fortune (Mar 2026), "unicorn cap-table gridlock."

## The "guerilla fund" specimen — honest status

The literal label "guerilla/guerrilla" is **not** a reliable selector for non-unicorn capital. Three real funds carry it: Guerrilla Capital (Copenhagen, 2018), Guerrilla Ventures (Delhi angel fund), Guerrilla Venture Capital (Louisville). For the Copenhagen fund I have only third-party profiles (no own-site text): early-stage pre-seed→Series A, operator-investor model, partners who built ~$43M-valued companies. That ~$43M figure is a *middle* outcome, not unicorn scale — so the evidence is **ambiguous**, not a clear non-fit. Classified **needs_verification**, pending the fund's own-words self-description. The broader point stands: classification must come from self-description language, not branding.

## Reiterated taxonomy (proposed)

Keep what the market self-identifies with; demote coinages to an analytic layer:

- **Acquisition & Hold** — vertical/serial software acquirers + permanent-equity holders (clusters 1, 8).
- **Steward / Evergreen / Patient Capital** — merge Patient Capital with the permanent/steward/evergreen identity (cluster 8 + new web entities).
- **Search / ETA Capital** — validated as-is (cluster 2), with an SMB/employee-ownership ETA sub-lane (cluster 6).
- **Studio / Company-Creation Capital** — split out of Portfolio Capital (clusters 3, 9).
- **Revenue-Linked / Non-Dilutive Financing** — promote from "Instrument" to a provider class (cluster 4); includes embedded finance (cluster 7).
- **Sovereign / Strategic Capital** — validated as-is (cluster 5).
- **SMV / LMV** — retain as *analytic umbrellas* (capital-efficiency and micro-team theses), not as self-identities.
