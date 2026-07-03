export const meta = {
  name: 'classification-synthesis-full',
  description: 'Overseer synthesis: pattern-finders cluster all ~500 entity self-descriptions taxonomy-blind, an overseer synthesizes the TRUE emergent asset classification, a critic refutes, a reviser finalizes.',
  phases: [{ title: 'Cluster' }, { title: 'Synthesize' }, { title: 'Critique' }, { title: 'Finalize' }],
}

const NUM_SLICES = 12

const CLUSTER_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    local_clusters: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          theme: { type: 'string' },
          description: { type: 'string' },
          recurring_phrases: { type: 'array', items: { type: 'string' } },
          example_entity_names: { type: 'array', items: { type: 'string' } },
          capital_structure: { type: 'string', description: 'instrument + hold period that defines this cluster' },
        },
        required: ['theme', 'description', 'recurring_phrases', 'example_entity_names', 'capital_structure'],
      },
    },
    surprises: { type: 'array', items: { type: 'string' } },
  },
  required: ['local_clusters', 'surprises'],
}

const CLUSTER_RULES = `You are doing TAXONOMY-BLIND clustering of capital-allocator self-descriptions. Read the file given below (use Read tool). It contains ~42 firms, each with: self_named_role, capital_type, instrument, hold_period, target_companies, geography, verbatim_quotes, signal_phrases, cluster_hint.

DO NOT assume any predefined taxonomy (ignore SMV / Patient Capital / LMV / Search-ETA / Portfolio Capital / Sovereign Capital). Read the actual self-descriptions and let real clusters emerge from HOW THESE FIRMS DESCRIBE THEMSELVES.

For each natural cluster you observe, return: theme (short name), description (1-2 sentences grounded in actual phrases), recurring_phrases (verbatim words multiple firms use), example_entity_names (3-8 from this slice), capital_structure (the instrument + hold-period signature that unifies the cluster — e.g. "permanent-hold equity acquisition", "revenue-share debt, revolving", "two-stage search equity, 5-7y").

Then flag 2-5 surprises: outliers, hybrids, mislabels, or non-allocators (marketplaces, networks, advisories, articles, products) you spot.

Do NOT call advisor. Do NOT spawn other agents. Return ONLY the structured object.`

phase('Cluster')
const slices = []
for (let i = 1; i <= NUM_SLICES; i++) slices.push(i)
const clusterResults = await parallel(
  slices.map((i) => () =>
    agent(`${CLUSTER_RULES}\n\nFILE TO READ: C:/Users/cobys/projects/post-unicorn-finance/data/runtime/synth_slices/slice_${i}.json`,
      { label: `cluster:slice-${i}`, phase: 'Cluster', schema: CLUSTER_SCHEMA })
      .then((r) => (r ? { slice: i, ...r } : null))
      .catch(() => null)
  )
)
const goodClusters = clusterResults.filter(Boolean)
log(`pattern-finders returned: ${goodClusters.length}/${NUM_SLICES} slices`)

// Compact the cluster outputs for the synthesizer prompt
const clusterDigest = goodClusters.map((c) =>
  `=== SLICE ${c.slice} ===\nCLUSTERS:\n` +
  c.local_clusters.map((lc) => `- ${lc.theme} [${lc.capital_structure}]: ${lc.description} | phrases: ${(lc.recurring_phrases || []).slice(0, 6).join(', ')} | examples: ${(lc.example_entity_names || []).slice(0, 6).join(', ')}`).join('\n') +
  `\nSURPRISES: ${(c.surprises || []).join(' | ')}`
).join('\n\n')

const TAXONOMY_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    classes: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          class_id: { type: 'string' },
          name: { type: 'string' },
          definition: { type: 'string' },
          capital_signature: { type: 'string', description: 'the instrument + hold-period + target that defines membership' },
          criteria: { type: 'array', items: { type: 'string' } },
          common_phrases: { type: 'array', items: { type: 'string' } },
          prototype_entity_names: { type: 'array', items: { type: 'string' } },
          estimated_count: { type: 'integer' },
          relationship_to_prior_six: { type: 'string' },
        },
        required: ['class_id', 'name', 'definition', 'capital_signature', 'criteria', 'common_phrases', 'prototype_entity_names', 'estimated_count', 'relationship_to_prior_six'],
      },
    },
    insights: { type: 'array', items: { type: 'string' } },
    coverage_estimate: { type: 'string' },
    ecosystem_non_allocators: { type: 'array', items: { type: 'string' } },
    prior_taxonomy_assessment: {
      type: 'object', additionalProperties: false,
      properties: {
        where_it_works: { type: 'array', items: { type: 'string' } },
        where_it_splits_a_real_category: { type: 'array', items: { type: 'string' } },
        where_it_merges_two_real_categories: { type: 'array', items: { type: 'string' } },
      },
      required: ['where_it_works', 'where_it_splits_a_real_category', 'where_it_merges_two_real_categories'],
    },
  },
  required: ['classes', 'insights', 'coverage_estimate', 'ecosystem_non_allocators', 'prior_taxonomy_assessment'],
}

phase('Synthesize')
const taxonomy = await agent(
  `You are the OVERSEER synthesizing a TRUE, bottom-up emergent taxonomy of "Post-Unicorn Finance" capital allocators from ${goodClusters.length} independent taxonomy-blind clusterings covering ~500 firms total. The current atlas uses 6 prior classes (SMV, Patient Capital, LMV, Search/ETA, Portfolio Capital, Sovereign Capital) but we do NOT trust them — your job is to derive the classification the entities themselves imply.

Themes appearing across MANY slices are STRONG signals. Themes in 1-2 slices may be sub-clusters or noise. Distinguish real ALLOCATORS (deploy own/LP capital) from ECOSYSTEM non-allocators (marketplaces, networks, advisories, articles, products) that recur in the surprises.

Define each class by its CAPITAL SIGNATURE (instrument + hold-period + target), not by vocabulary alone — duration words like "long-term" leak across categories, so the discriminator must be structural. For each class give: class_id, name (grounded in firm self-descriptions), definition, capital_signature, criteria, common_phrases, prototype_entity_names, estimated_count (of ~500), relationship_to_prior_six (honest: keep / split / merge).

Also return: 8-12 insights about the industry, coverage_estimate, ecosystem_non_allocators (firms to remove from the allocator atlas), and prior_taxonomy_assessment (where_it_works / where_it_splits_a_real_category / where_it_merges_two_real_categories).

Do NOT call advisor. Return ONLY the structured object.

PATTERN-FINDER OUTPUTS (${goodClusters.length} slices):\n\n${clusterDigest}`,
  { label: 'overseer-synthesize', phase: 'Synthesize', schema: TAXONOMY_SCHEMA }
)

const CRITIC_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    critical_issues: { type: 'array', items: { type: 'object', additionalProperties: false, properties: { severity: { type: 'string', enum: ['high', 'med', 'low'] }, issue: { type: 'string' }, recommendation: { type: 'string' } }, required: ['severity', 'issue', 'recommendation'] } },
    collapse_proposals: { type: 'array', items: { type: 'string' } },
    split_proposals: { type: 'array', items: { type: 'string' } },
    missing_categories: { type: 'array', items: { type: 'string' } },
    verdict: { type: 'string', enum: ['accept', 'accept_with_revisions', 'major_rework'] },
    summary: { type: 'string' },
  },
  required: ['critical_issues', 'collapse_proposals', 'split_proposals', 'missing_categories', 'verdict', 'summary'],
}

phase('Critique')
const critique = await agent(
  `You are an adversarial critic. REFUTE the proposed emergent taxonomy below. Find overlapping classes that should collapse, single classes that should split, missing categories, suspect counts, and any non-allocators kept as prototypes. Be specific. Do NOT call advisor. Return ONLY the structured object.\n\nPROPOSED TAXONOMY:\n${JSON.stringify(taxonomy).slice(0, 14000)}`,
  { label: 'adversarial-critic', phase: 'Critique', schema: CRITIC_SCHEMA }
)

phase('Finalize')
const final = await agent(
  `You are finalizing the TRUE emergent asset classification for Post-Unicorn Finance. You have a proposed taxonomy and an adversarial critique. Produce the FINAL taxonomy incorporating the valid critiques (collapse/split/add as warranted), plus a clear set of insights for the user. Keep every class grounded in a capital_signature. Do NOT call advisor. Return ONLY the structured object (same shape as the taxonomy: classes[], insights[], coverage_estimate, ecosystem_non_allocators[], prior_taxonomy_assessment{}).\n\nPROPOSED TAXONOMY:\n${JSON.stringify(taxonomy).slice(0, 12000)}\n\nADVERSARIAL CRITIQUE:\n${JSON.stringify(critique).slice(0, 6000)}`,
  { label: 'finalize-taxonomy', phase: 'Finalize', schema: TAXONOMY_SCHEMA }
)

return { final_taxonomy: final, draft_taxonomy: taxonomy, critique, slices_clustered: goodClusters.length }
