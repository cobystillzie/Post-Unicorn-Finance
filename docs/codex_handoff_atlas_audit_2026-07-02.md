# Codex Hand-off — Comprehensive Atlas Audit (2026-07-02, ~15:30 ET)

**For:** Codex (or any fresh agent) finishing the comprehensive per-entity atlas audit that Claude
Code started 2026-07-02. Claude's session limit was hit mid-fan-out (**resets 6:50pm ET**). This doc
is self-contained: it gives exact machine state, the remaining work, and the rules needed to do it
without hallucinating.

## Read first (in order)
1. This doc.
2. `docs/comprehensive_atlas_audit_brief_2026-07-02.md` — the governing brief (§4 output fields,
   §5 classification rules, §6 must-resolve items, §8–9 deliverables). This hand-off restates the
   operational parts, but the brief is authority.
3. `docs/01_taxonomy.md` + `docs/research/ethan_guidance_2026-06-07.md` — taxonomy authority
   (Ethan's INPUT→OUTPUT model governs).

## Machine state — what is DONE
1. **CLAUDE.md fixed** (deliverable 5 ✅): data-model section now names `data/evidence/atlas.csv`
   (149 rows, Schema B) as authoritative and records the legacy `industry_entities.csv` deletion.
2. **Backup** ✅: pre-audit `atlas.csv` → `data/runtime/backup_2026-07-02_preaudit/atlas.csv`.
3. **Batch input** ✅: `data/runtime/audit_batches_2026-07-02.json` — a JSON array of **15 batches**
   (10+10+…+9 = 149 entities). Each entity: `entity_id, name, current_class, current_band,
   current_horizon_years, tech_enabled, website, audit_flag`, and for 29 of them a **`special_note`**
   carrying the §6 must-resolve directives (Group 6, Gearbox/PeakSpan band fix, RBF lenders,
   Perpetuity Project, Malpani ruling, fast-exit cohort). **Agents MUST honor special_note.**
4. **80/149 entities audited** ✅: batches **0, 2, 3, 4, 6, 7, 8, 9** are complete and validated
   (all expected entity_ids present, all required fields) at
   `data/runtime/audit_results_2026-07-02/batch_<i>.json`.
5. **Merge script ready** ✅ (not yet run): `scripts/merge_audit_results.py`. Deterministic; run
   **once, from repo root, only after all 15 batch files exist** — it is NOT idempotent
   (`source_note` appends on every run).
6. Workflow script copy (for reference): `scripts/comprehensive_atlas_audit_workflow.js`.

## What REMAINS
1. **Audit batches 1, 5, 10, 11, 12, 13, 14** = 69 entities (batch 14 has 9).
2. **Adversarial verify pass** — never ran (the only batch whose verify stage executed, batch 6,
   had nothing to verify). Required for anything to be auto-applied by the merge.
3. **Run the merge** → enriched `atlas.csv` (+`country`, `allocator`, `evidence_signal`; filled
   horizons/bands) + `docs/atlas_comprehensive_audit_2026-07-02.md` review table +
   `data/evidence/manual_changes_2026-07-02.log` append.
4. **Taxonomy-first packet rebuild** (see below).
5. **claude.ai Artifact publish** — Claude-only tool (Codex cannot do this). Leave for a Claude
   session; owner confirmed publish happens AFTER the audit.

---

## Task 1 — audit the 7 remaining batches

For each batch `i` in `{1, 5, 10, 11, 12, 13, 14}`:
read `data/runtime/audit_batches_2026-07-02.json`[i]; for each entity fetch its `website`
(plus 1–3 more pages on the SAME site — homepage/about/approach/thesis — when useful); then write
`data/runtime/audit_results_2026-07-02/batch_<i>.json` as `{"entities": [ ... ]}`.

**Per-entity output object (all fields required):**

| field | type / allowed values |
|---|---|
| `entity_id`, `name` | copy from input |
| `confirmed_asset_class` | one of `SMV, Nimble, Permanent, Studio, Impact Capital, Under Review, Excluded-Traditional, Reserved` |
| `changed_from` | previous class if proposing/applying a change, else `null` |
| `change_type` | `none` (confirmed) / `apply` (unambiguous, NOT SMV↔Nimble, NOT Group 6) / `propose` (judgment call) |
| `classification_confidence` | `high` / `med` / `low` |
| `rationale` | one line |
| `country` | HQ country; prefer the firm's own site; else ONE web search citing LinkedIn/Crunchbase/registry in `country_source`; else `"Unknown"` |
| `country_source` | URL or `"not stated"` |
| `liquidity_band` | `Nimble` (<6y) / `SMV` (~6–10y sub-unicorn) / `Permanent` (no exit) / `Studio` / `Unknown` — **NEVER `Unicorn`** |
| `horizon_years` | as stated, e.g. `"3-5"`, `"7"`, `""` if none |
| `exit_quote`, `exit_quote_url` | verbatim exit-horizon quote + URL, `""` if none stated |
| `allocator` | boolean — deploys its OWN or LPs' capital into companies (equity/debt/rev-share/acquisition). Build-their-own studios COUNT. Marketplaces/brokers/networks/pure advisories/no-capital accelerators do NOT |
| `tech_enabled` | boolean |
| `evidence_signal` | 1–2 sentence summary of how the firm describes ITSELF |
| `verbatim_quote`, `source_url`, `fetch_date` | best anchor quote (copied EXACTLY from a fetched page), its URL, `"2026-07-02"` (or actual fetch date) |
| `flags` | conflicts / `needs_review: <why>` / `""` |

**Classification rules (do not improvise — from the brief §5):**
- **Ethan INPUT→OUTPUT model:** SMV = large-ish markets → sub-unicorn liquidity (~$50–500M) at
  VC-like-or-better timing (~7–9y). Nimble = SMALLER markets → fast (<6y, typically 3–5y) liquidity.
  Permanent = no forced exit (evergreen/steward/holdco/family office; far beyond 10y). Studio =
  builds AND owns its own products (company creation IS the investment; ratified 2026-06-08).
  Impact Capital = tech-enabled mission/impact allocators with explicit anti-power-law message.
  Reserved = watch classes (Operator, Sovereign), parked never dropped. Excluded-Traditional =
  unicorn-chasing VC/PE contrast baseline. Under Review = borderline + revenue-based LENDERS
  (return = loan repayment, not a company exit).
- **Tie-break:** Permanent WINS over Nimble when a firm is both no-exit AND capital-efficient.
- **Unicorn rule:** 10y+ horizons excluded UNLESS explicitly non-unicorn-chasing (e.g. Gearbox) —
  then keep, band must NOT read "Unicorn" (nor Permanent).
- **Do NOT auto-reclassify SMV↔Nimble** (pending Ethan reconciliation) → `change_type='propose'`.
- **Group 6** (special_note marks them) → per-firm evidence, never blanket-relabel, `propose` only.
- **Anti-hallucination:** every claim needs a VERBATIM quote from a page actually fetched + URL.
  Unverifiable ≠ fabricated: dead/403/thin/JS-only page → keep current class, confidence `low`,
  flag `needs_review: <why>`, quotes `""`. NEVER invent or paraphrase quotes.
- False-junk warning: an embedded-financing platform saying "our capital" + revenue-based funding
  IS a real allocator (YouLend precedent). Be as skeptical of junk calls as of keep calls.

## Task 2 — adversarial verify pass

For EVERY entity (all 15 batches) with `change_type=='apply'` **or** `allocator==false`:
re-fetch the cited `source_url`, confirm the quote actually appears live (whitespace differences OK,
paraphrase NOT OK), and independently re-apply the rules trying to REFUTE the call. Write:

`data/runtime/audit_workflow_summary_2026-07-02.json`
```json
{"batches": [{"batch": 0, "verdicts": [
  {"entity_id": "...", "quote_verified": true, "upheld": true, "notes": "..."}
]}]}
```

**Without this file the merge auto-applies NOTHING** — every class change becomes a proposal
(safe, but weaker). An `apply` change with no verdict, or `upheld=false`, is demoted to proposal.

## Task 3 — merge (once, after ALL 15 batch files exist)

```
cd C:\Users\cobys\projects\post-unicorn-finance
python scripts/merge_audit_results.py
```
Produces: enriched `data/evidence/atlas.csv` (adds `country, allocator, evidence_signal` columns;
fills bands/horizons; refreshes live-verified exit quotes; applies ONLY verified unambiguous class
changes), `docs/atlas_comprehensive_audit_2026-07-02.md` (applied + proposed + per-entity tables),
and appends `data/evidence/manual_changes_2026-07-02.log`. Review its stdout: it prints applied vs
proposed changes and any missing/extra entities. If a redo is needed, restore from
`data/runtime/backup_2026-07-02_preaudit/atlas.csv` first.

## Task 4 — taxonomy-first packet rebuild (after merge)

Extend `scripts/build_atlas_packet_html.py` (generator for `site/atlas_packet_2026-07-02.html`):
1. Add a **taxonomy-first top section** modeled on `site/post_unicorn_industry_atlas_packet.html`
   heading flow — *Taxonomy → The Post-Unicorn Stack → How the classes differ → Where the classes
   bleed → non-allocator layers → Instruments* — but describing the CURRENT class set (Nimble, SMV,
   Permanent, Studio, Impact active; Reserved = watch; Excluded-Traditional = contrast; Under
   Review). Capital innovation is the UMBRELLA of the whole atlas, not a section.
2. Add a **Country** column and switch the signal cell to the new `evidence_signal`
   (self-description) with `exit_quote` as secondary.
3. Regenerate the HTML. (The claude.ai Artifact publish step stays with Claude.)

## Alternative path — resume in Claude Code after 6:50pm ET (cheapest)

The original workflow is resumable and its script was edited so audit agents **short-circuit**:
if their `batch_<i>.json` already exists and is complete they return it WITHOUT re-fetching. So a
resume re-runs only the 7 missing batches at full cost plus 8 cheap re-reads, then runs the verify
stage automatically. In a Claude Code session:

```
Workflow({
  scriptPath: "C:\\Users\\cobys\\.claude\\projects\\C--Users-cobys-projects-post-unicorn-finance\\2720d864-ab5c-465c-926b-53e2cb5349ce\\workflows\\scripts\\comprehensive-atlas-audit-wf_54ba77e1-c4a.js",
  resumeFromRunId: "wf_54ba77e1-c4a"
})
```
(Script copy for reference: `scripts/comprehensive_atlas_audit_workflow.js`. The resume must run in
the SAME Claude Code session/journal; from a fresh session, just launch the script fresh — the
short-circuit makes that nearly as cheap.) Then: save the workflow's returned summary JSON to
`data/runtime/audit_workflow_summary_2026-07-02.json`, run the merge, rebuild the packet, publish
the Artifact.

## Operating cautions (from CLAUDE.md — binding)
- Classification credibility over count; a junky row is worse than a missing one.
- Flag, don't auto-edit, anything ambiguous; log every manual change.
- Social platforms are discovery-only; verify via the firm's official site; don't bypass protections.
- Batch-6 observations already flagged for owner attention: `tiny` (band contradiction: stored
  Nimble/4y vs "hold for the long term" on-site), `bridges-evergreen` (only 2016 press page;
  tech_enabled unsupported), `purpose-evergreen-capital` (8–13y is a self-liquidating instrument
  duration, not an exit — stays Permanent).
