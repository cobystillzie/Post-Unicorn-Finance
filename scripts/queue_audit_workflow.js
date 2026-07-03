export const meta = {
  name: 'queue-audit',
  description: 'Full allocator-test audit on every queue lead (needs_more_source / needs_review / queued)',
  phases: [{ title: 'Load' }, { title: 'Audit' }, { title: 'Refute' }],
}

const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          lead_id: { type: 'string' },
          name: { type: 'string' },
          is_allocator: { type: 'boolean', description: 'true if it deploys its OWN/LP capital into companies' },
          page_type: { type: 'string', enum: ['allocator','marketplace_or_broker','network_or_membership','consultancy_or_advisor','accelerator_no_capital','product_or_saas','article_or_blog','other'] },
          self_described_class: { type: 'string', enum: ['SMV','Patient Capital','LMV','Search/ETA','Portfolio Capital','Sovereign Capital','UVC','none'] },
          class_match: { type: 'boolean', description: 'true if target_class is a reasonable fit for the firm self-description' },
          verdict: { type: 'string', enum: ['genuine_correct','genuine_misclassified','junk_not_allocator','unverifiable'] },
          note: { type: 'string', description: 'one short sentence citing a phrase from the homepage' },
        },
        required: ['lead_id','name','is_allocator','page_type','self_described_class','class_match','verdict','note'],
      },
    },
  },
  required: ['verdicts'],
}

phase('Load')
const boot = await agent(
  `Read C:/Users/cobys/projects/post-unicorn-finance/data/runtime/queue_audit_targets.json (use Read or python). Return its "leads" array verbatim. Include ALL items, do not truncate. Do not call advisor.`,
  { label: 'load-targets', phase: 'Load', schema: { type: 'object', additionalProperties: true, properties: { leads: { type: 'array', items: { type: 'object', additionalProperties: true, properties: { lead_id: { type: 'string' }, name: { type: 'string' }, website: { type: 'string' }, target_class: { type: 'string' }, target_role: { type: 'string' }, review_status: { type: 'string' }, notes: { type: 'string' } }, required: ['lead_id','name','website','target_class'] } } }, required: ['leads'] } }
)
const leads = (boot && boot.leads) || []
log(`auditing ${leads.length} queue leads`)

const BATCH = 8
const batches = []
for (let i = 0; i < leads.length; i += BATCH) batches.push({ start: i, items: leads.slice(i, i + BATCH) })

const AUDIT_RULES = `You are auditing leads in a Post-Unicorn Finance industry atlas. For each lead you must DECIDE three things from its homepage:
(1) is_allocator: does this entity DEPLOY ITS OWN/LP CAPITAL into companies (equity/debt/revenue-share/acquisition)? A marketplace/broker that only matches buyers&sellers = NO. A pure network/standards body = NO. A pure advisory/nonprofit = NO. An accelerator that takes no equity & writes no checks = NO. An article/listicle = NO (page_type 'article_or_blog'). A SaaS product = NO. A real fund/lender/holdco/RBF provider = YES. A balance-sheet lender that ORIGINATES off its own warehouse facilities, even if "embedded" or "platform-branded", IS an allocator.
(2) self_described_class: which existing atlas class fits the firm's self-description?
(3) class_match: is the assigned target_class a reasonable fit?

Use WebFetch (load via ToolSearch "select:WebFetch" if needed) on the lead's website (and one obvious subpage like /about if homepage is thin). Do NOT call advisor. Do NOT spawn other agents. Quote a real phrase from the homepage in the note.

verdict mapping:
- 'genuine_correct'        — is_allocator AND class_match
- 'genuine_misclassified'  — is_allocator AND NOT class_match (or target_class clearly wrong)
- 'junk_not_allocator'     — NOT is_allocator
- 'unverifiable'           — page dead/403/JS-only/thin so you cannot judge

Be skeptical of lookalikes (embedded-finance, marketplaces, networks) but ALSO skeptical of false-junk calls — if the firm has a fund page or "Our capital" wording, it IS likely an allocator. Default to 'unverifiable' rather than guessing.`

phase('Audit')
const verdicts = await parallel(
  batches.map((b) => () => {
    const list = b.items.map((e) => `lead_id="${e.lead_id}" | name="${e.name}" | website=${e.website} | target_class=${e.target_class} | target_role=${e.target_role}`).join('\n')
    return agent(`${AUDIT_RULES}\n\nLEADS TO JUDGE (one verdict per lead):\n${list}\n\nReturn the structured object with one verdict per lead.`,
      { label: `audit:${b.start}`, phase: 'Audit', schema: VERDICT_SCHEMA })
      .then((r) => (r && r.verdicts ? r.verdicts : []))
      .catch(() => [])
  })
)
const allVerdicts = verdicts.flat().filter(Boolean)
const counts = (k) => allVerdicts.filter((v) => v.verdict === k).length
log(`audit done: genuine_correct=${counts('genuine_correct')} misclass=${counts('genuine_misclassified')} junk=${counts('junk_not_allocator')} unverifiable=${counts('unverifiable')}`)

// Phase 3: adversarial recheck on flagged junk only
const flaggedJunk = allVerdicts.filter((v) => v.verdict === 'junk_not_allocator')

const RESCUE_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    results: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          lead_id: { type: 'string' },
          name: { type: 'string' },
          deploys_own_capital: { type: 'boolean' },
          is_allocator: { type: 'boolean' },
          best_class: { type: 'string', enum: ['SMV','Patient Capital','LMV','Search/ETA','Portfolio Capital','Sovereign Capital','UVC','none'] },
          ruling: { type: 'string', enum: ['rescued_allocator','confirmed_non_allocator','unverifiable'] },
          evidence: { type: 'string' },
        },
        required: ['lead_id','name','deploys_own_capital','is_allocator','best_class','ruling','evidence'],
      },
    },
  },
  required: ['results'],
}

const RESCUE_RULES = `Adversarially re-check entities flagged as NOT capital allocators. Try to REFUTE the flag: find evidence that the firm DEPLOYS ITS OWN (or LP) CAPITAL. Many real lenders look like "platforms" or "products"; if the firm raises warehouse facilities, lists "Our capital", has a /fund or /invest page, or reports own-balance-sheet deployments, it IS an allocator. Use WebFetch (and /about, /portfolio, /invest, /how-it-works subpages). Do NOT call advisor.

rulings:
- 'rescued_allocator'        — firm IS a real allocator; flag stands incorrect
- 'confirmed_non_allocator'  — flag stands; marketplace/network/advisory/article confirmed
- 'unverifiable'             — page genuinely cannot be judged`

phase('Refute')
let rescueResults = []
if (flaggedJunk.length > 0) {
  const RBATCH = 8
  const rbatches = []
  for (let i = 0; i < flaggedJunk.length; i += RBATCH) rbatches.push({ start: i, items: flaggedJunk.slice(i, i + RBATCH) })
  rescueResults = (await parallel(
    rbatches.map((b) => () => {
      const list = b.items.map((e) => `lead_id="${e.lead_id}" | name="${e.name}" | flag_reason="${(e.note || '').slice(0, 100)}"`).join('\n')
      return agent(`${RESCUE_RULES}\n\nFLAGGED-AS-JUNK LEADS:\n${list}\n\nReturn the structured object.`,
        { label: `refute:${b.start}`, phase: 'Refute', schema: RESCUE_SCHEMA })
        .then((r) => (r && r.results ? r.results : []))
        .catch(() => [])
    })
  )).flat().filter(Boolean)
  const rescued = rescueResults.filter((r) => r.ruling === 'rescued_allocator').length
  log(`re-checked ${rescueResults.length} flagged-junk: rescued=${rescued}`)
}
return { verdicts: allVerdicts, rescues: rescueResults }
