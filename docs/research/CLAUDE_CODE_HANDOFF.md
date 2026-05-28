# Claude Code Handoff — Post-Unicorn Finance self-description / taxonomy work

_Written 2026-05-27 from a Claude Cowork session. Hand this whole file to Claude Code._

## 1. What this session set out to do

Goal (from the user, Coby): stop forcing entities into the predefined asset classes and instead **derive real asset classes bottom-up** from how non-unicorn capital entities describe *themselves* — in the atlas AND on the open web. The existing classes (SMV, LMV, Patient Capital, Sovereign Capital, Search/ETA, Portfolio Capital, Camel, Instrument) are **placeholders** to be validated, renamed, merged, or split once genuine commonality is proven. Hard rules: no hallucination, every self-description tied to real captured/fetched text, ask rather than assume.

## 2. What was actually done (and is sitting in the working tree)

Grounded analysis (read-only, in `data/analysis/`):
- `entity_self_descriptions.csv` — per-entity self-description corpus (109 fetched `source_pages` + structured fields).
- `phrase_signals.csv` — recurring multi-word self-description phrases (entity_count, occurrences).
- `clusters.json` — 91 clusters; 9 of size >=3.
- `verbatim_snippets.json` — raw page text per entity for traceability.

New scripts (`scripts/`): `mine_self_descriptions.py`, `cluster_self_descriptions.py`, `validate_placeholders.py`, `build_terms_dashboard.py`, `append_discovery.py`.

Deliverables: `docs/research/self_description_taxonomy_findings.md` (the findings + proposed reiterated taxonomy), `site/self_description_terms_atlas.html` (interactive dashboard).

Edits to existing files:
- `scripts/research_agents.py` — expanded `KEYWORD_GROUPS` (enriched all groups; **added new `permanent_steward_language` group**) and `CLASS_KEYWORDS`. **NOTE:** during editing the file's `main()` dispatch tail was accidentally truncated by a tool write and then repaired from `git HEAD`. Please re-verify integrity: exactly one `if __name__ == "__main__"`, one `args = parser.parse_args()`, one `if args.command == "discover":`; `python -c "import ast,sys; ast.parse(open('scripts/research_agents.py').read())"` should pass; `git diff HEAD -- scripts/research_agents.py` should show only additive vocabulary changes (~+90/-5).
- `data/evidence/scrape_targets.csv` — +4 lanes (permanent/steward, embedded finance, studios, employee-ownership ETA).
- `data/evidence/entity_intake_queue.csv` — +7 leads: Everhold & Purpose Evergreen Capital as `candidate_evidence` (own-site text fetched & quoted); HOLD.co, Upliift, Bending Spoons, Fund for Employee Ownership, Evergreen (evergreensg.com) as `queued`/`needs_verification`. All `lead_type=web_search_result`, `review_status=queued`, lead_ids `intake-web-2026-05-27-00X`.
- `data/evidence/source_registry.csv` — +7 source rows for the above.

Verification done in-session: `python scripts/validate_evidence.py` → **passed**; data imports cleanly to a temp SQLite (169 entities / 51 intake / 17 scrape_targets / 236 source_registry); **35 tests passed** (`test_sqlite_pipeline`, `test_validation`, `test_learning_ops`, `test_repo_hygiene`).

## 3. What Cowork could NOT do — please do these in Claude Code (local env)

The Cowork sandbox is a separate Linux VM (Python 3.10) with the repo *mounted*; several operations the mount/permissions/version blocked:

1. **Rebuild `data/atlas.sqlite`.** The mount won't let the sandbox `unlink` the existing file (`PermissionError: Operation not permitted`). Run locally: `python scripts/atlas_sqlite.py build` then `python scripts/atlas_sqlite.py validate --strict-verified-sources`.
2. **Run the full pytest suite.** Sandbox Python 3.10 cannot even *collect* `tests/test_publish_packet.py` because `scripts/export_research_dossier.py:101` has an f-string containing a backslash (`re.sub(r'^\d+\.\s+', ...)` inside an f-string) — illegal in 3.10, **legal in 3.12+** (your machine). I never touched that file. On local 3.12+, run the full `python -m pytest -q`. (Optional: make it 3.10-safe by hoisting the regex out of the f-string, if you ever want CI on 3.10.)
3. **Clean up stale exports.** `data/exports/asset_class_rankings_sqlite/*.csv` couldn't be rewritten (same permission wall). The ranking/export steps will run fine locally.
4. **Commit/push.** `.git/index.lock` wasn't writable. Review `git diff` and commit locally.
5. **Run the PowerShell cron scripts** (`scripts/run-*.ps1`) — not available in the Linux sandbox; they'll run on your Windows machine.

## 4. Caveats about the working tree (so you don't misattribute changes)

`git diff --name-only HEAD` shows extra "modified" files I did **not** edit: `asset_classes.csv`, `entity_claims.csv`, `industry_entities.csv`, `instrument_provider_map.csv`, `.github/*`, most of `site/*`. These are (a) pre-existing uncommitted cron output from before the session and/or (b) **CRLF↔LF line-ending noise** (e.g. `industry_entities.csv` diff is `@@ -1,170 +1,170 @@` with byte-identical content). My intended edits are only the four files in section 2. Separate these before committing.

## 5. Open items / do better

- **Guerilla fund: unconfirmed.** The literal "guerilla/guerrilla" funds (Copenhagen Guerrilla Capital, Delhi Guerrilla Ventures, Louisville Guerrilla VC) are conventional early-stage VC by presentation; I could not reach Guerrilla Capital's own site, only third-party profiles, and found **no** evidence of power-law/unicorn targeting (its partners' ~$43M outcomes actually lean non-unicorn). It is a needs-verification case, **not** a confirmed non-fit. Do not add it without the user's specific fund name/URL.
- Promote Everhold & Purpose Evergreen to the atlas **only** via the intake-promotion path after fetching/reviewing source text (repo discipline: promotion creates `candidate_evidence`, never `paper_ready`).
- The reiterated taxonomy in `self_description_taxonomy_findings.md` is a **proposal**; `asset_classes.csv` and the published paper were intentionally left untouched.

## 6. EVERGREEN — verification before adding it as an asset class (READ THIS FIRST)

The user is considering adding "Evergreen Capital" as an asset class and hunting ~200 entities. **Verified finding: do NOT name the class "Evergreen," and do NOT bulk-add everything that calls itself evergreen.** Reasoning is grounded:

- "Evergreen" is a **fund-structure term** (open-ended, no fixed termination), not a non-unicorn thesis. It is used heavily by mainstream, unicorn-inclusive capital: **$457B across 486 semi-liquid evergreen funds as of YE2025** (KKR, Morgan Stanley, Vista, Warburg Pincus, Hamilton Lane, Wellington, iCapital). The industry is explicitly building evergreen vehicles to give wealth channels **access to VC and growth equity** — i.e. to unicorns. So "evergreen" fails the "outside unicorn VC" test as a selector. Same failure mode as "guerilla": the label does not select for the population.
- The genuinely non-unicorn signal is the narrower **permanent / patient / steward capital** thesis under some evergreen branding: "forever hold," "never sell," "no intention of selling," yield via dividends instead of exit, often a **holding-company (not fund)** structure, founder-legacy / mission-lock (steward ownership), sometimes **capped returns**. The distinguishing trait is the **return model (yield + slow compounding, no exit)**, not the word "evergreen."

**Asset-class test (taxonomy's own 6 criteria) — the permanent-capital holdco model plausibly qualifies:** return model = dividends/yield + durable compounding (not exit); underwriting = durable profitability/cash flow; capital structure = perpetual holdco / evergreen vehicle; risk = lower-growth, liquidity, operating durability; liquidity path = distributions, optional secondaries, no forced exit; fit = founders wanting legacy and no sale. Recommend naming it **Permanent / Steward Capital** (reconcile with the existing `Patient Capital` placeholder — they overlap heavily; likely a merge/rename, not a new sibling).

**Instructions for the 200-entity hunt (give these to the search):**
- INCLUDE only entities whose *self-description* shows: hold forever / never sell / no forced exit / no intention of selling / permanent capital / steward-ownership / dividends-not-exit / founder-legacy / mission-lock.
- EXCLUDE (these are unicorn-inclusive or exit-driven, despite "evergreen" branding): "semi-liquid," "democratizing private equity," "access to private markets," BDCs, fund-of-funds and wealth-access vehicles (KKR/Morgan Stanley/Vista/Warburg/Hamilton Lane/iCapital/Wellington), anything whose return model is IPO/exit-driven or that markets VC/growth/unicorn exposure.
- VERIFY each candidate against fetched own-site text (no third-party-only classifications); tier as `candidate_evidence` only after the page is fetched and quoted.
- Seeds already found (grounded): Permanent Equity, Everhold, Purpose Evergreen Capital, HOLD.co, Tiny, Bridges (evergreen vehicle), Evergreen-for-MSPs / Alpine "Evergreen" (verify — Alpine is a large PE firm), Evergreen Succession Capital (verify — financial-services PE-style), Fund for Employee Ownership.
- Watch the boundary with **Search/ETA** (SMB acquisition) and **Portfolio Capital** (software acquirers/holdcos) — permanent-capital holdcos overlap both; classify by *intent to hold forever + yield-not-exit*, not by acquisition activity alone.

## 7. Reusable method (for repeatability)

`scripts/mine_self_descriptions.py` builds the per-entity corpus from `source_pages.raw_text` + structured fields. `scripts/cluster_self_descriptions.py` clusters on **multi-word phrases only**, after stripping (a) the project's own scaffolding boilerplate ("candidate supports industry mapping outside... classic unicorn VC", "source-backed SMV bucket") and (b) the placeholder class tokens (smv/lmv/uvc) — otherwise clusters reflect our labels, not entity language. `scripts/validate_placeholders.py` tests whether a class's natural-language self-label appears in entities' own pages (the coined names SMV/LMV/strategic-middle scored **0/106**).
