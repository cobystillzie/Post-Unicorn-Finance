# Ethan's Classification & Report-Structure Directives — captured 2026-06-07

Source: Slack thread (New Cap Stack), Coby Stillman <-> Ethan. Coby's questions posted "Yesterday"
(2026-06-06 PM); Ethan's replies "Today" (2026-06-07 AM). **These are AUTHORITATIVE** — they define how the
Atlas report is structured and how funds are classified.

- **Section 1 is VERBATIM** (do not paraphrase or "improve" it; typos preserved with [sic]).
- **Section 2 is the plain-language reading.**
- **Section 3 is the integration + open reconciliations.**

---

## 1. VERBATIM (exact — typos preserved)

### 1a. Report structure — re: Operator & Sovereign with no funds
> **Coby (2026-06-06, 7:18 PM):** "I will hold off on finding funds that pertain to operator and Sovereign Capital until there is a more concrete definition"
>
> **Ethan (2026-06-07, 6:38 AM):** "I think the report should separate active experiments from trends or things to look out for. So if we find no fund for soveirgn [sic], it goes in the other section"

### 1b. SMV vs Nimble — separation + Nimble's current status
> **Coby (2026-06-06, 7:31 PM):** "Can an SMV also be nimble? and what would separate nimble from SMV?"
>
> **Ethan (2026-06-07, 6:37 AM):** "We are figuring it out as we go. 2 things. 1) ideally these groupings will be based on actual fund theses 2) nimble was part of several convos I has [sic: had], so no funds yet. The idea was small companies designed for fast liquidity events"

### 1c. The fund-thesis (INPUT -> OUTPUT) model — Nimble is NOT a bag of animal types
> **Coby (2026-06-06, 7:40 PM):** "Is Nimble essentially a compilation of elephant, camels, and Zebras? If i am understanding correctly."
>
> **Ethan (2026-06-07, 6:42 AM):** "No.
> So what's a startup and how does it relate to a fund? A fund is portfolio of startups
> In traditionally vc, that portfolio will be made up entirely of unicorn chasers (input: early stage going after large Markets output : unicorn in 7-10 years). Smv (input : similar to traditional output: sub unicorn liquidity in similar or better timeliness). (nimble input: early stage going after smaller markets output: 3-5 years liquidity event). Again this is all hypothetical and the [sic] helping to give search terms. Ultimately the report needs to include what is actually out there"

### 1d. Tech-enabled scope — confirmed (IMPLICIT)
> **Coby (2026-06-06, 7:11 PM):** "And just to make sure, all of these should be in the tech-enabled sector? I'll be going under that assumption."
>
> **Ethan:** reacted **[thumbs-up]** (👍). This is an *implicit* confirmation of the tech-enabled assumption — NOT a verbal statement. (Also present, non-substantive: "All good, don't worry about it. We will find time".)

---

## 2. PLAIN-LANGUAGE READING

**(A) The report needs TWO kinds of sections.**
- **Active Experiments** — asset-class buckets where we have actually found REAL operating funds.
- **Trends / Things to Look Out For** ("the other section") — buckets that are conceptual/emerging but have
  **no funds found yet**. If no Sovereign fund is found, Sovereign goes HERE — it is **not dropped**.

**(B) Classify funds by their ACTUAL THESIS, not by our invented boxes.** "Ideally these groupings will be
based on actual fund theses." The class labels are "hypothetical... helping to give search terms"; "ultimately
the report needs to include what is actually out there." -> The taxonomy is **search scaffolding**; the report
must describe real funds as they actually describe themselves.

**(C) How to tell fund classes apart — the INPUT -> OUTPUT model.** A fund = a portfolio of startups. Classify
the fund by (INPUT) the kind of startups it backs and (OUTPUT) the liquidity outcome it targets:

| Fund class | INPUT (startups it backs) | OUTPUT (target outcome) |
|---|---|---|
| Traditional VC | early-stage, going after **large** markets | a **unicorn ($1B+)** in **7-10 years** |
| **SMV** | **similar to traditional** (early-stage, large-ish markets) | **sub-unicorn** liquidity, in **similar or better** timing |
| **Nimble** | early-stage, going after **smaller** markets | a **3-5 year liquidity event** (fast exit) |

-> **What separates Nimble from SMV (Ethan's direct answer):** the **market size** of the target startups
(smaller vs large-ish) AND the **speed of liquidity** (fast 3-5yr event vs sub-unicorn at VC-like-or-faster
timing). It is **not** about the financing instrument.

**(D) Nimble is NOT "elephants + camels + zebras."** Those animal metaphors describe **startups**; fund classes
describe **theses**. Nimble = "small companies designed for fast liquidity events," and per Ethan it currently
has **no funds identified yet** (it came out of conversations; still hypothetical to him).

**(E) Tech-enabled scope confirmed** (👍).

---

## 3. INTEGRATION + OPEN RECONCILIATIONS

### Adopt now (consistent with Ethan):
1. **Report = "Active Experiments" + "Trends / Watch" sections.** Map the atlas's **Reserved** classes
   (Operator, Sovereign — "not searched/populated pending definition") to the **Trends/Watch** section. The
   populated classes (SMV, Nimble, Permanent, Studio) form the **Active Experiments** section. An empty class
   is parked in Watch, never dropped.
2. **Thesis-based classification is the rule.** Classify each fund by its OWN stated thesis (input market +
   output liquidity), per Ethan. This reinforces the self-description-classification phase and the
   "report what's actually out there" / drop-quota stance set 2026-06-07.
3. **Tech-enabled gate stays** (Ethan 👍).

### [!] RECONCILE — Ethan's SMV/Nimble definition DIVERGES from the current taxonomy (do NOT auto-reclassify; put to Ethan/Coby):
The current taxonomy (`docs/01_taxonomy.md`) splits **SMV vs Nimble by INSTRUMENT**:
- SMV = "equity targeting venture-scale $50-500M outcomes"; Nimble = "non-dilutive / revenue-based / micro,
  fast realization."

Ethan splits them by **MARKET SIZE + LIQUIDITY SPEED** (instrument-agnostic):
- SMV = large-ish markets, sub-unicorn exits at VC-like-or-better timing; Nimble = **smaller markets, 3-5yr
  fast liquidity** (an early-stage equity VC thesis, not a financing-instrument category).

**Consequence - the biggest open item:** the atlas's current **22 "Nimble" entities** were classified by the
*instrument* rule (mostly revenue-based lenders + capital-efficient micro funds - e.g. Lighter, TIMIA, camel
VCs). Under **Ethan's** definition, "Nimble" means **small-market, fast-exit, early-stage (equity) VC** - a
different set - and Ethan says Nimble has "no funds yet." So the label "Nimble" currently means different
things to the atlas vs to Ethan. **Action:** reconcile the SMV/Nimble definition with Ethan FIRST, then
re-validate the 22 Nimble + 16 SMV rows against the agreed input/output definition. **Flagged, not executed.**

### Open question to put back to Ethan:
- *"Can an SMV also be Nimble?"* - Ethan did not answer directly ("we are figuring it out"). Under the
  input/output model they read as distinct theses (a fund is one or the other), but confirm whether a single
  fund can carry both tags.

---

*Cross-refs: `docs/01_taxonomy.md` (current class defs - pending reconciliation), CLAUDE.md / AGENTS.md
(operating rules), `docs/research/classification_validation_2026-06-07.md` (the SMV-Nimble boundary was
already the empirical weak spot - Ethan's input/output model is the intended resolution axis).*
