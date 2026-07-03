# Exit-Framing Research — Plan & Codex Handoff (2026-06-19)

**This doc is self-contained.** A fresh session OR OpenAI Codex should be able to finish the task reading only
this file + the workflow output. It is both the make-plan deliverable and the usage-limit handoff the user asked
for.

---

## 0. Mission & context

Part of **Post-Unicorn Finance** (capital-innovation thesis — see `CLAUDE.md`). This is a **CORE-thesis** research
run (NOT the `economic-impact-study` side study). Question:

> **How are people FRAMING startup/company EXITS?** Find a curated set of **outliers + case studies** around
> (a) **alternative / anti-unicorn exit models** — exit-to-community, EOT/employee-buyout, secondaries/tenders-
> as-exit, search-fund/ETA, holdco/permanent-hold, roll-up "forever home", profit/dividends-as-exit, AND the
> "build-to-keep / no exit / stay private forever / permanent capital" stance — and (b) the **"traditional exit
> is broken/dead"** discourse and what people say is replacing it.

**Locked scope (from the user, 2026-06-19):**
- Angle: **alternative exit models (incl. no-exit/permanent) + "exit is broken" discourse** (NOT mainstream
  IPO/M&A-revival cheerleading).
- Outliers = **both** striking *narratives/takes* AND *firms/funds with a novel exit model they actually use*.
- Voices: **all** (founders/operators, VCs/GPs/LPs, analysts/press/newsletters, employees, + anything relevant).
- Geography: **global**. Time window: **none** — best examples win.
- Count: **as many as are genuinely credible** (quality-gated, not a fixed number).
- Verification: **full adversarial workflow** (fetch + refute each candidate before counting).

## 1. Binding discipline (same as prior runs)
- **Every claim needs a real source_url + a verbatim quote actually seen on that page.** Never invent or stitch
  quotes (a finder in the outliers run stitched a composite quote — caught in verification; do not repeat).
- **Verify before counting.** We caught a viral "Groq made options worthless" claim that was FALSE; default to
  skepticism, fetch the page, write the strongest argument *against* before accepting.
- Distinguish a **distinct exit-framing outlier** from generic VC/exit advice. Generic "how to plan your exit"
  explainers do NOT count.
- **Exclude already-covered baseline facts** (SpaceX IPO, OpenAI tender, Nvidia–Groq, generic Carta secondaries
  stats — all in `economic-impact-study/analysis/state_of_value_participation.md`) UNLESS a genuinely distinct
  framing is attached.
- LinkedIn = **discovery only** (login wall); verify via the primary source.
- End the final output with a **Plain-English summary** (standing user preference — define secondary, EOT, holdco).

## 2. Sources (all free stack — no paid scraping)
X/Twitter (session cookies), web (WebSearch + Exa + Brave), Hacker News, YouTube, GitHub, Substack/newsletters,
company & personal blogs, podcasts (show notes/transcripts), news. ScrapeCreators (paid TikTok/IG/native-Reddit)
is OFF. Reddit reachable via web search.

## 3. The verified-workflow run (ALREADY LAUNCHED)
- **Workflow:** `exit-framing-outliers` · **Task ID:** `w3iwnyv76` · **Run ID:** `wf_a385453d-65e`
- **Script:** `…/c4d4ba47-…/workflows/scripts/exit-framing-outliers-wf_a385453d-65e.js`
- **Output (results land here when done):**
  `C:\Users\cobys\AppData\Local\Temp\claude\C--Users-cobys-projects-post-unicorn-finance\c4d4ba47-0558-41ba-bef7-09b77ab5b5dd\tasks\w3iwnyv76.output`
- **Shape:** 14 finder agents (Discover) → dedupe → adversarial verify (fetch + refute) → synthesize. Returns
  `{ unique_count, survived, verified:[…], synthesis:{ themes, case_studies, plain_english, caveats } }`.
- Finder angles: exit-is-broken; secondaries-as-new-IPO; build-to-keep/no-exit; sell-small/anti-unicorn;
  profit-dividends-as-exit; exit-to-community/employees; permanent-capital holdco; search/ETA/sponsors;
  secondary-liquidity funds; evergreen/structured-exit; roll-up "forever home"; EOT-as-exit-channel;
  X/podcast takes; Substack/blog analysts.

## 4. Phase plan (for re-run or manual execution)
- **Phase 0 — Context (done):** this doc + project `CLAUDE.md` + the two prior verified runs
  (`economic-impact-study/analysis/outliers_and_quiet_signals_2026-06-19.md`,
  `…/state_of_value_participation.md`) establish method + what to exclude.
- **Phase 1 — Discover:** fan out finders by angle/source/voice; each returns real candidates (name, framing,
  source_url, verbatim quote, source_type, region, why_notable).
- **Phase 2 — Verify:** for each unique candidate, fetch the source, confirm the verbatim quote, judge
  `is_alt_or_broken_framing` + `is_distinct_outlier`, write refutation_notes, rate confidence; drop refuted /
  generic.
- **Phase 3 — Synthesize & write:** group survivors by framing theme; write the dated research doc (below).

## 5. Output spec (the deliverable to write when the workflow lands)
Write **`docs/research/exit_framing_outliers_2026-06-19.md`** mirroring the outliers-doc style:
1. Purpose + method (cite run `w3iwnyv76`).
2. **Bottom line** (one paragraph: how are people reframing exits; the most notable shift).
3. **Framing themes** (the distinct exit narratives observed, with example names).
4. **Case studies** — every credible outlier (firms-with-novel-models AND narrative takes), each: profile,
   verbatim quote, link, source_type, framing, why-notable, confidence, limits.
5. **Caveats** (self-reported/single-source/searched-not-found).
6. **Plain English** summary (define secondary, EOT, holdco).

## 6. Anti-patterns / guards
- No invented or stitched quotes; quote only what's confirmed on the fetched page.
- Don't count generic exit advice or already-covered baseline facts.
- Don't conflate a *firm's marketing* with an executed model — flag self-reported/single-source.
- Don't pad to a number; "as many as are credible" can be few.

## 7. CURRENT STATE & NEXT ACTION (read this if you are Codex / a fresh session)
- **State (2026-06-19):** the verified workflow `w3iwnyv76` was launched and is running/likely complete. Session
  was at ~$800 and approaching usage limits — hence this handoff.
- **Next action:**
  1. **Read the output file** (§3 path). If truncated, page through it (it is one JSON object;
     `result.synthesis` holds `themes`, `case_studies`, `plain_english`, `caveats`; `result.verified` holds the
     full per-candidate evidence).
  2. **Write** `docs/research/exit_framing_outliers_2026-06-19.md` per §5, using only verified quotes + URLs.
  3. Optionally add a one-line pointer to it from `docs/research/post_unicorn_finance_research_dossier.md`.
- **If the run never completed / you want to re-run:** in Claude Code, re-invoke the Workflow tool with
  `{ scriptPath: "<§3 script path>", resumeFromRunId: "wf_a385453d-65e" }` (cached agents return instantly).
- **If running in Codex (no Claude Workflow tool):** execute Phases 1–3 manually — for each §3 finder angle, do
  web searches, fetch candidate pages, confirm a verbatim quote, apply §1 discipline + §6 guards, then write §5.
  Keep the adversarial "try to refute each candidate before counting" step.

_Plan + handoff generated 2026-06-19. Pairs with the prior verified runs in `economic-impact-study/analysis/`._
