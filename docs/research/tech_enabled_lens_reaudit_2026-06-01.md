# Tech-Enabled Lens — Re-Audit Plan & Insight Synthesis

**Date:** 2026-06-01
**Trigger:** Boss (Ethan) feedback on the Patient-Capital-heavy distribution — introduces a
**tech-enabled** boundary as a first-class research dimension.
**Status:** tech-economy judge pass running over all 850 entities (LLM refinement of the v0 keyword scan).

---

## 1. The reframe (headline)

The project's identity just shifted:

> **Before:** "Capital allocators *outside* unicorn VC."
> **After:** "Capital allocators outside unicorn VC **for tech-enabled companies** — and the
> definition of *tech-enabled* is itself a research contribution."

The atlas is now bounded on **two** sides, not one:

- **UVC** (classic unicorn VC) — the original "too-hot growth capital" contrast.
- **Traditional PE / Real-Economy capital** (NEW) — long-hold / permanent / acquisition capital
  for the **wrong asset**: real estate, restaurants, dental practices, HVAC, home services,
  laundromats, franchises, physical roll-ups. Right *mechanism*, wrong *target*.

The atlas lives in the narrow band between them: **non-unicorn capital for tech-enabled companies.**

---

## 2. Ethan's insights, organized

1. **Patient Capital's ~46% is inflated by traditional PE.** "Long-term hold" caught both genuine
   tech patient-capital and traditional permanent-equity buying real-economy businesses. (Confirmed
   below — only ~28% of Patient Capital is clearly tech.)
2. **Separate traditional PE from tech-enabled** — explicitly. This is the missing filter.
3. **The space is tech-enabled companies.** Not the whole real economy.
4. **The hard problem is the deliverable.** Defining "tech-enabled" (the *Sweetgreen problem* —
   everyone claims to be tech) is, in Ethan's words, "part of the report." The boundary and its
   edge cases are an output, not a pre-processing step.
5. **Tech definition (Ethan v1):** *"A tech startup is a company whose primary innovation and
   scalability come from technology."* Iterative; **Ethan owns refining it.**
6. **Venture Studio is validated and strategic.** Ethan wrote a 2022 Venture Studio whitepaper and
   called the category "extremely relevant." (Probe: it is the cleanest tech category — 0% traditional.)

**Structural insight (how we execute without redoing work):** tech-enabled is an **orthogonal tag**,
not a re-classification. Every entity keeps its mechanism class (Patient / Portfolio / SMV / LMV /
Search-ETA / Sovereign / Venture Studio) and gains a second dimension:
`target_economy in {tech, traditional, mixed, unclear}`. A dental-DSO roll-up is correctly
**Portfolio Capital by mechanism** *and* **traditional by target**. The atlas presents as
**7 classes x tech/traditional**. All prior 7-class and A+ work is preserved.

---

## 3. Final numbers (LLM-judge of all 850, from self-descriptions)

The v0 keyword scan was too lenient. The LLM judges (strict two-prong test + the tech-for-vertical
distinction) produced the definitive split. Overlay file: `data/evidence/target_economy_2026-06-01.csv`.

| Class | n | Tech | Traditional | Mixed |
|---|--:|--:|--:|--:|
| Patient Capital | 257 | **16 (6%)** | 121 (47%) | 120 |
| Portfolio Capital | 156 | 64 | 60 | 32 |
| SMV | 111 | 48 | 29 | 34 |
| LMV | 128 | **95 (74%)** | 1 | 32 |
| Search/ETA | 83 | **1 (1%)** | 55 (66%) | 27 |
| Sovereign | 88 | 11 | 26 | 51 |
| Venture Studio | 27 | **23 (85%)** | 0 | 4 |
| **Total** | **850** | **258** | **292** | **300** |

**Read (Ethan confirmed):** Patient Capital is 47% traditional and only 6% tech; Search/ETA is 66%
traditional and 1% tech (it is SMB acquisition — laundromats, HVAC, dental practices). LMV and
Venture Studio are the tech-pure cores. The tech atlas is ~258 clearly-tech + 300 boundary/mixed;
~292 traditional separate out. QA: zero tech-for-vertical inconsistencies; traditional calls
(Shopify Capital, Wayflyer, search funds) verified correct from their own self-descriptions.

**v0 vs final:** the keyword scan over-counted tech (411 → 258) because allocator marketing uses
software vocabulary even when funding physical businesses — itself evidence for why the LLM-judge
+ the explicit boundary definition are necessary.

**Two caveats — and they ARE the boundary deliverable:**
- **False positives:** "real estate" flagged *Camber Creek* as traditional, but it is **proptech**
  (a tech company serving real estate). The tag must distinguish *tech-for-a-vertical*
  (proptech / fintech / healthtech = **tech**) from *capital-into-the-physical-business*
  (buying actual dental practices = **traditional**).
- **218 "unclear" (26%):** vague self-descriptions that hit no marker — resolved by the LLM-judge pass.

---

## 4. Tech-enabled boundary — operational rubric v1 (for Ethan's refinement)

A company is **tech-enabled** when BOTH prongs hold:

1. **Innovation** — its core product / IP is technology (software, data, AI, platform), not a
   physical good or service that merely *uses* software.
2. **Scalability** — growth comes from software / network leverage (near-zero marginal cost), not
   from adding physical locations, labor, or real assets.

Discriminators:
- **IS-tech vs USES-tech.** Sweetgreen has an app (uses tech) but innovation = salads and scale =
  new locations -> **not** tech-enabled.
- **Tech-for-a-vertical IS tech.** A SaaS/platform serving dentists, landlords, or banks
  (healthtech / proptech / fintech) is tech-enabled. Capital that **buys the dental practice / the
  building / the bank branch** is traditional.

Applied to allocators (the atlas unit): tag by the **companies the allocator funds or acquires.**
- Funds software / SaaS / AI / platform / marketplace startups -> **tech**.
- Buys / operates physical businesses or real assets -> **traditional**.
- Genuinely both, or text too thin -> **mixed** (never guess tech).

> **v1 — owned by Ethan.** Align with his 2022 Venture Studio whitepaper (please share the PDF; it
> can't be read from the working environment). Borderline / mixed cases are surfaced as the report's
> "What is a tech-enabled company?" evidence, not silently bucketed.

---

## 5. Implementation plan

Backbone: an **orthogonal `target_economy` tag**, never a re-classification.

- **Phase 0 — Define the bound** (this doc + the rubric above). The report's intellectual core.
- **Phase 1 — Tag all 850** (RUNNING). Deterministic v0 -> LLM-judge refinement over unclear + mixed +
  proptech false-positive suspects, from existing profiles (no new web fetches).
- **Phase 2 — Data model.** Add `target_economy` column + schema enum. The A+ mechanism classes stay frozen.
- **Phase 3 — Separate, don't delete.** New **"Traditional PE / Real-Economy"** layer parallel to UVC:
  reversible tag, preserved evidence-backed roster, adversarial double-check before any move (false
  positives cut both ways — this is the list Ethan will scrutinize hardest).
- **Phase 4 — Re-present.** 7 classes x tech/traditional; add the 3rd excluded layer; add the
  "What is a tech-enabled company?" section with the MIXED cases as evidence; re-run the boundary
  appendix on the tech-filtered atlas. (The paused packet build is reusable — it just gains the tech dimension.)
- **Phase 5 — Tighten the intake gate** to encode the tech filter so discovery stops re-importing traditional PE.
- **Phase 6 — Grow to ~1,000 tech-enabled entities** via tech-focused discovery rounds through the
  tightened gate. Continue without stopping.

---

## 6. Decisions (resolved 2026-06-01)

- **Borderline / MIXED ->** their own "boundary cases" section (the definition evidence).
- **Timing ->** start the re-audit now on the current 850 AND keep working toward 1,000; do not stop.
- **Unclear (218) ->** LLM-judge refinement from full profile text (running).
- **Open ask for Ethan:** share the **2022 Venture Studio whitepaper** so the atlas's Venture Studio
  definition matches his.

---

## 7. What does NOT change

The 7 mechanism classes, the A+ finalization, the Ecosystem/UVC layers, and the boundary-resolution
appendix all stand. Tech-enabled is added *on top*. No prior work is discarded or re-run.
