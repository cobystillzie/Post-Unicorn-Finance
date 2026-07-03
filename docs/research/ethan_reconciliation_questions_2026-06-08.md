# Questions for Ethan — reconciliation + clarification (drafted 2026-06-08)

Send-ready. Derived from the divergences logged in `ethan_guidance_2026-06-07.md`. Goal: lock the
classification rules and report scope BEFORE we re-validate rows or regenerate the Atlas PDF.

Current state for his reference: classification layer = 117 entities (Permanent 66, Nimble 22, SMV 16,
Reserved 6, Studio 4, Excluded-Traditional 3); curated verified track = 105 funds. Permanent is 56% of the
atlas today.

---

## A. CRITICAL — these block classification (need answers first)

1. **SMV vs Nimble — which definition wins?** Our working taxonomy splits them by *instrument* (equity =
   SMV; revenue-based / non-dilutive = Nimble). Your model splits by *market size + liquidity speed* (SMV =
   large-ish markets, sub-unicorn exit at VC-like-or-better timing; Nimble = smaller markets, 3-5yr fast
   exit). Confirm we should **drop the instrument rule and reclassify by your input/output model.**

2. **Where do revenue-based / non-dilutive lenders go?** Under your market-size model, RBF/SEAL lenders
   (Lighter Capital, TIMIA, the "alternative to VC" funds) are an *instrument*, not a market-size thesis.
   Most of our current 22 "Nimble" rows are these. Are they SMV, Nimble, or a separate instrument bucket
   that sits outside the input/output model?

3. **Nimble = "no funds yet"?** You said Nimble is still hypothetical with no funds identified. We currently
   have 22 rows tagged Nimble (by the old instrument rule). Should **Nimble move to the "Trends / Watch"
   section** and those 22 rows be redistributed — or do some genuinely qualify as Nimble under your
   small-market / fast-exit definition?

4. **Can a single fund be both SMV and Nimble?** (You said "figuring it out.") Under the input/output model
   they read as distinct theses. Is each fund exactly **one** class, or can it carry both tags?

5. **Are Permanent Capital and Studio even in your framework?** Your INPUT->OUTPUT model only described
   Traditional VC, SMV, and Nimble — all *VC-style* (early-stage startups -> a liquidity outcome). But **66 of
   our 117 entities are Permanent Capital** (buy-and-hold holdcos that never exit) and 4 are venture Studios.
   Is the report's spine **"alternatives to traditional VC" (SMV/Nimble vs Traditional)**, with permanent-hold
   holdcos as a *different category or out of scope* — or are Permanent and Studio first-class "Active
   Experiments" alongside SMV? This determines whether the majority of the atlas belongs in the report at all.

## B. SCOPE & STRUCTURE — sharpen the report

6. **Rough market-size / liquidity bands.** To make classification operable: roughly what TAM separates
   "large" vs "large-ish" vs "smaller" markets, and what $ range counts as "sub-unicorn" liquidity
   (e.g. <$1B? $50-500M?)? Even ballpark examples per class would anchor it.

7. **Class names for the published report.** You called the labels "hypothetical… helping to give search
   terms." Are **SMV / Nimble / Permanent / Studio** the names you want in the final report, or placeholders
   to be renamed once we see what's actually out there?

8. **Active vs Watch mapping — confirm.** Active Experiments = classes with real funds (proposed:
   SMV, Permanent, Studio); Trends / Watch = empty classes (Operator, Sovereign, and Nimble if it has no
   funds). Is that the split you want?

9. **Reserved classes — search now or stay parked?** Should we start hunting Operator (search/ETA) and
   Sovereign funds now, or leave them parked in Watch until you finalize their definitions?

10. **Tech-enabled scope (written confirm).** We're treating every class as within the tech-enabled sector
    (your 👍). Confirm in writing — and confirm the impact/justice funds you flagged ("related but not the
    focus") stay as **adjacent mentions**, not core admits.

## C. LOGISTICS

11. **Audience & format of the final report** — investor memo / public essay / academic-style? Drives depth
    and tone.

12. **Timeline** — when do you want a first full draft, and is there an interim checkpoint you'd prefer?

---

*Cross-refs: `docs/research/ethan_guidance_2026-06-07.md` (his verbatim directives), `docs/01_taxonomy.md`
(current class defs — pending reconciliation), `docs/post_unicorn_permanent_capital_atlas.md` (current packet,
pre-Ethan structure).*
