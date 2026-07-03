export const meta = {
  name: 'comprehensive-atlas-audit',
  description: 'Per-entity audit of all 149 atlas entities: fetch live pages, verify, classify, enrich',
  phases: [
    { title: 'Audit', detail: '15 batch agents x ~10 entities: fetch pages, extract fields, classify per rules' },
    { title: 'Verify', detail: 'adversarial re-check of auto-apply class changes and non-allocator calls' },
  ],
}

const BATCH_FILE = 'C:/Users/cobys/projects/post-unicorn-finance/data/runtime/audit_batches_2026-07-02.json'
const OUT_DIR = 'C:/Users/cobys/projects/post-unicorn-finance/data/runtime/audit_results_2026-07-02'
const N = 15

const RULES = `ASSET CLASSES (Ethan INPUT->OUTPUT model — classify by the firm's ACTUAL stated thesis, not invented boxes):
- SMV: backs early-stage companies in LARGE-ISH markets -> SUB-UNICORN liquidity (~$50-500M outcomes) at VC-like-or-better timing (~7-9y).
- Nimble: backs early-stage companies in SMALLER markets -> FAST liquidity events (<6y, typically 3-5y).
- Permanent: NO forced exit — evergreen, permanent equity, buy-and-hold holdco, steward-ownership, family office. Horizon far beyond 10y.
- Studio: builds AND owns its own products — systematic company creation IS the investment activity (ratified 2026-06-08: these ARE allocators; do not hold a studio for building its own products).
- Impact Capital: tech-enabled mission/impact-driven allocators with an explicit anti-power-law message.
- Reserved: watch classes with no real funds yet (Operator = search funds/ETA; Sovereign = sovereign wealth/DFI/blended). Parked, never dropped.
- Excluded-Traditional: classic unicorn-chasing VC/PE, kept only as contrast baseline.
- Under Review: borderline/unplaced entities + revenue-based LENDERS (their return is loan repayment, not a company exit).

HARD RULES:
1. Tie-break: Permanent WINS over Nimble when a firm is BOTH no-exit AND capital-efficient.
2. Allocator test: allocator=true only if it deploys its OWN or LPs' capital INTO companies (equity/debt/revenue-share/acquisition). Build-their-own studios COUNT. Marketplaces, brokers, M&A advisors, industry networks, pure advisories, no-capital accelerators, and article/listicle pages are NOT allocators -> Under Review; never force a non-allocator into a real class. BUT beware false-junk: an "embedded financing platform" saying "our capital" + revenue-based funding IS a real allocator (YouLend precedent).
3. Unicorn band (10y+) is excluded UNLESS the firm is explicitly non-unicorn-chasing — then it stays, and its band must NOT read "Unicorn" (nor "Permanent" — permanent means far beyond 10y). Use the class-appropriate band with the stated horizon years.
4. Do NOT silently reclassify between SMV and Nimble — those definitions are pending reconciliation with the thesis owner. If evidence points across that line, use change_type='propose' (never 'apply').
5. Entities whose special_note mentions GROUP 6: per-firm evidence only, NEVER blanket-relabel, change_type='propose', and surface the conflict in flags.
6. Anti-hallucination: every classification/enrichment needs a VERBATIM quote copied EXACTLY from a page you actually fetched this session, plus its URL. Unverifiable != fabricated: if a page is dead/403/thin/JS-only, KEEP the current class, set classification_confidence='low', put 'needs_review: <why>' in flags, and use "" for quotes. NEVER invent or paraphrase a quote.
7. change_type semantics: 'none' = current class confirmed; 'apply' = unambiguous, evidence-backed correction that is NOT SMV<->Nimble and NOT Group 6; 'propose' = judgment call for owner review.`

const ENTITY_SCHEMA = {
  type: 'object',
  properties: {
    entity_id: { type: 'string' },
    name: { type: 'string' },
    confirmed_asset_class: { type: 'string', enum: ['SMV','Nimble','Permanent','Studio','Impact Capital','Under Review','Excluded-Traditional','Reserved'] },
    changed_from: { type: ['string','null'], description: 'previous class if proposing/applying a change, else null' },
    change_type: { type: 'string', enum: ['none','apply','propose'] },
    classification_confidence: { type: 'string', enum: ['high','med','low'] },
    rationale: { type: 'string' },
    country: { type: 'string' },
    country_source: { type: 'string' },
    liquidity_band: { type: 'string', enum: ['Nimble','SMV','Permanent','Studio','Unknown'] },
    horizon_years: { type: 'string' },
    exit_quote: { type: 'string' },
    exit_quote_url: { type: 'string' },
    allocator: { type: 'boolean' },
    tech_enabled: { type: 'boolean' },
    evidence_signal: { type: 'string' },
    verbatim_quote: { type: 'string' },
    source_url: { type: 'string' },
    fetch_date: { type: 'string' },
    flags: { type: 'string' }
  },
  required: ['entity_id','name','confirmed_asset_class','changed_from','change_type','classification_confidence','rationale','country','country_source','liquidity_band','horizon_years','exit_quote','exit_quote_url','allocator','tech_enabled','evidence_signal','verbatim_quote','source_url','fetch_date','flags']
}
const BATCH_SCHEMA = { type: 'object', properties: { entities: { type: 'array', items: ENTITY_SCHEMA } }, required: ['entities'] }
const VERDICT_SCHEMA = {
  type: 'object',
  properties: {
    quote_verified: { type: 'boolean', description: 'does the cited quote actually appear on the live page' },
    upheld: { type: 'boolean', description: 'is the auditor decision correct under the rules' },
    notes: { type: 'string' }
  },
  required: ['quote_verified','upheld','notes']
}

function auditPrompt(i) {
  return `You are a research auditor for the Post-Unicorn Finance atlas — a source-backed catalog of capital allocators operating OUTSIDE the classic 10-year unicorn-VC power-law model. Classification credibility is everything: a miscategorized row is worse than a missing one.

STEP 0 — CHECK FOR EXISTING RESULTS FIRST: if ${OUT_DIR}/batch_${i}.json already exists, Read it. If it contains ALL your batch's entities with the required fields filled, return its contents EXACTLY as your structured output — do NOT re-fetch anything. Only audit entities missing from it (then merge them in, rewrite the file, and return the full set).

STEP 0b — Read the file ${BATCH_FILE} (a JSON array of batches). Your batch is index ${i} (0-based): ~10 entities, each with entity_id, name, current_class, current_band, current_horizon_years, tech_enabled, website, audit_flag, and sometimes special_note. If special_note exists you MUST follow it.

FOR EACH entity in your batch:
1. WebFetch its website URL. Also fetch 1-3 additional pages on the SAME site when useful (homepage if the stored URL is a subpage; about/approach/thesis/team pages for classification + country evidence). Respect site protections; if a fetch fails or the page is thin/JS-only, note that and move on — do not retry endlessly.
2. Produce these fields (schema-enforced), each grounded in what you actually fetched:
   - confirmed_asset_class + changed_from + change_type + classification_confidence (high/med/low) + one-line rationale.
   - country: HQ country. Prefer the firm's own site (footer/contact/about/legal). If absent there, you MAY use one WebSearch and cite a reputable third-party page (LinkedIn/Crunchbase/company registry) as country_source — mark it clearly as third-party. If still unclear: country="Unknown", country_source="not stated".
   - liquidity horizon: horizon_years as stated (e.g. "3-5", "7", "" if none stated) + liquidity_band + exit_quote (verbatim, "" if none stated) + exit_quote_url ("" if none). Bands: Nimble (<6y fast exit), SMV (sub-unicorn exit ~6-10y), Permanent (no exit / indefinite hold), Studio (studio model), Unknown. NEVER output band "Unicorn".
   - allocator (true/false) per the allocator test in the rules.
   - tech_enabled (true/false): does it target software / tech-enabled companies?
   - evidence_signal: 1-2 sentence descriptive summary of how the firm describes ITSELF (self-description, not your opinion).
   - verbatim_quote + source_url + fetch_date "2026-07-02": the single best anchor quote supporting your classification, copied EXACTLY from the fetched page.
   - flags: conflicts / open questions / "needs_review: <why>" — "" if clean.

RULES (do not improvise):
${RULES}

OUTPUT (both steps required):
1. Write the complete result as JSON {"entities":[...all ~10...]} to ${OUT_DIR}/batch_${i}.json using the Write tool — exact same content you will return.
2. Return the SAME data via your structured output. Every entity from your batch must appear exactly once.`
}

function verifyPrompt(e) {
  return `You are an ADVERSARIAL verifier for the Post-Unicorn Finance atlas. An auditor just made this call about "${e.name}":
- Decision: asset class ${e.confirmed_asset_class}${e.changed_from ? ' (CHANGED from ' + e.changed_from + ')' : ''}; allocator=${e.allocator}.
- Their anchor quote: "${e.verbatim_quote}" — cited from ${e.source_url || '(no URL given)'}
- Their rationale: ${e.rationale}

Your job is to try to REFUTE this call:
1. WebFetch ${e.source_url || 'the firm homepage'} (and the firm's homepage if different). Check the quote actually appears on the live page (whitespace/punctuation differences OK; paraphrase is NOT OK).
2. Re-apply the key rules: allocator = deploys its OWN or LPs' capital into companies (equity/debt/rev-share/acquisition); build-their-own studios COUNT as allocators; marketplaces/brokers/networks/pure advisories do NOT. Permanent beats Nimble when a firm is both no-exit and capital-efficient. Revenue-based LENDERS belong in Under Review.
3. If the auditor called this a NON-allocator, be extra skeptical of the junk call itself — false positives cut both ways (an embedded-financing platform saying "our capital" IS a real allocator).

Return: quote_verified (bool), upheld (bool — is the decision correct), notes (1-2 sentences on what you found).`
}

const results = await pipeline(
  Array.from({ length: N }, (_, i) => i),
  (i) => agent(auditPrompt(i), { label: 'audit:batch' + i, phase: 'Audit', schema: BATCH_SCHEMA }),
  async (batch, i) => {
    if (!batch || !batch.entities) return { batch: i, failed: true }
    const flagged = batch.entities.filter(e => (e.change_type === 'apply' && e.changed_from) || e.allocator === false)
    let verdicts = []
    if (flagged.length) {
      verdicts = (await parallel(flagged.map(e => () =>
        agent(verifyPrompt(e), { label: 'verify:' + e.entity_id, phase: 'Verify', schema: VERDICT_SCHEMA })
          .then(v => ({ entity_id: e.entity_id, quote_verified: v.quote_verified, upheld: v.upheld, notes: v.notes }))
      ))).filter(Boolean)
    }
    return {
      batch: i,
      audited: batch.entities.length,
      changes: batch.entities.filter(e => e.change_type !== 'none').map(e => ({
        id: e.entity_id, from: e.changed_from || e.confirmed_asset_class, to: e.confirmed_asset_class,
        type: e.change_type, conf: e.classification_confidence, why: e.rationale
      })),
      nonAllocators: batch.entities.filter(e => e.allocator === false).map(e => e.entity_id),
      flaggedEntities: batch.entities.filter(e => e.flags && e.flags.trim().length).map(e => ({ id: e.entity_id, flags: e.flags })),
      verdicts
    }
  }
)

const ok = results.filter(Boolean)
const done = ok.filter(r => !r.failed)
log('Batches complete: ' + done.length + '/' + N + ' | entities audited: ' + done.reduce((s, r) => s + (r.audited || 0), 0))
return { batches: ok, totalAudited: done.reduce((s, r) => s + (r.audited || 0), 0) }