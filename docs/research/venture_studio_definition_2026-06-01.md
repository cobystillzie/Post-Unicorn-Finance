# Venture Studio — Definition, Matching Rubric & Discovery Plan

**Date:** 2026-06-01
**Source of truth:** Ethan's *National Venture Studio Model: A framework for securing the future in
the age of innovation sovereignty* (Spring 2022). Extracted text:
`data/runtime/venture_studio_whitepaper_2022_text.txt`.
**Purpose:** Align the atlas's Venture Studio class to Ethan's own definition, and drive a discovery
push to find the large non-US studio population the whitepaper documents — **only adding studios we
can match up properly** (gate + identity audit + adversarial studio-genuineness judge).

---

## 1. Ethan's definition (verbatim, p.7)

> "Venture studios are organizations that align talent, resources, and infrastructure to **generate
> and validate startup ideas quickly, and launch them into the market**. The studio **hires promising
> entrepreneurs**, provides them with proper training, connections, and resources, and grows teams…
> The studio, funded by the community/country, provides money, access, and knowledge for the initial
> iteration of the product. The studio **holds a large percentage of the company**, and thus the model
> is self-sustaining."

Supporting mechanics (p.8): studios "can efficiently **test dozens of ideas per year**, require
**smaller initial investments**," and provide **follow-on funding** so ideas that work get off the ground.

## 2. The size of the prize (verbatim, p.8)

> "It has grown over 600% over the last seven years. Today, there are **almost 600 such studios, half
> of which are outside the United States**, serving a wide variety of interests."

- **Anchor (do not inflate):** ~600 total, **~half (≈300) non-US**, as of **Spring 2022**.
- Treat **~300 non-US as a FLOOR** (2022 figure; the population is larger in 2026). Never invent a count.
- **Atlas today:** 27 Venture Studio entities, mostly US (only ~7 clearly non-US). The gap *is* the work.

## 3. Distinguishing markers — what makes a studio a studio (the matching rubric)

A genuine venture studio satisfies the **build mechanic**, not merely the label "studio." Require
homepage evidence of:

1. **Creates / co-founds companies in-house** — it builds startups itself (ideates, validates,
   spins out), rather than only selecting and funding external founders.
2. **Hires entrepreneurs / EIRs / builds founding teams** — people are brought in to build.
3. **Holds significant equity** — the self-sustaining mechanic (large ownership stake in what it builds).
4. (Supporting) **follow-on funding**, **portfolio of internally-built ventures**, "**venture
   builder / startup studio / company builder / we build & operate**" self-description.

### Anti-patterns — looks like a studio, isn't (→ NOT Venture Studio)

- **Accelerator / incubator** that takes external founders through a cohort program (selects + funds;
  does not co-found in-house) → ecosystem or its funding class, **not** Venture Studio.
- **Ordinary pre-seed/seed VC** that calls itself a "studio" for branding but only writes checks → LMV/UVC.
- **Agency / dev shop** that builds software for clients (no equity, no ventures of its own) → Ecosystem.
- **Holdco / serial acquirer** that *buys* companies rather than *building* them → genuine **Portfolio Capital**.

"Studio" is the most over-claimed label in this space. The verbatim build-mechanic quote is mandatory.

## 4. How studios enter the atlas — promote-as-Portfolio, then reclassify (the "match properly" flow)

The promotion gate has **no Venture Studio class** (`AUTO_PROMOTION_ASSET_CLASSES` lacks it; studio
vocabulary lives under `portfolio_capital_language`). So studios cannot promote *as* Venture Studio
today. The reversible, gate-respecting flow:

1. **Discover** (directory-seeded, non-US weighted) → each candidate web-verified with a verbatim
   homepage quote proving the build mechanic + HQ country.
2. **Inject** with `target_asset_class = "Portfolio Capital"`, `discovered_from = "venture_studio_sweep_<round>"`
   so the cohort is traceable.
3. **Gate** (`inject_and_promote.py`): unchanged. Promotes on name+domain + ≥2 bucket claims (studio
   vocab scores under portfolio_capital_language). Dead/thin/unsupported pages correctly do NOT promote.
4. **Identity audit:** unchanged (distinctive name token on a substantial homepage).
5. **Adversarial studio-genuineness judge (three-way):** run over the **gate-fetched homepage text**
   (richer than the discovery quote), prompted with §1 + §3 above. Verdict per entity:
   - **`Venture Studio`** — homepage proves the build mechanic (creates/co-founds + hires/builds +
     holds equity). **Reclassify** `Portfolio Capital → Venture Studio`; log to
     `data/evidence/manual_changes_2026-06-01.log`. Require a verbatim build-mechanic quote.
   - **`Portfolio Capital`** — genuine holdco/serial-acquirer, not a studio. **Keep.**
   - **`flag`** — VC/accelerator/agency that slipped the gate. Set `review_status=needs_review`;
     do not leave silently mislabeled (CLAUDE.md non-allocator trap).
6. **Tech overlay:** tag `target_economy` (studios are ~85% tech per the re-audit) in
   `data/evidence/target_economy_2026-06-01.csv`.

**Do NOT add a `venture_studio_language` gate bucket mid-run.** Registering Venture Studio as an
auto-promotable class with its own keywords is the correct **Phase-5** gate change — done in isolation
and tested, not during a ~300-entity sweep. Reclassification is fully reversible; a gate change is not.

## 5. Discovery seeding — enumerations, not open search

To reach "almost all" of the non-US long tail (open geographic search finds only the famous studios),
seed agents from real studio **enumerations**, then verify each homepage through the gate:

- **Global Startup Studio Network (GSSN)** member directory.
- **Enhance Ventures — "The Power of Studios"** report (origin of the ~560–600 figure; regional splits).
- Regional / country compilations: "list of venture studios in <country/region>", studio-tracker
  databases, "company builders in <region>".
- Geographic lanes weighted to the non-US population: **Europe** (DACH, Nordics, France, UK, Iberia,
  Italy, CEE), **MENA/Gulf** (UAE/Dubai, Saudi, Egypt), **Latin America**, **Africa**, **India**,
  **Southeast Asia**, **East Asia** (Japan, Korea), **ANZ**.

Each agent returns: `{name, website, hq_country, evidence_quote (verbatim build mechanic), why_studio,
asset_class_guess:"Portfolio Capital"}`. Dedup vs the existing 27 Venture Studio + all Portfolio Capital
entities before injection.

## 6. Innovation-sovereignty note (cross-class)

The whitepaper's thesis is **government-sponsored / national** venture studios (e.g., *Studio Launchpad*
for Dubai DIFC). Sovereign-or-government-backed studios sit at the **Venture Studio × Sovereign Capital**
boundary — flag these for the boundary appendix rather than forcing one class. They are disproportionately
non-US and are exactly the strategic population Ethan cares about.

---

**Standing conditions (unchanged):** gate threshold is not lowered; web-verify every candidate; flag —
don't fabricate; reclassifications are logged and reversible; "passed the gate" ≠ "genuine" — the
studio-genuineness judge is the real filter.
