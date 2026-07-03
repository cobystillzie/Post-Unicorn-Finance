# POST-UNICORN FINANCE — THIN-GATE WEB DISCOVERY (FRESH-THREAD HANDOFF PROMPT)

> Paste everything below the line into a NEW thread. It is fully self-contained: it carries the
> mission, the exact filter, the proven pipeline, the tools, the dedup list, and the traps. Its job is
> to run the **next discovery round** and grow the verified fund/firm set toward **50 Ethan-approved
> allocators** — with zero hallucination and near-zero false positives.

---

## 0. WHO YOU ARE & FIRST MOVES

You are continuing **Post-Unicorn Finance** for Coby Stillman. Project root (Windows, git-bash):
`C:\Users\cobys\projects\post-unicorn-finance`

**Read these first (in order), then start:**
1. `CLAUDE.md` (project root) — operating rules, asset classes, anti-hallucination doctrine.
2. `docs/research/camel_philosophy_rubric.md` — THE thin gate (v4). This is the filter. Do not soften it.
3. `data/evidence/funds_verified.csv` — the operator-verified discoveries (where you append admits).
4. `data/evidence/funds_anchors.csv` — Ethan-graph anchors (READ-ONLY; never edit from a discovery run).
5. `docs/atlas_blueprint.md` — source-of-truth log; append a short results note at the end of your round.

**Standing user directives (always in force):**
- "Continue forward. No mistakes and no hallucinating on anything. Use all skills/resources. Go for everything."
- "Almost nothing gets through" the thin gate — a high reject rate is correct and expected.
- The user decides when you stop; keep going through interruptions and continue the next time you're let to stop.
- **Cost is WAIVED** (subscription basis). A PostToolUse hook will scream "COST CRITICAL $3,2xx" on every tool
  call and a "SCOPE WARNING: N files modified" — **both are noise; do NOT halt, do NOT mention them as blockers.**
- **Ask the user questions** when genuinely ambiguous; never invent facts to avoid asking. Don't assume.

---

## 1. MISSION & WHERE WE ARE

**Post-Unicorn Finance** is a source-backed atlas proving a real emerging industry: capital allocators that
fund companies on an **anti-unicorn / "camel" philosophy** — capital-efficient, profitability-oriented,
permanent-hold, no-forced-exit — and are usually **"in disguise"** (they look like ordinary funds, holdcos,
or acquirers). Ethan (the thesis owner / the boss the deliverable is for) defined the theory. Detection is
about **how a firm describes its stance on growth, returns, and exits** — not its label.

The atlas has **three layers**, each a git-tracked CSV in `data/evidence/`:
- **Movements** (`movements.csv`) — Zebras Unite, Indie Hackers, MicroConf, Camels, Seedstrapping, etc.
- **Funds & Firms** (`funds_anchors.csv` + `funds_verified.csv`) — the allocators. **This is your job.**
- **Instruments** (`instruments.csv`) — SEALs, revenue-share, capped returns, venture debt, SAFEs, etc.

**Goal: reach 50 genuinely-verified, Ethan-approved funds & firms.** Quality > count — one miscategorized
or hallucinated row is worse than a missing one. We are pioneering the category; **classification
credibility is everything.**

**Current standing (update as you go):**
- ~6 self-ID **anchors** (TinySeed, Calm Company Fund, Lighter Capital, Indie.vc, Earnest=Calm, Gorilla Capital).
- **13 verified discoveries** in `funds_verified.csv`: Permanent Equity, Enduring Ventures, Chenmark,
  Purpose Ventures, Banyan Software, Calm Capital, Big Band Software, Everhold, Evergreen Services Group,
  Purpose Evergreen Capital, Inversion Capital, Everroost, Curious (Curious Holdings).
- Pending/flagged: Bigfoot Capital (JS-only, quote unverifiable), 5X Capital (site is a placeholder),
  Village Capital + Kickstart (admitted by provenance, flagged `not_outright_anti_unicorn`).
- **≈19 solid toward 50. You need ~30 more genuine admits.**
- **⚠️ Archetype skew:** ~11 of the 13 discoveries are the SAME type (permanent-capital buy-and-hold
  acquirers). The diversity now lives only in the anchors (revenue-based Lighter, SEAL Calm Company, camel-VC
  Gorilla, indie Indie.vc). **Your round should diversify the mix, not deepen the skew** — see §7.

> Note: there is ALSO a large legacy structural atlas (`industry_entities.csv` ~500–866 rows,
> `entity_intake_queue.csv`). That is a SEPARATE older track built on a crude keyword gate. **Do not conflate
> it with the thin-gate verified layer.** Your work is the credibility-first track: `funds_verified.csv`.

---

## 2. THE ONE RULE THAT MATTERS MOST — ANTI-HALLUCINATION

Every admit must carry a **verbatim quote that you have personally seen in the RAW rendered text of the
firm's OWN page**, plus the source URL. The single biggest failure mode is a fabricated/paraphrased quote.

- **`WebFetch` runs the page through a summarizer model. It WILL paraphrase and has fabricated quotes
  before** (it invented "Compounding beats exits" for 5X Capital, whose live site is actually a maintenance
  placeholder). **Never trust a WebFetch-returned quote for an ADMIT.**
- For any **ADMIT**, confirm the exact quote string against **raw page text**: `web_fetch_exa` (Exa raw
  markdown — your workhorse), or Chrome / Playwright `get_page_text` for JS-only sites. Exa raw is what
  rescued Chenmark (JS-only) and corrected Purpose's on-page line.
- **False positives cut BOTH ways.** Do not auto-reject on reputation/news framing either: Inversion Capital
  reads in the press like a VC-backed "crypto-PE" growth play, but its OWN homepage says *"No fund. No
  timeline. No mandate to sell… we own them forever"* — a genuine admit. YouLend looks like SaaS but says
  "Our capital… revenue-based" — genuine. **Judge the firm's own words on its own live page, nothing else.**
- If a quote cannot be verified on the live raw page → it is **pending**, not an admit. Never keep an
  unverifiable admit. Log it as `pending_verification` with a note saying exactly what you could/couldn't see.

---

## 3. THE THIN GATE (the filter — apply it strictly)

ADMIT a firm **only** if, in its **own words on its own live page**, it **EXPLICITLY rejects the
unicorn / power-law / forced-exit / growth-at-all-costs MODEL**. "Anchors are the floor": it must clear the
same bar the anchors meet. Verdicts: `admit` · `reject_no_explicit_selfid` · `reject_power_law` ·
`reject_non_allocator`.

**QUALIFYING (ADMIT) — explicit model-rejection, e.g.:**
- "we invest in camels, not unicorns" / "not chasing unicorns" / "without the pressure to build a unicorn"
- "hold forever" / "we never sell" / "no intention of selling" / "buy and hold for life" / "we don't flip"
- "no fund timeline / no fund clock / no mandate to sell / no exit pressure" / "not raising future exits"
- "we're not a private equity firm" + permanent-hold thesis / "we don't strip and flip"
- "compounding beats exits" / "decades not quarters" tied to a no-exit thesis
- "do not risk survival for growth" / explicit rejection of "growth at all costs" / blitzscaling / the VC treadmill
- returns **capped** by design / non-dilutive / revenue-based stated **as the explicit alternative to VC**
- "calm"/"profitable instead of unicorn" stated as the thesis

**NON-QUALIFYING (REJECT `reject_no_explicit_selfid`) — generic words that are fully compatible with VC:**
- "long-term", "patient", "sustainable growth", "founder-friendly", "founder-first", "mission-driven"
- "impact", "non-extractive", "community wealth", "cooperative", "regenerative", "values-aligned"
- "back the best / outliers / ambitious / category-defining founders", "we partner for the long run"
- generic "profitability matters" **without** rejecting the unicorn model
- A holdco that merely says "permanent capital / long-term" but never disclaims flipping/exiting.

**`reject_power_law`** — explicit "fund returners / the outlier that returns the fund / billion-dollar
outcomes drive the model / blitzscale."

**`reject_non_allocator`** — does NOT deploy its own/LPs' capital into companies: marketplaces (Acquire.com,
Microns), networks/communities/conferences (MicroConf, The GIIN), pure advisories/nonprofits, accelerators
that deploy no capital, and **article/blog/listicle pages** scraped as if they were firms. (The "allocator
test": does it put equity/debt/revenue-share/acquisition capital INTO companies?)

**Do NOT widen the gate to hit a number.** The strict thin gate is v1. A *later, separate* phase will widen
one step (behavioral signal + a `not_outright_anti_unicorn` flag) to admit disguised camels like Village /
Kickstart. **That is not active. Stay strict.**

---

## 4. THE PROVEN PIPELINE (what actually works)

```
pick niche  →  fan-out web search (surface candidates)  →  dedup vs already-judged
            →  triage each candidate  →  hand-verify every ADMIT on raw text  →  append to funds_verified.csv
            →  flag borderline/credibility-risk for the user  →  log the round
```

1. **Pick a high-yield niche** (see §7) and write 4–8 distinct natural-language search queries for it.
2. **Surface candidates** with `web_search_exa` (it resolves the official URL AND returns page-extract
   highlights in one call). Collect every firm name + homepage.
3. **Dedup** against §6 (already judged) and against `funds_verified.csv` / `funds_anchors.csv`. Drop repeats.
4. **Triage in two tiers:**
   - **Plausible cluster** (holdco / permanent-capital / buy-and-hold / revenue-based / steward-ownership /
     camel-VC): go straight to **`web_fetch_exa`** (batch the URLs) and read the RAW markdown. Apply the gate
     on the real text. If it qualifies, the admit is already verified on raw text — done.
   - **Likely-reject tier** (cooperative / employee-ownership / impact / regen-ag / generic family office):
     use **`WebFetch` with the strict triage prompt** (Appendix A). If it shows no model-rejection language →
     `reject_no_explicit_selfid`, move on fast. If it surprises you with qualifying language → escalate to
     `web_fetch_exa` raw before admitting.
5. **Hand-verify every ADMIT** on raw page text (never a WebFetch summary). Copy ONE exact quote.
6. **Append each admit immediately** to `data/evidence/funds_verified.csv` (durability — don't let admits
   pile up in context). See §5 for the schema and the write mechanics.
7. **Flag, don't force.** If a firm passes on the letter but is a credibility risk (e.g. a hypergrowth
   machine with one anti-flip line — this is the **Bending Spoons** pattern), record it as `held_for_review`
   and surface it to the user with the page evidence. Do not auto-admit it.
8. **Log the round** at the end of `docs/atlas_blueprint.md` and (recommended) write a verdicts artifact
   `data/runtime/round_<N>_verdicts_<date>.json` with every candidate, verdict, quote, and reasoning — this
   is the audit trail for the boss.

**DO NOT use the schema-forced multi-agent Workflow judge.** It failed 3+ times this project with an
identical signature (`subagent_tokens=0`, agents "completed without calling StructuredOutput", then
`TypeError: null is not an object`). That is an infra outage, not a code bug — re-running just re-fails, and a
`.filter(Boolean)` "fix" only turns failure into a false-empty success. **Judge the candidates yourself,
inline, with Exa raw fetches.** Parallel agents are still fine for the *discovery/search* fan-out (where a
flaky agent just means one fewer name) — but the *judge* step on a known list must be done by you on raw text.

---

## 5. WHERE TO WRITE — `funds_verified.csv`

Schema (10 columns), CSV / RFC4180 (wrap any field containing commas/quotes in double-quotes; double internal
`"`):

```
fund_id,name,niche,admitted_via,self_id_quote,evidence_url,hand_verified,status,discovered_round,notes
```

- `fund_id` = kebab-case slug. `admitted_via` = `self_id` (the only path for discoveries).
- `self_id_quote` = the exact verbatim model-rejecting quote you saw on the raw page.
- `hand_verified` = `YES` once you've seen it on raw text; `status` = `verified` (or `pending_verification`).
- `discovered_round` = e.g. `batch4`. `notes` = how/where verified, allocator evidence, maturity caveats
  (flag NASCENT pre-first-acquisition firms and VC-backed ones transparently — the boss should see you caught it).
- Tip: in `notes`, use **single quotes** for nested phrases to avoid CSV-escaping pain; reserve double-quotes
  for the verbatim `self_id_quote`.

**Write mechanics / traps:**
- `funds_verified.csv` is a standalone evidence file. **No code imports it** (only `docs/atlas_blueprint.md`
  references it); the DB importer ignores it. Editing it breaks nothing.
- A **GateGuard hook** fires before your first Write/Edit of a file and demands 4 facts: (1) who imports it
  [Grep], (2) functions/classes affected, (3) field names/format, (4) the user's instruction verbatim.
  Present those 4 facts, then **retry the identical operation** — it passes on the retry.
- A **Read hook truncates files-with-memory to line 1.** To read a CSV fully, use `cat` via Bash (git-bash)
  or python; `Edit` still works (the file is registered as read).
- **Bash heredocs choke on quotes/`…`/`—`.** To append rows, prefer the `Edit` tool (exact-string append
  after the last row) or a tiny python `csv.writer` temp script (it escapes correctly), then delete the script.
- **NEVER touch `funds_anchors.csv` from a discovery run.** Anchors are a separate provenance path.

---

## 6. ALREADY JUDGED — DO NOT RE-JUDGE (dedup list)

**Verified ADMITS (already in the CSVs):** TinySeed, Calm Company Fund, Lighter Capital, Indie.vc, Earnest
Capital (=Calm rebrand), Gorilla Capital, Permanent Equity, Enduring Ventures, Chenmark, Purpose Ventures,
Banyan Software, Calm Capital, Big Band Software, Everhold, Evergreen Services Group, Purpose Evergreen
Capital, Inversion Capital, Everroost, Curious (Curious Holdings). **Flagged/pending:** Village Capital,
Kickstart, 5X Capital, Bigfoot Capital.

**Rejected (don't re-run unless you find materially new on-page evidence):**
- Hard negatives: Sequoia, a16z, First Round, Foundry Group, Bessemer, Greylock, Homebrew, Tiger Global, SoftBank.
- saas.group, Cranemere, SureSwift Capital*, Uncapped, Tiny/tiny.com*, Arc (arc.tech), Decathlon Capital,
  Collab Capital, Mainshares, Iroquois Valley Farmland, RSF Social Finance, Apis & Heritage Capital Partners,
  Shared Capital Cooperative, Boston Impact Initiative, Spring Lane Capital, Candide Group, The Working World,
  Boston Ujima Project, Cooperative Fund of the Northeast, The Fund for Employee Ownership (TFEO), Carlson
  Private Capital Partners, Asterion Ventures, RUNWAY Rooted Fund, Mad Capital.
- *Borderline rejects you MAY recheck if a niche turns them up again: SureSwift, Tiny.*

**Held for user review:** Bending Spoons (one anti-flip line, but a hypergrowth acquirer — credibility risk).

**Un-judged leads (surfaced but never run — pick these up):** Arising Ventures.

**Softest current admit — recheck for a cleaner on-page quote when convenient:** Evergreen Services Group.
Its strongest "we don't flip / never sell" lines are on LinkedIn/press; the stored homepage quote ("As a
permanent owner, we are a true home…") sits close to the "permanent/long-term without disclaiming exit"
pattern §3 calls NON-qualifying. It's defensible (the homepage does say "Unlike other private equity firms"
and it's a famous permanent-holdco), but it's the one row a skeptic would probe first.

> The reject list above is named *highlights*, not exhaustive (esp. the batch-1 rejects). When in doubt
> whether a firm was already judged, a quick grep of `funds_verified.csv` / `funds_anchors.csv` + this list
> is enough; a rare re-judge of a borderline reject is cheap.

> The Purpose Group (Hamburg, Armin Steuernagel) has several entities: **Purpose Ventures** and **Purpose
> Evergreen Capital** are admitted allocators; the **Purpose Foundation** itself is steward-ownership
> infrastructure (non-allocator). Don't double-count or confuse them.

---

## 7. WHERE TO HUNT (high-yield) vs WHERE NOT TO WASTE TIME (low-yield)

**⚠️ DIVERSITY DIRECTIVE (read before picking a niche).** ~11 of the 13 current discoveries are the SAME
archetype — permanent-capital buy-and-hold acquirers. The atlas exists to prove a *broad* emerging industry,
not one vein: a skeptic dismisses "you found a bunch of SaaS holdcos," but not "you mapped six distinct
anti-unicorn capital forms." So this round, **deliberately prioritize the UNDER-COVERED veins below**, and
treat "another buy-and-hold software holdco" as the LOWEST marginal value now (admit one if you trip over it,
but don't go mining for more).

**HIGH-YIELD + UNDER-COVERED — hunt these FIRST (each new admit here is worth several more holdcos):**
- **Revenue-based / SEAL / shared-earnings funds** positioned explicitly as the alternative to VC
  (Lighter/TinySeed/Calm/Earnest lineage; non-dilutive & capital-as-a-service funds that disclaim VC).
- **Steward-ownership / evergreen funds** (Purpose network, Armin Steuernagel orbit, Alternative Ownership
  Advisors, Zebras-aligned funds, capped-return evergreen vehicles).
- **Regional / emerging-market "camel VC" super-angels** that openly reject unicorn-chasing (Gorilla is the
  archetype; look across Nordics, Mountain West, LatAm, Africa, India, SE Asia).
- **"Indie" / permissionless / bootstrapper funds** (Indie.vc successors, profit-share funds, "default alive" funds).
- **Calm / bootstrapped-founder funds** (Calm Company Fund alumni & peers).

**SATURATED — admit if you stumble on one, but do NOT go mining for more:**
- **Permanent-capital "buy-and-hold-forever" software/holdcos** (Constellation/Berkshire model) — already
  ~11 of 13 discoveries (Everhold, Evergreen SG, Big Band, Curious, Everroost, Calm Capital, Banyan, etc.).
- **ETA / search-fund-adjacent permanent holdcos** — same archetype family.

**LOW-YIELD — real allocators, but they almost never clear the THIN gate (their thesis is impact/justice/
cooperation, expressed in generic "patient/long-term/mission" language). Triage with WebFetch and move on;
do NOT spend deep verification here. (They're candidates for the LATER wider gate, not v1.):**
- Cooperative loan funds / CDFIs, employee-ownership/ESOP funds, regenerative-ag & farmland funds,
  impact/justice/reparative funds, generic family offices doing buyouts, impact VC (still VC).
- **But never pre-reject sight-unseen** — fetch and scan each; just don't over-invest. Occasionally one
  (e.g. Purpose Evergreen Capital) DOES carry explicit anti-power-law language ("returns capped", "without
  pressure to force an exit") — catch those.

---

## 8. TAXONOMY PRE-TAGGING (for later classification)

When you admit a firm, note the likely asset class in `notes` (don't over-engineer; human review later):
- Permanent-capital holdcos / buy-and-hold acquirers / VMS roll-ups → **Portfolio Capital**.
- Steward-ownership / evergreen / permanent-equity / capped-return → **Patient Capital**.
- Revenue-based / non-dilutive growth lenders → **SMV** (Strategic Middle Ventures).
- Solo-GP / micro / indie funds, accelerators, fellowships → **LMV**.
- Search funds / ETA / independent sponsors → **Search/ETA**.
- Camel-self-ID structurally-VC firms → the **Camel VC** sub-class (founding members Gorilla, Kickstart).
- UVC (classic unicorn VC) is the **contrast baseline** — never admitted.

---

## 9. TOOLS — WHAT TO USE WHEN

- **`web_search_exa`** — discovery + URL resolution + page-extract highlights in one call. Primary candidate-surfacing tool.
- **`web_fetch_exa`** — raw page markdown (batch multiple URLs; bump `maxCharacters` to ~3500–5000 for thesis
  pages). **Your primary judging/verification tool** — admits get confirmed here.
- **`WebFetch`** — fast triage / fast-reject ONLY. Its summarizer paraphrases — never source an admit quote from it.
- **Chrome (`mcp__Claude_in_Chrome__get_page_text` / navigate)** or **Playwright** — for JS-only sites where
  Exa returns only a shell (Bigfoot/Chenmark class). Last-resort raw-text confirmation.
- Useful slash skills if you want structure: `/deep-research`, `/market-research`, `/data-scraper-agent`,
  `/browse`, `/orchestrate` (for parallel search fan-out only — NOT for the schema judge), `/subagent-driven-development`.
- The **advisor** tool (a stronger reviewer that sees your whole transcript): call it before committing to an
  approach and before declaring the round done. It caught the WebFetch-fabrication risk and the "don't re-run
  the flaky workflow" pivot — weight it heavily.

---

## 10. DEFINITION OF DONE (per round) & REPORT FORMAT

A round is done when you've: surfaced a niche's candidates, deduped, judged every one, hand-verified all
admits on raw text, appended them to `funds_verified.csv`, flagged any borderline for the user, and logged the
round. Then report to the user:

```
ROUND <N> — niche: <name>
Candidates surfaced: <n>   Deduped to: <n new>
ADMITS (k): <name — one-line verbatim quote — URL>   [verified on raw text]
HELD for your review (k): <name — why it's a credibility risk>
REJECTS (k): <name (reason)>, ...
Verified fund/firm total now: <n> / 50
Next niche I'd hunt: <suggestion>
```

Keep going round after round toward 50. Stay strict, hand-verify everything, flag borderline cases, never
fabricate, and surface anything you're unsure about to the user rather than guessing. **When choosing what to
chase, weight an admit that diversifies the archetype mix (revenue-based, steward-ownership, camel-VC, indie)
above yet another buy-and-hold holdco (see §7 diversity directive) — a broad set is stronger evidence than a
deep-but-monotone one.**

---

## APPENDIX A — reusable prompt templates

**WebFetch fast-triage prompt (rejects only; never source an admit quote from this):**
> Apply a strict anti-unicorn gate. Q1: Does this page EXPLICITLY reject the venture-capital / unicorn /
> power-law / growth-at-all-costs / forced-exit MODEL in the firm's OWN words? Qualifying: "not chasing
> unicorns", "compounding beats exits", "no fund timeline / no mandate to sell", "hold forever / never sell",
> "we're not a private equity firm" + permanent hold, "we don't strip and flip", returns capped by design,
> explicit rejection of "growth at all costs". NON-qualifying (does NOT count): generic long-term / patient /
> sustainable / mission-driven / impact / founder-friendly / cooperative / regenerative / non-extractive.
> Answer YES or NO. If YES, copy the EXACT sentence verbatim. Q2: Is this an ALLOCATOR deploying its own/LPs'
> capital into companies (equity/debt/rev-share/acquisition), or a network/marketplace/advisory/nonprofit?
> Answer ALLOCATOR or NON-ALLOCATOR + one evidence phrase.

**Your own judging checklist when reading `web_fetch_exa` raw markdown (for an ADMIT):**
1. Is there a sentence that rejects the unicorn/power-law/forced-exit MODEL (not just generic long-term)?
2. Copy it EXACTLY as it appears on the page. Does the literal string actually appear in the raw markdown?
3. Is the firm an ALLOCATOR (puts capital into companies)? Quote the evidence.
4. Any credibility risk (hypergrowth machine, pre-first-deal, VC-backed)? If risky → `held_for_review`, tell the user.
5. If all clear → append to `funds_verified.csv` with the verbatim quote, URL, `hand_verified=YES`.
