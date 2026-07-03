export const meta = {
  name: 'atlas-reverify-junk',
  description: 'Adversarially re-check entities flagged as non-allocators — try to REFUTE the junk call by finding evidence they deploy their own capital',
  phases: [{ title: 'Load' }, { title: 'Refute' }],
}

const SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    results: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          name: { type: 'string' },
          deploys_own_capital: { type: 'boolean', description: 'true if the firm puts its OWN/LP capital into companies (fund, lending, revenue-share, acquisitions, investments)' },
          is_allocator: { type: 'boolean' },
          best_class: { type: 'string', enum: ['SMV', 'Patient Capital', 'LMV', 'Search/ETA', 'Portfolio Capital', 'Sovereign Capital', 'UVC', 'none'] },
          ruling: { type: 'string', enum: ['rescued_allocator', 'confirmed_non_allocator', 'unverifiable'] },
          evidence: { type: 'string', description: 'exact quote or fact from the site supporting the ruling' },
        },
        required: ['name', 'deploys_own_capital', 'is_allocator', 'best_class', 'ruling', 'evidence'],
      },
    },
  },
  required: ['results'],
}

phase('Load')
const boot = await agent(
  `Read the JSON file data/runtime/audit_triage.json (use Read or python). Return its "firmjunk" array as {entities:[{name, assigned_class, website, note}]} (map each firmjunk item's fields; assigned_class from any class field if present else ""). Include ALL items, do not truncate. Do not call advisor.`,
  { label: 'load-firmjunk', phase: 'Load', schema: { type: 'object', additionalProperties: true, properties: { entities: { type: 'array', items: { type: 'object', additionalProperties: true, properties: { name: { type: 'string' }, website: { type: 'string' }, note: { type: 'string' } }, required: ['name'] } } }, required: ['entities'] } }
)
const entities = (boot && boot.entities) || []
log(`re-checking ${entities.length} flagged non-allocators`)

const BATCH = 10
const batches = []
for (let i = 0; i < entities.length; i += BATCH) batches.push({ start: i, items: entities.slice(i, i + BATCH) })

const RULES = `These entities were flagged as NOT capital allocators for a "Post-Unicorn Finance" atlas. Your job is ADVERSARIAL: actively try to REFUTE that flag. A capital allocator DEPLOYS ITS OWN (or LPs') capital into companies via equity, debt, revenue-share, or acquisition.

Be skeptical of the flag: many real lenders/funds look like "platforms" or "products" (e.g. an embedded-financing firm that says "Our capital" IS a real lender). Search the homepage AND obvious subpages (/about, /portfolio, /funds, /invest, /how-it-works) for evidence they deploy their own capital. Use WebFetch (load via ToolSearch "select:WebFetch,WebSearch" if needed). Do NOT call advisor.

Conclude per entity:
- deploys_own_capital: does the firm put its own/LP money into companies? (a marketplace/broker that only matches buyers&sellers for a fee = NO; a pure network/standards body = NO; a pure advisory/nonprofit = NO; an accelerator that takes no equity & writes no checks = NO; a lender/fund/holdco/RBF provider = YES)
- is_allocator, best_class (which atlas class fits if it IS an allocator; else none)
- ruling: rescued_allocator (it IS a real allocator, wrongly flagged), confirmed_non_allocator (flag stands), or unverifiable (page dead/blocked/thin)
- evidence: exact quote/fact from the site`

phase('Refute')
const results = await parallel(
  batches.map((b) => () => {
    const list = b.items.map((e) => `${e.name} || ${e.website} || prior_flag_reason: ${(e.note || '').slice(0, 90)}`).join('\n')
    return agent(`${RULES}\n\nENTITIES (name || website || prior_flag_reason):\n${list}\n\nReturn the structured object with one result per entity.`,
      { label: `refute:${b.start}`, phase: 'Refute', schema: SCHEMA })
      .then((r) => (r && r.results ? r.results : []))
      .catch(() => [])
  })
)
const all = results.flat().filter(Boolean)
const by = (r) => all.filter((x) => x.ruling === r).length
log(`re-checked ${all.length}: rescued=${by('rescued_allocator')} confirmed_junk=${by('confirmed_non_allocator')} unverifiable=${by('unverifiable')}`)
return { results: all }
