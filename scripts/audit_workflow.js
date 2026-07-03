export const meta = {
  name: 'atlas-full-audit',
  description: 'Grade every atlas entity for genuineness (is it a capital allocator?) and classification fit, from its live homepage',
  phases: [{ title: 'Audit', detail: 'batch judging agents fetch + judge' }],
}

const BOOTSTRAP_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    entities: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: { name: { type: 'string' }, assigned_class: { type: 'string' }, entity_type: { type: 'string' }, website: { type: 'string' } },
        required: ['name', 'assigned_class', 'website'],
      },
    },
  },
  required: ['entities'],
}

phase('Load')
let entities = (args && args.entities) || []
if (!entities.length) {
  const boot = await agent(
    `Read the file data/evidence/industry_entities.csv (use the Read tool or python). Return EVERY row as JSON: {entities:[{name, assigned_class (= the primary_asset_class column), entity_type, website}]}. Include all rows, do not truncate or sample. Do not call advisor.`,
    { label: 'load-entities', phase: 'Load', schema: BOOTSTRAP_SCHEMA }
  )
  entities = (boot && boot.entities) || []
}
log(`loaded ${entities.length} entities to audit`)
const BATCH = 12
const batches = []
for (let i = 0; i < entities.length; i += BATCH) batches.push({ start: i, items: entities.slice(i, i + BATCH) })

const SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          name: { type: 'string' },
          is_allocator: { type: 'boolean' },
          page_type: { type: 'string', enum: ['allocator', 'article_or_blog', 'product_or_saas', 'marketplace_or_broker', 'network_or_membership', 'consultancy_or_advisor', 'accelerator_no_capital', 'other'] },
          self_described_class: { type: 'string', enum: ['SMV', 'Patient Capital', 'LMV', 'Search/ETA', 'Portfolio Capital', 'Sovereign Capital', 'UVC', 'none'] },
          class_match: { type: 'boolean' },
          verdict: { type: 'string', enum: ['genuine_correct', 'genuine_misclassified', 'junk_not_allocator', 'unverifiable'] },
          note: { type: 'string' },
        },
        required: ['name', 'is_allocator', 'page_type', 'self_described_class', 'class_match', 'verdict', 'note'],
      },
    },
  },
  required: ['verdicts'],
}

const RULES = `You audit rows of a "Post-Unicorn Finance" atlas of CAPITAL ALLOCATORS operating OUTSIDE classic unicorn VC. An ALLOCATOR deploys its OWN (or its LPs') capital into companies via equity, debt, revenue-share, or acquisition. Valid classes (all are allocator types): SMV (revenue-based/non-dilutive growth capital), Patient Capital (permanent equity, evergreen, steward-ownership, family offices, endowments, mission/impact long-hold), LMV (solo-GP/micro/indie VC, accelerators+fellowships THAT INVEST), Search/ETA (search funds, ETA, independent sponsors), Portfolio Capital (serial acquirers, holdcos, venture studios, roll-ups), Sovereign Capital (sovereign wealth, public investment banks, DFIs, catalytic/blended/climate institutional finance). UVC = classic unicorn VC, the baseline we contrast AGAINST (not a valid atlas class).

NOT allocators (is_allocator=false, verdict=junk_not_allocator): marketplaces/brokers that match buyers&sellers for a fee (e.g. Acquire.com, Flippa), embedded-finance products/SaaS infrastructure, membership/industry networks, pure advisory/consultancies, accelerators that deploy NO capital, and article/blog/listicle pages.

Process: do NOT call advisor. For each entity, fetch its homepage ONCE (load WebFetch via ToolSearch "select:WebFetch" if needed; if WebFetch is blocked/403/JS-only, that entity = unverifiable). Judge ONLY from the page. Then emit the structured object.

Per entity decide: is_allocator; page_type; self_described_class (how THEY describe themselves; UVC or none allowed); class_match (is assigned_class defensible?); verdict (genuine_correct | genuine_misclassified | junk_not_allocator | unverifiable); note (one sentence citing the page).`

phase('Audit')
const results = await parallel(
  batches.map((b) => () => {
    const list = b.items.map((e) => `${e.name} || ${e.assigned_class} || ${e.entity_type} || ${e.website}`).join('\n')
    return agent(`${RULES}\n\nENTITIES (name || assigned_class || entity_type || website):\n${list}\n\nReturn the structured object with one verdict per entity above.`,
      { label: `audit:${b.start}`, phase: 'Audit', schema: SCHEMA })
      .then((r) => (r && r.verdicts ? r.verdicts : []))
      .catch(() => [])
  })
)
const all = results.flat().filter(Boolean)
const by = (v) => all.filter((x) => x.verdict === v).length
log(`audited ${all.length}/${entities.length}: correct=${by('genuine_correct')} misclassified=${by('genuine_misclassified')} junk=${by('junk_not_allocator')} unverifiable=${by('unverifiable')}`)
return { audited: all.length, total: entities.length, verdicts: all }
