# Taxonomy — Asset Classes (overhaul, 2026-06-03)

> **[!] 2026-06-07 - PENDING RECONCILIATION WITH ETHAN.** The SMV/Nimble split below is defined here by
> *instrument* (equity vs non-dilutive/revenue-based). Ethan (2026-06-07) instead defines it by *market size +
> liquidity speed* (SMV = large-ish markets, sub-unicorn exit at VC-like-or-better timing; Nimble = smaller
> markets, 3-5yr fast liquidity event). Treat the SMV/Nimble definitions here as PROVISIONAL until reconciled;
> the 22 Nimble + 16 SMV rows are flagged for re-validation. Report structure also gains an "Active Experiments
> vs Trends/Watch" split (empty Reserved classes -> Watch, never dropped). Source of truth:
> `docs/research/ethan_guidance_2026-06-07.md`.

**Status: active overhaul.** Supersedes the prior label set (Portfolio / Patient / LMV / Search-ETA /
Sovereign / SMV-with-camel-modifier — see git history). This is an **outcome/strategy axis** — what kind of
result the capital targets — and is **orthogonal to the verified / in-disguise / provenance tier** (which
captures whether a firm explicitly rejects the power-law / unicorn-exit model). Every entity carries BOTH an
asset class and a tier.

## The classes

| Class | Status | Definition |
|---|---|---|
| **Unicorn Capital** | baseline (excluded) | Power-law investing. The contrast the atlas is defined *against*; never populated. |
| **SMV Capital** | **active** | Small-to-medium venture. Equity targeting venture-scale, **non-unicorn $50M–500M** outcomes. |
| **Nimble Capital** | **active** | Small capital requirements, capital-efficient, rapid scaling, **quick realization** (non-dilutive / revenue-based / micro). |
| **Permanent Capital** | **active** | **No exit required**; no-exit compounding (buy-and-hold holdcos, evergreen, permanent equity, steward). |
| **Studio Capital** (Venture Studio) | **active** | **Systematic company creation** as an investment activity. Studios are now admitted. |
| **Impact Capital** | **active** (added 2026-06-17) | **Tech-enabled mission/impact allocators** with an explicit anti-power-law message (frontier-market & catalytic VC, impact funds). Tech-enabled required going forward; distinct from the reserved Sovereign Capital. |
| **Operator Capital** | **RESERVED** | ≈ search funds / ETA. **Not searched or populated** pending a finalized definition. |
| **Sovereign Capital** | **RESERVED** | Outcomes often have nothing to do with money. **Not searched or populated** pending a finalized definition. |

## Decision rules (locked 2026-06-03)

1. **SMV vs Nimble — by instrument + outcome.** Equity funds targeting ~$50–500M outcomes → **SMV**;
   non-dilutive / revenue-based / micro funds with fast realization → **Nimble**.
2. **Permanent wins the tie.** When a firm is both no-exit *and* capital-efficient, it is **Permanent**
   (no-exit is the stronger structural trait). A small buy-and-hold holdco is Permanent, not Nimble.
3. **Studio admission.** Venture studios (company creation as the investment activity) are admitted —
   this reverses the prior "build-from-scratch = non-allocator" exclusion. Previously-rejected studios
   (Finis, MVP Founders, Waythor, Cone, etc.) are re-eligible and will be re-searched. **[Ratified 2026-06-08: user confirmed build-their-own studios count as allocators - company creation = the investment activity; supersedes the older 'build-from-scratch = non-allocator' hold logic.]**
4. **Reserved classes are parked, not forced.** Entities that primarily belong to Operator or Sovereign
   are flagged **Reserved (candidate)** and left out of the four active classes; impact/steward funds that
   *also* satisfy Permanent's no-exit definition are placed in Permanent with a Sovereign-candidate flag.
5. **Unicorn Capital** is the excluded baseline (the "power-law" distinction we already implement via the
   verified/in-disguise tier). The old "camel" modifier is now subsumed by SMV (equity) / Nimble (non-dilutive).
6. **Impact Capital (added 2026-06-17).** Tech-enabled mission/impact allocators carrying an explicit
   anti-power-law message form their own **active** class — promoted from the Reserved parking lot once a
   real cluster existed. Inaugural member **Rhino Impact Fund**; reclassified in: Delta Fund, Zebra Impact
   Ventures, Village Capital, Bridges Evergreen, Purpose Evergreen Capital, Purpose Ventures.
   **Tech-enabled is required going forward** (Delta Fund is a documented operator/Ethan-vouched non-tech
   exception). Distinct from the still-reserved **Sovereign Capital** (sovereign wealth / DFI / blended).

## Old → new mapping (summary)

- Old **Portfolio Capital** (buy-and-hold software/holdcos) → **Permanent**.
- Old **Patient Capital** (permanent-equity / evergreen / steward) → **Permanent** (steward/impact ones flagged Sovereign-candidate).
- Old **Camel & Capital-Efficient** → split **SMV** (equity, venture-scale) vs **Nimble** (non-dilutive / revenue / micro).
- Venture studios (e.g., Next Wave, MicroSaaS.io) → **Studio**.
- Zebra / impact-first → **Impact Capital** (new active class, 2026-06-17; previously Reserved/Sovereign-candidate).

## Search priority (next phase)

Permanent is already well-populated (~54). Growth targets for the upcoming multi-round search are
**SMV**, **Nimble**, and **Studio** (under-populated). Operator and Sovereign are **not** searched yet.
