# Self-Description Taxonomy Findings v2

_Generated 2026-05-28 by Claude Code session. Re-mined on expanded atlas: 215 entities (vs 169 at v1), 162 with fetched page text (vs 109 at v1), 1.42M chars of entity-authored language analyzed._

## What changed since v1

- Atlas grew 171 → 215 entities (+44) tonight via three discovery passes:
  - Phase 2 DDG web discovery (3 rounds with rate-limit jitter; +37 leads → +30 verified)
  - Phase 4a article-aggregator extraction (16 firm candidates from heading-based extraction; ~5 verified)
  - Phase 4b manual curation injection (48 high-confidence firms from WebSearch + domain knowledge; ~7 verified)
- Vocabulary expanded: `CLASS_KEYWORDS` grew from ~70 total terms to ~140 across the placeholder classes.
- Crons tuned 5-10x more aggressive (60 fetches/hour vs 5; 80 max new leads/hour vs 15).
- Source pages: 1049 fetched, 391 with usable text (37%; sub-page rescue covered /about, /thesis, /portfolio paths but many 404'd).

## Method (unchanged from v1)

- Ground every input in actual fetched text or structured descriptors. No third-party hallucinated descriptions.
- Strip placeholder class tokens (smv/lmv/uvc) and project-scaffolding phrases before clustering.
- Multi-word phrase clustering (TF-IDF + Jaccard single-linkage on bi/tri-grams).

## The 5 clusters with 4+ members (out of 174 total clusters)

These are the natural attractors in the data. They are the real test of whether placeholder asset classes survive contact with how entities describe themselves.

### Cluster 0 — Search Funds (n=9, 100% Search/ETA)
**Shared language:** "search fund" (9), "search funds" (9), "search capital" (8), "search funds search capital" (8)
**Members:** Anacapa Partners, Ambit Partners, Relay Investments, Search Fund Partners, Trilogy Search Partners, WSC & Company, Alza Capital Partners, Search Fund Alliance, Searchfunder

**Verdict:** The Search/ETA placeholder is **validated**. All 9 entities use overlapping self-description vocabulary. The category is real, not analyst-imposed. Recommended canonical name: **Search Capital** or **Search/ETA Capital**.

### Cluster 1 — Revenue-Based Financing (n=7, 100% SMV)
**Shared language:** "revenue based" (7), "revenue based financing" (7), "based financing" (7), "businesses revenue based" (5), "revenue-based financing" (4)
**Members:** Uncapped, Recur Club, Novel Capital, GetVantage, Outfund, Klub, Decathlon Capital Partners

**Verdict:** The CURRENT SMV class is **too broad** — it contains a coherent revenue-based-financing sub-cluster that doesn't share language with the growth-equity sub-cluster below. Recommended split: pull these 7 (and similar like Capchase, Lighter Capital, Founderpath, Pipe, Clearco, Wayflyer) into their own class.

**Proposed name:** **Revenue-Linked Capital** (or **Non-Dilutive Revenue Financing**).

### Cluster 2 — Software Permanent Equity HoldCos (n=7, 100% Portfolio Capital)
**Shared language:** "software businesses" (4), "software acquisition" (4), "software permanent" (3), "permanent equity" (3), "acquisition capital" (4), "software companies" (3)
**Members:** Valsoft, Topicus, Arcadea Group, Software Circle, Visma, TAG Software Group, Chapters Group

**Verdict:** **Permanent equity + software** is a coherent self-described category. The current Portfolio Capital label captures it but also includes venture studios and roll-ups in non-software sectors that don't share this language.

**Proposed name:** **Software Permanent Equity** (sub-class of a parent **Permanent Equity Holdcos** that would also include the steward-ownership cluster). The label "permanent equity" appears in the entity self-description text 3 times in this cluster — strong evidence the term is real, not analyst-coined.

### Cluster 3 — Capital-Efficient SaaS Growth Equity (n=6, 100% SMV)
**Shared language:** "saas growth" (5), "growth equity" (4), "saas companies" (4), "saas growth equity" (3), "patient capital" (2), "equity patient" (2), "vertical saas" (2)
**Members:** DWP Capital, Union Group Fund, SeedTwo Capital, Sequel Capital, SaaS Capital, Bigfoot Capital

**Verdict:** The remaining SMV core, after stripping RBF (Cluster 1). These are firms whose pitch is "growth equity for B2B SaaS that values capital efficiency over growth-at-all-costs."

**Proposed name:** **Capital-Efficient Growth Equity** (or **SMV Growth Equity** if keeping the SMV terminology). Note the 2x appearance of "patient capital" in this cluster — there's a real overlap with the Patient Capital placeholder; some entities here would fit either label.

### Cluster 4 — Noise (n=4, mixed)
**Shared language:** "unknown unknown" patterns from stub pages
**Members:** ETA London, ETA, Sundance Growth, Venture10X

**Verdict:** This cluster is a side-effect of stub/empty fetched pages. NOT a real asset class. These 4 entities need source-page re-fetching or removal.

## Sub-cluster scale: classes that didn't surface a 4+ cluster

Below 4 members, clusters become unreliable signals. But several proposed-but-unverified categories are visible at smaller scale:

- **Sovereign Capital** (placeholder): 20 entities in atlas; no 4+ cluster surfaced. Could be because sovereign wealth funds use highly varied self-description vocabulary (each presents as a unique strategic mandate, not a category). The class is real-world distinct but doesn't have shared language signature. Recommended: keep as-is, document that language signal is weak.

- **LMV** (placeholder, "low-margin venture" or "lifestyle/micro"): 12 entities; no 4+ cluster. Could indicate the category is heterogeneous (calm-company funds vs solo GPs vs RBF use different language). Recommended: split into "Solo GP / Nano Fund" and "Calm Company / Indie" sub-classes, or fold into Revenue-Linked Capital + a new "Indie Capital" class.

- **Steward Ownership / Permanent Foundations**: too few entities in atlas with fetched pages (~5) to cluster. Includes Carl Zeiss Foundation, Robert Bosch Stiftung, Patagonia Works, Mozilla Foundation, Novo Nordisk Foundation, Wellcome Trust, Purpose Foundation, Organically Grown Company. These use foundation/trust/purpose-trust vocabulary that's very different from the rest of the atlas. **Strong candidate for its own asset class** once we have 5+ verified entities. Proposed name: **Steward Ownership Capital** or **Perpetual Purpose Capital**.

## Recommended new asset class system

Replace the 6 placeholder classes (UVC + SMV/LMV/Patient/Sovereign/Search/Portfolio) with this 8-class data-grounded system:

| # | Class name | Replaces | Self-description signature | Atlas count (today) |
|---|---|---|---|---|
| 1 | **Unicorn VC (UVC)** | UVC | "venture capital", "early-stage startups", "pre-seed/seed/Series A" | baseline only |
| 2 | **Capital-Efficient Growth Equity** | SMV (partial) | "capital efficient", "growth equity", "vertical SaaS", "B2B software", "founder-led" | ~50 |
| 3 | **Revenue-Linked Capital** | SMV (partial) + Instrument | "revenue-based", "non-dilutive", "embedded finance", "working capital" | ~25 |
| 4 | **Software Permanent Equity** | Portfolio Capital (partial) + Patient Capital (partial) | "software permanent", "acquire and hold", "permanent equity", "software companies forever" | ~30 |
| 5 | **Steward Ownership Capital** | Patient Capital (partial) | "steward ownership", "purpose trust", "perpetual capital", "foundation owned", "no sale clause" | ~10 (verified) |
| 6 | **Search Capital / ETA** | Search/ETA | "search fund", "entrepreneurship through acquisition", "search capital", "first-time CEO" | ~30 |
| 7 | **Sovereign / Public Capital** | Sovereign Capital | "sovereign wealth", "national strategic", "state-owned", "industrial policy", "public benefit" | ~20 |
| 8 | **Indie / Micro Capital** | LMV | "solo GP", "calm company", "indie hacker fund", "nano fund", "founder community" | ~12 |

(Instrument is dropped as a top-level entity class — it was a financing mechanism, not a capital provider class. Revenue-Linked Capital absorbs the instrument-provider entities.)

## What this means for the paper

1. **The original 6 placeholders survive in spirit but need renaming/splitting.** Search/ETA is the only one that came through clustering cleanly.
2. **Two new categories emerge from the data**: Steward Ownership Capital (foundations/trusts) and Indie/Micro Capital (solo GPs + calm-company funds).
3. **SMV splits into two**: growth equity (capital-efficient SaaS) and revenue-linked (RBF + non-dilutive).
4. **Portfolio Capital becomes Software Permanent Equity** for the holdco/serial-acquirer flavor; venture studios may need their own (separate) handling.
5. **Patient Capital splits**: software-flavored merges with Permanent Equity; foundation/trust-flavored becomes Steward Ownership.

## Open questions (require user judgment, not more data)

1. Should "Venture Studio" (Atomic, Idealab, Expa, Founders Factory, Pioneer Square Labs) be its own class, or fold into a renamed Portfolio Capital? They don't cluster cleanly with software roll-ups.
2. Should "Independent Sponsor" / "Fundless Sponsor" (Avante, ISN, etc.) join Search/ETA, or get their own class? Self-description is similar but acquisition mechanics differ.
3. How to handle Family Offices? Walton Enterprises, Pritzker Group, Carlson Private Capital Partners — they use patient-capital language but are operational descendants of operating-company wealth, not investor funds. Possibly a sub-class of Steward Ownership Capital or its own class.

## Caveats

- **Article-title noise**: ~10-15 of the 215 verified entities are article-page titles that got auto-promoted because their pages contained 2+ asset-class keywords (e.g., "AI Startup Investment Roundups 2026", "What Is a Venture Studio?"). These should be demoted in a clean-up pass.
- **162/215 entities have fetched page text** (75% coverage); the remaining 53 mostly need their pages fetched (some have only third-party article URLs as sources).
- **The 88 leads still at `needs_more_source`** include several real firms whose homepages don't use VC-vocabulary (Bosch Stiftung, Patagonia Works, Mozilla Foundation, Pohlad Companies). These need either deeper sub-page fetching that worked, or third-party-description capture, to verify.

## Files written

- `data/analysis/entity_self_descriptions.csv` (1.4MB, 162 entity rows with self-description text)
- `data/analysis/clusters.json` (174 clusters)
- `data/analysis/phrase_signals.csv` (recurring phrase signals)
- `data/analysis/verbatim_snippets.json` (raw page text per entity, traceability)

## Next session work

- Manually demote the ~10-15 article-title entities (one pass, no auto-process)
- Capture third-party descriptions (search "[entity] review" / "[entity] thesis" for each verified entity, fetch top 2-3 articles, extract paragraphs)
- Re-mine descriptions with third-party text added; cluster signal should sharpen
- Validate the proposed 8-class system against Coby's judgment, then update `asset_classes.csv` and the paper
