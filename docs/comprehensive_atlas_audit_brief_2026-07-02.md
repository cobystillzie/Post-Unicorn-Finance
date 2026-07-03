# Comprehensive Atlas Audit — Handoff Brief (2026-07-02)

**Purpose:** Run a full, descriptive, per-entity audit of all 149 atlas entities in a **fresh
session** so it doesn't inherit this session's expensive accumulated context. This brief is
self-contained: reading it + the files it points to is enough to run the audit correctly.

> **How to start the fresh session:** paste →
> *"Read `docs/comprehensive_atlas_audit_brief_2026-07-02.md` and run the comprehensive atlas
> audit as a bounded workflow."* Ultracode should be ON (this is a legitimate large fan-out).

---

## 0. Read these first (in order)
1. **This brief** — it overrides any stale references below.
2. `CLAUDE.md` — mission + operating rules. **BUT SEE §1 correction: it still calls the
   deleted `industry_entities.csv` "the atlas." That is wrong now.**
3. `docs/01_taxonomy.md` — full asset-class definitions (read in full; this session only got line 1).
4. `data/evidence/atlas.csv` — the authoritative 149-entity dataset (Schema B).
5. **Obsidian vault** — the post-unicorn-finance notes. The Obsidian MCP is **working** (tools:
   `obsidian_search_notes`, `obsidian_list_notes`, `obsidian_get_note`). Search "post-unicorn"
   / "post unicorn finance" and read the relevant notes for classification context BEFORE auditing.
6. `docs/atlas_classification_audit_2026-07-02.md` — the existing flag list (open items).

## 1. Critical state corrections (neutralize landmines)
- **Authoritative data = `data/evidence/atlas.csv` (149 entities, Schema B: asset class +
  liquidity horizon per row).** Columns: `entity_id, name, asset_class, liquidity_band,
  horizon_years, tech_enabled, tier, confidence, website, exit_quote, audit_flag, source_note`.
- **`data/evidence/industry_entities.csv` is DELETED forever** (legacy 890-row, PE-bloated,
  pre-audit corpus). **Ignore CLAUDE.md's line calling it the atlas.** Backups exist in
  `data/runtime/backup_2026-07-01/`, `/backup_2026-07-02/`, `/backup_2026-07-02b/`, `/c/`.
- **Recommended cheap first action in the fresh session:** update `CLAUDE.md`'s data-model line
  to name `atlas.csv` as authoritative + note the legacy deletion, so this landmine dies.
- **Capital innovation is the UMBRELLA thesis of the entire atlas, NOT a section.** Every class
  is a different experiment in funding companies outside the 10-year unicorn power-law model.

## 2. Mission of this audit
For **every one of the 149 entities**, confirm exactly where it belongs and enrich it with
country + liquidity horizon + descriptive evidence. **Classification credibility is everything —
a miscategorized row is worse than a missing one.** Never assert without a live-page quote.

## 3. Current snapshot (before audit)
`Permanent 68 · Nimble 29 · SMV 18 · Studio 13 · Impact Capital 11 · Under Review 4 ·
Excluded-Traditional 3 · Reserved 3` = 149.

## 4. Per-entity output fields (the enriched schema)
For each entity produce, **each backed by a verbatim quote + source URL + fetch date**:
- `confirmed_asset_class` (+ `changed_from` if corrected) and `classification_confidence`
  (high/med/low) with a one-line rationale.
- `country` / HQ geography (+ source). This is the new global-geography lens the owner asked for.
- `liquidity_horizon` (years and/or band) + verbatim exit quote + URL — or "none stated."
- `allocator` (yes/no): does it deploy its OWN or LPs' capital (equity/debt/rev-share/acquisition)?
- `tech_enabled` (yes/no).
- `evidence_signal`: 1–2 sentence descriptive summary of how the firm describes ITSELF (self-description).
- `verbatim_quote` + `source_url` + `fetch_date` (anti-hallucination anchor).
- `flags` / open questions.
- **New columns to add to `atlas.csv`:** `country`, `allocator`, `evidence_signal` (keep all existing).

## 5. Classification rules (must follow — do not improvise)
- **Ethan INPUT→OUTPUT model:** **SMV** = large-ish markets → sub-unicorn liquidity at
  similar-or-better timing (~7–9y). **Nimble** = SMALLER markets → fast (<6y) liquidity events.
  **Permanent** = no forced exit (evergreen / steward-ownership / holdco / family office).
  **Studio** = builds AND owns its own products (company creation IS the investment; ratified
  2026-06-08). **Impact Capital** = mission/impact-driven capital. **Reserved** = watch classes
  with no real funds yet (Operator, Sovereign). **Excluded-Traditional** = classic unicorn VC/PE,
  kept only as contrast baseline. **Under Review** = borderline/unplaced + revenue-based lenders
  (their "return" is loan repayment, not a company exit).
- **Tie-break:** Permanent wins over Nimble when a firm is BOTH no-exit AND capital-efficient.
- **Allocator test:** must deploy own/LPs' capital. Build-their-own studios DO count.
  Marketplaces/brokers/networks/pure advisories/no-capital accelerators/article-or-listicle pages
  are NOT allocators → Under Review or drop (never force into a real class).
- **Unicorn band (10y+) is excluded** UNLESS the firm is explicitly non-unicorn-chasing — then it
  stays (e.g. **Gearbox Capital** = SMV with a stated 10y horizon but non-unicorn; band must NOT
  read "Unicorn"; and Permanent is wrong — permanent is far beyond 10y).
- **Do NOT auto-reclassify SMV↔Nimble** by the market-size model until reconciled with Ethan —
  propose + flag those, don't silently switch.
- **Anti-hallucination:** every classification/enrichment needs a verbatim quote from the LIVE
  page + URL. Unverifiable ≠ fabricated: mark `needs_review`, never invent. Thin/JS-only pages
  are not demotions by themselves.

## 6. Known must-resolve items (carry these in)
- **The Perpetuity Project:** currently Permanent; owner believes **Impact** — verify against its page.
- **Group 6 (impact vs. growth-equity):** owner said "move all to Impact," but the evidence
  conflicts — **Serent Capital** and **Silversmith Capital** are SaaS **growth-equity** (NOT
  impact); **Skoyen / Soch Holdings / The Perpetuity Project / Ascendant** are permanent/traditional;
  only **Savana Fund / Social Tech Ventures / Zebra Impact Ventures** (and maybe **Capacity
  Capital**) are genuinely impact. **Resolve per-firm with page evidence and surface the conflict —
  do not blanket-relabel growth-equity as impact.**
- **Gearbox Capital / PeakSpan Capital:** were SMV with a "Unicorn" band — re-verify horizon and
  fix the band (see §5 Unicorn rule).
- **~15+ entities with `liquidity_band` = Unknown/blank** — find horizons where they exist.
- **RBF lenders** (Bigfoot, Lighter, TIMIA) already moved to **Under Review**, noted "revenue-based
  lender." Confirm.
- The 12 fast-exit liquidity firms are already in (11 Nimble + Edited Capital in SMV) — re-confirm, don't re-add.

## 7. How to run it (cost-bounded Workflow — this is the expensive phase)
- Use the **Workflow tool** (Ultracode). **Batch** to control cost: ~15 agents × ~10 entities each
  (or a pipeline), NOT 149 separate agents.
- Each agent, for its batch: fetch each firm's homepage, extract the §4 fields with a verbatim
  quote + URL, classify per §5, return **structured JSON** (use a schema).
- **Set a HARD token budget** (`budget.total` via the owner's "+Nk" directive, or a
  `while (budget.remaining() > …)` guard) and STOP at the cap. Ask the owner for the ceiling at start.
- Dedup + synthesize → back up `atlas.csv` first, then write the enriched CSV + a **proposed-changes
  review table** (`docs/`). Apply only unambiguous, evidence-backed corrections; **flag judgment
  calls** (esp. SMV/Nimble and Group 6) for the owner. Log to `data/evidence/manual_changes_<date>.log`.

## 8. Packet + Claude Design (AFTER the audit)
- Rebuild the packet **taxonomy-first** to match `site/post_unicorn_industry_atlas_packet.html`
  (structure: Taxonomy → "The Post-Unicorn Stack" → how classes differ → entity layers → instruments),
  THEN the entity list. Extend `scripts/build_atlas_packet_html.py` to add the taxonomy section on
  top and new `country` + richer `evidence_signal` columns.
- Then **auto-publish as a claude.ai Artifact** (Artifact tool; load the `artifact-design` skill
  first). The owner confirmed: publish **after** the audit, and yes — Claude Code can do this
  automatically (no manual step for the owner).

## 9. Deliverables
1. Enriched `data/evidence/atlas.csv` (+ `country`, `allocator`, `evidence_signal`; filled horizons).
2. Proposed-changes review table in `docs/` (per-entity, with evidence + confidence).
3. Regenerated **taxonomy-first** HTML packet.
4. Published claude.ai Artifact.
5. Updated `CLAUDE.md` (atlas.csv authoritative; legacy deleted).

## 10. Cost discipline (owner directive)
This is the costliest phase. Batch, budget-cap, stop at the cap, and report spend. The owner
explicitly said: **"be very careful not to go over the session limit."** Prefer fewer, batched
agents over many small ones. Generator/CSV edits are deterministic — do them in-context, not via agents.
