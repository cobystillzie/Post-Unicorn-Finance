# Validation docket — SMV / Studio / Nimble vs current definitions (2026-06-08)

**Scope:** all 42 rows currently classed SMV (16), Studio (4), Nimble (22) in
`atlas_asset_class_audit.csv`. **Method:** desk cross-reference of each row's ALREADY-VERIFIED own-site
quote/niche (from `funds_verified.csv`) against the CURRENT taxonomy definitions in `docs/01_taxonomy.md`.
No raw re-fetch this pass; anything the stored quote can't settle is marked RE-FETCH. **Flag-only — no rows
edited.** NOTE: validated against the *provisional* (pre-Ethan) SMV/Nimble definitions; some verdicts flip
once Ethan's market-size/exit-speed reconciliation lands.

## Current definitions used
- **SMV** = equity, venture-scale, **non-unicorn $50M-500M** exit outcomes (NOT defined by capital-efficiency).
- **Nimble** = **non-dilutive / revenue-based / micro**, fast realization + capital-efficient early equity VCs.
- **Studio** = **systematic company creation** as the investment activity (build-to-keep).
- Tie rule: **Permanent wins** (no-exit + capital-efficient -> Permanent, not Nimble/SMV).

## CORE FINDING (the definitional problem this validation exposes)
The SMV/Nimble boundary is drawn **inconsistently**: the word "capital-efficient" appears in the deal-profile
of nearly every SMV row AND is the stated reason most Nimble rows are Nimble. In practice the de-facto line
is: **SMV = bigger-check growth EQUITY into bootstrapped/capital-efficient software aiming at a medium EXIT;
Nimble = micro / non-dilutive / revenue-based + explicitly "camel"-branded early VCs.** That line is not
what the written rule says, and ~6 SMV rows are just *deal profiles* with no explicit unicorn-model rejection,
while ~4 are standard exit-driven PE. **This is exactly the boundary Ethan's input/output (market-size +
exit-speed) model is meant to resolve — so freeze big reclassifications until he answers.**

---

## SMV (16)
**CLEAN / strong anti-unicorn self-ID (4):** Edited Capital ("doesn't fit the unicorn-or-bust model"),
Gearbox Capital ("we reject growth at any cost"), Workhorse Capital ("the unicorn is mythical"),
Startup Ignition Ventures ("Elephants, Not Unicorns"; operator-directed, Ethan-vouched).

**FITS but WEAK self-ID — quote is only a deal/target profile, no explicit model-rejection (6):**
Apex Point Equity, Argentum Group, Invictus Growth, Mainsail Partners, NYO Capital, Updata Partners.
-> Keep as SMV, but flag for a stronger on-page anti-unicorn quote (currently "we back bootstrapped SaaS"
   is VC-compatible on its own).

**RE-EXAMINE class — SMV vs Permanent (1):** Acadian Software — quote emphasizes "prepared to hold for
many years," which leans **Permanent** (holder, not medium-exit-seeker). Re-fetch & decide.

**RE-FETCH — no model-rejection in stored quote (1):** Expedition Growth Capital ("rapidly growing
software & AI") — current quote is growth-positive, not anti-unicorn. Re-verify or downgrade.

**BORDERLINE — genuine bootstrapped focus but standard exit-driven PE (4):** Serent Capital ($6B AUM,
"celebrated our first exit"), Silversmith Capital ($20-125M checks, exit-driven), TVC Capital
(take-privates/roll-ups/recaps), **Pemba Capital (worst: blog-sourced quote, main page = standard
Australian mid-market PE with "liquidity for shareholders" -> lean REMOVE/DOWNGRADE).**
-> These are the integrity risk: "just PE" wearing a capital-efficiency criterion. Re-fetch main positioning
   pages; Pemba is the clearest false-positive.

## Studio (4)  — all 4 are genuinely build-to-keep; class is just thin
**CLEAN (3):** MicroSaaS.io ("build products meant to last - not to flip"), Junagal ("originates, funds,
operates... no exit timeline"), Next Wave Partners ("building forever businesses").
**FLAG — nascent / low-confidence (1):** Noygear/Aware Partners — structurally build-to-keep ("no fund
clock") BUT ventures launch 2026 (pre-deal), founder is a unicorn/exit veteran. Keep-with-flag; re-confirm
when it has live portfolio companies.
*Note: 2 of 4 (Junagal, Noygear) are nascent/solo -> Studio expansion must target ESTABLISHED build-to-keep
studios with real held portfolios.*

## Nimble (22)
**RECLASS -> Permanent (1):** 4D Ventures — "investing our own money; no exit pressure... here for the very
long run (if needed by a generation)." That is **no-exit / generational hold = Permanent** (tie rule).
Strong reclassify candidate.

**RE-FETCH / REMOVE — unverifiable (1):** Capacity Capital — own page returns empty body (confirmed 2x); RBF
instrument fits Nimble but evidence is dead. Browser-verify or remove.

**FLAG — hedged / weak self-ID (2):** STS Ventures ("like most VCs we welcome unicorns... BUT we love
capital-efficient" = NOT an outright rejection -> lean downgrade); Kickstart (provenance tier, no verbatim
quote, previously `not_outright_anti_unicorn`).

**CLEAN / fits Nimble (18):** Bigfoot Capital, BuenTrip Ventures*, BuyBack Ventures, Calm Company Fund
(anchor), Camel Ventures, D2 Fund, Golden Section ("$5-15M rev exit, not a $500M IPO" -> clearly sub-SMV),
Gorilla Capital (anchor), HASAN.VC, henQ, Indie.vc (anchor), Iolar Ventures, Lighter Capital (anchor),
SaaSholic*, TIMIA Capital, TinySeed (anchor), Union Group Fund, UpsideDown VC.
  *blog-sourced evidence URL (BuenTrip, SaaSholic) — fine for now, prefer a positioning-page quote later.

---

## ACTION LIST (flagged, NOT executed — awaiting your direction)
1. **RECLASS:** 4D Ventures Nimble -> Permanent.
2. **RE-EXAMINE class:** Acadian Software (SMV vs Permanent).
3. **RE-FETCH (dead/weak evidence):** Capacity Capital, Expedition Growth, Pemba Capital.
4. **DOWNGRADE / borderline-PE review:** Serent, Silversmith, TVC, Pemba; hedged self-ID: STS Ventures, Kickstart.
5. **STRENGTHEN self-ID (keep, get a better quote):** Apex Point, Argentum, Invictus, Mainsail, NYO, Updata.
6. **HOLD all big SMV<->Nimble moves until Ethan reconciles** the market-size/exit-speed definition.

## Counts after a hypothetical clean-up (illustrative, NOT applied)
SMV 16 -> ~11 clean + 4 borderline-PE + 1 reclass-out... Nimble 22 -> ~19 (−4D Ventures, −Capacity, −STS).
Studio stays 4 (3 solid + 1 nascent). **Net: the credible SMV/Nimble core is solid (~30), Studio is the
thin class that most needs expansion.**
