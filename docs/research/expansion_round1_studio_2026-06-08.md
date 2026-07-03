# Expansion Round 1 — Studio-first (2026-06-08)

**Method:** Exa `web_search_exa` discovery (Studio-weighted) -> dedup -> `web_fetch_exa` RAW own-page ->
inline judge against all 7 gates -> `admit_batch.py` (gate_checks pre-screen + fund_id dedup + CSV backup).
No schema-Workflow judge (per doctrine). All admits carry a verbatim own-page quote seen in raw markdown.

## ADMITTED (3 new rows; funds_verified 105 -> 108, audit 117 -> 120)
- **Sacramento Labs** — Studio / verified / high. "We're not optimizing for exits. We're not chasing unicorn
  status. We're building to own and operate for decades." (sacramentolabs.com/our-philosophy)
- **Waythor** — Studio / verified / med. "We build and hold software companies... we have no exit timelines
  and no external investors... We don't flip companies. We run them. We buy to hold." Named portfolio
  Scallin/Horigam/Dexotal. (waythor.com) [taxonomy rule #3 re-eligible studio]
- **Brooks & Keitt** — **Permanent** (NOT Studio) / verified / med. "We build products to operate them - not
  to sell them... no exit strategy... not for sale." Self-describes "a holding company - not a studio";
  classed Permanent to avoid miscategorization (no-exit holdco that builds). Flagship ProntoID. (brookskeitt.com)

## DEDUP CATCHES -> FLAGS (pre-existing rows; flag-only, NOT edited)
- **Finis Ventures** — already in funds_verified as `held_for_review` (batch10), absent from audit. Raw
  re-verification (finis.ventures: "we build from zero, and we hold long; Self-funded. Operator-led.")
  supports **promoting to verified Studio (in_disguise)**. FLAG: still "does not announce" portfolio.
- **Malpani Ventures** — already in funds_verified as `verified` (batch4), audit_class=**Permanent**. Homepage
  reads as capital-efficient early-stage equity micro-PE ("durability over blitz-scaling... do not force
  growth"), real portfolio (Nexxio/Doco/Clodura.AI SaaS + deep-tech). **RECLASS candidate: Permanent -> Nimble.**

## DOCKET (real but not admitted — your review)
- **LaBarge Holdings** — explicit self-ID ("isn't a venture fund chasing unicorns... own, operate, grow the
  companies we create") BUT **zero named portfolio** on site -> allocator footprint unverified. Re-check later.
- **Perpetun** — build-to-keep studio ("decades not quarters... outlive founders") but **nascent** (3 ventures,
  1 active). Revisit when it has a real operating footprint.
- **Scale Ventures (DE)** — "leading Venture Studio for bootstrapped startups in Europe," anti-VC/bootstrapped,
  but accelerator/founder-program-flavored and hold-vs-exit unclear (a "fast exits?" FAQ). Needs clarification.

## REJECTED (failed a gate)
- **Barek Technologies** — backed by **Sequoia/a16z**, "pour fuel on the fire," placeholder "0 products" stats
  (vaporware tell). Fails anti-unicorn + footprint.
- **Scalable Ventures** — build-to-exit ("position for acquisitions, 4-6yr exit, $1B+ market opportunity").
- **Eagle Venture Studio** — "53% IRR, earlier liquidity" (returns/exit-driven).
- **alphaventurelabs (a-LPHA)** — build-to-**transfer/sell** ("transfer to a buyer"), opposite of build-to-keep.
- **Athanor / Sprinter / Kessel** — nascent / services-flavored / mixed-economy + weak or no anti-unicorn self-ID.

## EXCLUDED (Constellation/CSI family — exclusion gate)
- The Vertus Group (Jonas/CSI), Volaris Group (CSI), Vela Software (CSI).

## OFF-FOCUS (real Permanent allocators; Permanent is saturated -> docket for later, not mined)
- Upliift (UK permanent-equity software, "no fund cycle, no exit mandate"; blog-sourced), Waverock Software
  (founder-led permanent software holdco), Scaleworks (permanent B2B SaaS operator; 3rd-party profile only).

---

# Expansion Round 2 — Nimble + SMV (2026-06-08)

10 searches (5 Nimble + 5 SMV), same gated pipeline. **Key finding: the Nimble/SMV veins are SATURATED** —
almost every hit was already in the atlas, a pure RBF *tool* with no anti-unicorn thesis, or mainstream
growth equity. This confirms the blueprint's yield-decline note: the credible anti-unicorn allocator universe
is finite and largely mined.

## ADMITTED (1 new row; funds_verified 108 -> 109, SMV 16 -> 17)
- **PeakSpan Capital** — SMV / in_disguise / med. "Scale with discipline... not... the growth-at-all-costs
  narrative"; philosophy "Don't Go Chasing Unicorns"; capital-efficient Applied-AI B2B SaaS $3-15M ARR,
  <$20M raised, sub-unicorn $150-500M outcomes. FLAG: dedicated exit-prep function -> exit-driven (in_disguise).

## DOCKET (borderline — your review)
- **TGC Capital Partners** — "not a VC/PE chasing IRR... preserves equity... 30-40% less capital than VC"
  (on-thesis) BUT "hyperscale globally / exponential growth" + heavy services-platform (Gateway Group). Mixed.
- **Founderpath** — non-dilutive RBF ("keep 100% equity"), known prior candidate, but no explicit anti-unicorn
  thesis (it's an instrument). - **FPE Capital** / **Pandl Capital** — bootstrapped-software PE / plateaued-
  software acquirer; borderline exit-model (Permanent-ish), off SMV/Nimble focus.

## REJECTED (no explicit anti-unicorn self-ID — pure RBF tools or mainstream growth equity)
Novel Capital, Float, Financefair, re:cap (RBF tools, serve VC-track companies); Slow Ventures
("something big and important" - still power-law); InfraVia, Regeneration.VC (mainstream/impact growth equity);
Zebras Unite (movement / non-allocator).

## EXCLUDED / DEDUP
- Excluded (CSI): Valsoft. - Dedup (already held): Lighter, Calm, TinySeed, MicroSaaS, Golden Section,
  Expedition, Mainsail, Edited, HASAN, Pemba, Big Band, Recur Software, Malpani, 5X Capital.

---

# EXPANSION TOTAL (both rounds, 2026-06-08)
**+4 new verified rows: 105 -> 109.** Studio 4 -> 6 (Sacramento Labs, Waythor), SMV 16 -> 17 (PeakSpan),
Permanent 66 -> 67 (Brooks & Keitt). Audit 117 -> 121. Plus 2 flags: promote Finis (held->Studio), reclass
Malpani (Permanent->Nimble). **Finding: the credible anti-unicorn allocator vein is largely saturated; Studio
yielded the most NEW names; Nimble is fully mined via these dialects.** Next lever for more Studios: different
dialects (regional/non-US "company builder that keeps", profitable-SaaS-holdco) - many candidates were
build-to-FLIP or a16z-backed and correctly rejected.
