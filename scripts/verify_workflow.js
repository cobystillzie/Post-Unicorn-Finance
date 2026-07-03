export const meta = {
  name: 'atlas-verify-sample',
  description: 'Judge a sample of atlas entities for genuineness + classification from their pre-fetched homepage text',
  phases: [{ title: 'Judge', detail: 'one judging agent per entity (text passed in, no fetching)' }],
}

const items = (args && args.items) || []

const VERDICT_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    name: { type: 'string' },
    is_allocator: { type: 'boolean', description: 'true if the page describes a capital allocator/investor/acquirer/fund/holdco; false if it is an article/blog post/SaaS product/pure consultancy/news/directory' },
    page_type: { type: 'string', enum: ['allocator', 'article_or_blog', 'product_or_saas', 'consultancy_or_advisor', 'directory_or_list', 'other'] },
    self_described_class: { type: 'string', enum: ['SMV', 'Patient Capital', 'LMV', 'Search/ETA', 'Portfolio Capital', 'Sovereign Capital', 'UVC', 'none'], description: 'which class best matches how the firm describes ITSELF (UVC = classic unicorn venture capital; none = not an allocator)' },
    class_match: { type: 'boolean', description: 'true if assigned_class is a defensible fit for the self-description' },
    verdict: { type: 'string', enum: ['genuine_correct', 'genuine_misclassified', 'junk_not_allocator', 'unverifiable'] },
    note: { type: 'string', description: 'one sentence justification citing the page' },
  },
  required: ['name', 'is_allocator', 'page_type', 'self_described_class', 'class_match', 'verdict', 'note'],
}

phase('Judge')
const verdicts = await parallel(
  items.map((it) => () =>
    agent(
      `You are auditing one row of a "Post-Unicorn Finance" atlas of capital allocators that operate OUTSIDE classic unicorn venture capital. Classes: SMV (revenue-based/non-dilutive growth), Patient Capital (permanent equity, evergreen, steward-ownership, family offices, endowments, mission/impact long-hold), LMV (solo-GP/micro/indie funds, accelerators, fellowships), Search/ETA (search funds, ETA, independent sponsors), Portfolio Capital (serial acquirers, holdcos, studios, roll-ups), Sovereign Capital (sovereign wealth, public investment banks, DFIs, catalytic/blended/climate institutional finance). UVC = the classic unicorn VC we contrast AGAINST (not a valid atlas class).

Judge ONLY from the homepage text provided. Do not invent facts. If the text is too thin to tell, verdict = "unverifiable".

ENTITY: ${it.name}
ASSIGNED CLASS: ${it.assigned_class}
ASSIGNED ENTITY TYPE: ${it.entity_type}
WEBSITE: ${it.website}
HOMEPAGE TEXT (truncated):
"""${(it.text || '').slice(0, 2000)}"""

Decide: (1) is_allocator — is this an actual capital allocator/investor/acquirer/fund, or an article/blog/SaaS product/pure consultancy/directory? (2) self_described_class — which class fits how they describe THEMSELVES? (3) class_match — is the ASSIGNED class defensible? Set verdict: genuine_correct (real allocator + class fits), genuine_misclassified (real allocator but wrong class — name the right one in note), junk_not_allocator (not an allocator at all), or unverifiable (text too thin).`,
      { label: `judge:${it.name}`.slice(0, 40), phase: 'Judge', schema: VERDICT_SCHEMA }
    ).then((v) => v || { name: it.name, verdict: 'unverifiable', note: 'agent returned nothing' })
  )
)

const ok = verdicts.filter(Boolean)
const by = (k, val) => ok.filter((v) => v[k] === val).length
log(`judged ${ok.length}: correct=${by('verdict', 'genuine_correct')} misclassified=${by('verdict', 'genuine_misclassified')} junk=${by('verdict', 'junk_not_allocator')} unverifiable=${by('verdict', 'unverifiable')}`)
return { verdicts: ok }
