# Liquidity-Horizon Enrichment Pipeline — Design Spec (2026-06-09)

**Status:** approved (verbal, 2026-06-09). Scope = Phase 1 (enrich-first re-audit). Implementation in progress.

## Goal

Make "operates outside the unicorn ~10-year power-law exit" the atlas's measurable, evidenced thesis.
Measure each firm's **liquidity horizon** (how fast capital is returned) and use it as the new classification
spine. This operationalizes Ethan's market-size/liquidity-speed axis (the SMV/Nimble divergence pending
since 2026-06-07).

## Decisions locked (user, 2026-06-09)

1. **Scraper = Scrapling** (BSD-3), `robots_obey=ON`, for the legit surface (firm sites, blogs, essays,
   press). LinkedIn/X stay public-unauthenticated or official-API only — never bypass a login wall.
2. **Signal = qualitative-primary, numeric-when-stated.** Language yields a qualitative signal; explicit
   years/$ are optional precision fields. (Realized-exit numbers via Crunchbase/PitchBook = Phase 2 seam.)
3. **Record, don't move.** Add the liquidity field + evidence + a *proposed* reclass note to every entity.
   Execute NO row moves until Ethan signs off on the cutoffs. (Honors the "flag, don't auto-edit" rule.)
4. **Bands (option 2 + tie-breaker):** Nimble `<6yr` · SMV `6–9yr AND $50M–500M` · Unicorn `≥10yr`
   (excluded) · Permanent = no exit · Studio = exit N/A. **Tie-breaker:** at the ~6yr crossing point, a
   sub-$50M exit → Nimble (small = nimble). Axis conflicts → `needs_review`, never a silent guess.
5. **Scrape purpose = both, enrich-first.** Re-audit the existing ~123 first; the same language gate becomes
   a discovery filter for new sub-10yr firms in a later cycle.

## Unit definition

A firm's **target / typical hold period** — stated philosophy in Phase 1; median realized hold in Phase 2.
A firm does not have a single "exit"; we measure the horizon it operates on.

## Data model — `data/evidence/liquidity_horizons.csv` (new, keyed `fund_id`)

Separate file (additive) → avoids the `atlas.sqlite` contamination trap; no `industry_entities`/`schema.json`
change in P1. Columns:

`fund_id, name, liquidity_signal, horizon_years, exit_size_usd, evidence_quote, evidence_url,
source_tier, confidence, current_class, proposed_band, proposed_reclass, needs_review, audited_at`

- `liquidity_signal` (primary): `fast | medium | slow | none | build_from_within | unknown`
- `horizon_years`, `exit_size_usd`: filled ONLY when explicitly stated.
- `source_tier`: `stated | language | structure | realized`.
- `proposed_reclass`: e.g. `"SMV->Nimble (signal=fast, exit<$50M)"` — recorded, NOT executed.
- Mirror into the audit CSV deferred (keep P1 strictly additive / zero-touch).

## Classifier — pure, config-driven (`liquidity/bands.py`)

Cutoffs in one config object (expected to change post-Ethan):
`BandConfig(nimble_max_years=6, smv_years=(6,9), smv_exit_usd=(50M,500M), unicorn_min_years=10)`

Resolution (qualitative-primary, numeric-refined, conflict→needs_review):
- `signal=none` → **Permanent**; `signal=build_from_within` → **Studio** (structural; numeric ignored, but a
  contradictory stated horizon sets `needs_review`).
- Derive `signal_band`: fast→Nimble, medium→SMV, slow→Unicorn, unknown→(none).
- Derive `numeric_band` when `horizon_years` present:
  - `>=10` → Unicorn · `<6` → Nimble
  - `6–9`: exit `<50M` **and horizon==6** → Nimble (tie-breaker); exit in `[50M,500M]` → SMV;
    exit `>500M` → needs_review; exit unknown → SMV + needs_review; exit `<50M` and horizon `>6` →
    needs_review (small-exit/medium-speed conflict).
  - `9–10` (gap) → needs_review.
- Combine: both bands present & equal → that band; both present & differ → **needs_review** (record both);
  only one present → that one; neither → **Unknown**.

## Scraper (`liquidity/scraper.py`)

Scrapling `Fetcher` (HTTP, TLS impersonation) primary; `StealthyFetcher` only for Cloudflare-blocked public
pages. `robots_obey=True`, polite delay. Reuse `strip_page.py` HTML→text logic; stdlib `urllib` fallback so
the module works before Scrapling installs. Enrichment only — the re-audit classifies stored text first, then
scrapes entities that come back `unknown`/low-confidence. LinkedIn/X hosts are hard-blocked in the fetcher.
**Two extraction targets by class:** Permanent/Studio (74) → *confirm* no-exit / build thesis; SMV/Nimble
(~40) → *pin* signal + horizon + exit-size.

## Signal extractor (`liquidity/signals.py`)

Deterministic lexicon (keyword/phrase → signal) + regex for stated years and $ figures. Every signal carries
the **matched verbatim quote** (anti-hallucination). No LLM in the extraction loop.
**Validation gate:** the first 123-run prints quotes per entity; eyeball the first ~15–20 to confirm the
lexicon before trusting it at scale.

## Re-audit harness (`liquidity/reaudit.py`)

Join audit (123) + verified (110) on `fund_id` → extract signal from stored text (`self_id_quote` + `notes` +
`flag`) → classify → write `liquidity_horizons.csv` + `proposed_reclass` flags (NO moves) → emit
`docs/research/liquidity_reaudit_<date>.md`. `--enrich` scrapes sites for entities with no stored signal.

## Build order

P1a model+config+**classifier (TDD)** → P1b extractor + validate on 15–20 → P1c scraper (Scrapling) +
full 123 run + report.

## Parked (later cycles, named)

Discovery filter for new firms · atlas-packet / "Active Experiments vs Watch" report integration ·
Crunchbase/PitchBook realized-exit numbers · mirroring liquidity columns into the audit CSV.

## Testing

Classifier → table-driven unit tests (`liquidity/tests/test_bands.py`: every band + $50M tie-breaker +
conflict→needs_review). `pytest`, AAA structure.
