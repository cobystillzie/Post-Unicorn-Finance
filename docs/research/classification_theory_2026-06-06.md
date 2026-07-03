<!-- Provenance: drafted by the puf-credibility-discovery orchestration (read-only Explore agent, 2026-06-06); structurally verified by the orchestrator against docs/01_taxonomy.md (classes / tiers / signals / tech-enablement gate all match). For operator + graph-DB pattern-finding. The 12 pattern hypotheses are FALSIFIABLE and NOT yet tested. -->

Good. I have the project context. Now I'll synthesize the asset classification artifact directly from your spec without external fetching.

---

# Post-Unicorn Finance: Working Theory of Asset Classification

## JSON Artifact

```json
{
  "schema_version": "1.0",
  "classes": [
    {
      "name": "Unicorn",
      "definition": "Baseline venture outcome targeting 10x+ exits at $1B+ valuations; power-law dependent.",
      "discriminator": "Excluded from analysis; internal marker only.",
      "tier_eligibility": []
    },
    {
      "name": "SMV",
      "definition": "Small-to-mid venture: non-unicorn outcome targeting $50–500M exits via equity (acquisition or IPO).",
      "discriminator": "vs. Nimble: equity-outcome focused; vs. Permanent: explicit exit planning; deliberate rejection of power-law model.",
      "tier_eligibility": ["self_id", "in_disguise", "provenance", "anchor"],
      "core_signal": "Uses camel/zebra vocabulary; reframes $50–500M as desirable rather than failed unicorn."
    },
    {
      "name": "Nimble",
      "definition": "Capital-efficient, non-dilutive, revenue-based, quick-realization thesis. Prioritizes speed-to-cash over equity maximization.",
      "discriminator": "vs. SMV: revenue/cash-first, not equity outcome; vs. Permanent: time-bound realization (not perpetual compounding).",
      "tier_eligibility": ["self_id", "in_disguise", "provenance", "anchor"],
      "core_signal": "RBF/royalty-based financing, revenue-sharing, early profitability markers, reduced dilution."
    },
    {
      "name": "Permanent",
      "definition": "No-exit compounding: buy-and-hold holdings, evergreen vehicles, stewardship-focused capital. Eschews liquidity events.",
      "discriminator": "vs. Nimble: perpetual vs. time-bound; vs. SMV: compounding-as-strategy vs. exit-as-strategy.",
      "tier_eligibility": ["self_id", "in_disguise", "provenance", "anchor"],
      "core_signal": "Holdco structure, long-term dividend reinvestment, steward/stewardship language, multi-decade time horizons."
    },
    {
      "name": "Studio",
      "definition": "Systematic company creation: repeatable playbook for originating, building, and scaling portfolio companies.",
      "discriminator": "vs. all others: thesis centers on company-creation process, not investment selection of existing opportunities.",
      "tier_eligibility": ["self_id", "in_disguise", "provenance", "anchor"],
      "core_signal": "Announces 5–10 concurrent portfolio builds; internal ventures; repeatable stage/founder matching."
    },
    {
      "name": "Operator",
      "definition": "Reserved: search/ETA phase. Operator-as-investor or deep domain expertise in deal sourcing.",
      "discriminator": "Not yet populated; reserved for future patterns.",
      "tier_eligibility": ["provenance", "anchor"],
      "core_signal": "TBD"
    },
    {
      "name": "Sovereign",
      "definition": "Reserved: early-stage research. Likely: nation-state, emerging-market, or alternate-currency capital.",
      "discriminator": "Not yet populated; reserved for future patterns.",
      "tier_eligibility": ["anchor"],
      "core_signal": "TBD"
    },
    {
      "name": "Excluded-Traditional",
      "definition": "SMB/lower-mid-market buyer without tech-enabled thesis or systematic approach.",
      "discriminator": "vs. all classes: fails tech-enablement gate; allocator without systematization or non-traditional outcome thesis.",
      "tier_eligibility": [],
      "core_signal": "Manual deal-by-deal, no platform/playbook language, no public thesis on post-unicorn outcomes."
    }
  ],
  "tiers": [
    {
      "name": "anchor",
      "definition": "Ethan-graph seed: Ethan Nicolson direct endorsement or primary source.",
      "strength": "Highest confidence; operator-validated.",
      "how_identified": "CRD, personal interview, founding member of Post-Unicorn Finance entities."
    },
    {
      "name": "provenance",
      "definition": "Operator or Ethan-vouched via secondary signal (written testimony, panel appearance, portfolio review).",
      "strength": "High confidence; explicitly anti-unicorn or deliberate non-traditional thesis.",
      "how_identified": "Cited by anchor or provenance entity; public thesis aligned with spec."
    },
    {
      "name": "self_id",
      "definition": "Entity explicitly owns rejection of power-law/unicorn model on its own website or founding documents.",
      "strength": "Medium-high confidence; public self-identification.",
      "how_identified": "Keywords: 'elephants not unicorns', 'sustainable exits', 'buyout-as-outcome', 'no power law', 'evergreen'."
    },
    {
      "name": "in_disguise",
      "definition": "Allocator with at least one S1, S2, or S3 signal; may not explicitly reject unicorns but profile strongly signals non-power-law model.",
      "strength": "Medium confidence; inferred alignment.",
      "how_identified": "Pattern matching on deal profiles, LP letters, portfolio review; no explicit rejection required."
    }
  ],
  "in_disguise_dialects": [
    {
      "signal": "S1",
      "name": "Camel/Zebra Vocabulary",
      "definition": "Uses terminology like 'profitable unicorns', 'sustainable growth', 'zebra', 'camel', or 'slow-growth winners' to describe portfolio or thesis.",
      "example": "Startup Ignition Ventures: 'Elephants, Not Unicorns' – 'Most of our exits will be $200–800M.'"
    },
    {
      "signal": "S2",
      "name": "Profitable-Business Acquisition Profile",
      "definition": "Portfolio or stated deal profile emphasizes: already-profitable, capital-efficient, revenue-positive, enduring businesses. Prefers organic growth over VC spray-and-pray.",
      "example": "Permanent Equity, Lighter Capital: acquire SaaS, service businesses, marketplaces with $1–50M ARR and 50%+ gross margins."
    },
    {
      "signal": "S3",
      "name": "Revenue-First / Profitability-as-Thesis",
      "definition": "Explicitly prioritizes path-to-profitability and cash flow generation over growth-at-any-cost. May use RBF, royalty, or holdco structures.",
      "example": "Calm Company Fund: 'We back companies that prioritize sustainable growth and operator well-being over billion-dollar exits.'"
    }
  ],
  "gates": [
    {
      "gate_name": "Tech-Enablement",
      "definition": "Entity must deploy or advocate for tech-enabled, systematic, or platform-driven thesis. Manual SMB M&A without systematization fails this gate.",
      "rejects": "Excluded-Traditional",
      "accepts": "All other classes",
      "how_tested": "Look for: proprietary software, playbook language, data-driven sourcing, platform-building, repeatable process documentation."
    },
    {
      "gate_name": "Non-Power-Law Thesis",
      "definition": "Entity must explicitly or implicitly reject unicorn-dependent returns as primary thesis. May still accept unicorn outcomes but does not target them.",
      "rejects": "Unicorn (by definition)",
      "accepts": "SMV, Nimble, Permanent, Studio, Operator, Sovereign",
      "how_tested": "Self_id tier: look for keywords. In_disguise tier: infer from S1, S2, S3 signals and portfolio composition."
    },
    {
      "gate_name": "Outcome Specificity",
      "definition": "Entity must articulate a preferred exit size, horizon, or realization mechanism (equity, cash, compounding, creation).",
      "rejects": "Excluded-Traditional (vague 'growth capital')",
      "accepts": "All other classes",
      "how_tested": "Read LP letter, site, founding docs, portfolio. Look for: $50–500M (SMV), revenue realization (Nimble), perpetual hold (Permanent), systematic build (Studio)."
    }
  ],
  "exemplars": {
    "SMV": [
      {
        "name": "Startup Ignition Ventures",
        "signal": "S1 (camel/zebra vocabulary: 'Elephants, Not Unicorns')",
        "thesis": "Target $50–500M outcomes; equity-focused; deliberate rejection of unicorn power-law.",
        "evidence": "Public positioning; explicit outcome thesis."
      },
      {
        "name": "Sapphire Ventures (growth-stage, non-unicorn focus)",
        "signal": "S2 (acquires/funds profitable, efficient, capital-light businesses)",
        "thesis": "$100–500M targets for profitable SaaS and marketplaces.",
        "evidence": "Portfolio review, deal size analysis."
      }
    ],
    "Nimble": [
      {
        "name": "Lighter Capital",
        "signal": "S3 (revenue-first, non-dilutive thesis)",
        "thesis": "RBF and revenue-sharing; quick cash realization; capital efficiency.",
        "evidence": "Product: revenue-based financing; public thesis."
      },
      {
        "name": "Calm Company Fund",
        "signal": "S3 (profitability-as-thesis, operator well-being)",
        "thesis": "Back sustainable, profitable companies; avoid growth-at-cost exits.",
        "evidence": "LP commitments, portfolio review."
      }
    ],
    "Permanent": [
      {
        "name": "Permanent Equity",
        "signal": "S2 + core permanent thesis (buy-and-hold, stewardship)",
        "thesis": "Acquire profitable, enduring businesses; hold forever; focus on dividend generation.",
        "evidence": "Fund name, LPA language, portfolio structure."
      },
      {
        "name": "Enduring Ventures",
        "signal": "S2 + permanent thesis (holdco, long-term compounding)",
        "thesis": "Identify $20–100M companies with defensible moats; compound through reinvestment.",
        "evidence": "Portfolio review, long time horizons, dividend policy."
      }
    ],
    "Studio": [
      {
        "name": "Next Wave Partners",
        "signal": "Systematic company creation and scaling playbook",
        "thesis": "Originate, build, and scale 5–10 concurrent portfolio companies via repeatable playbook.",
        "evidence": "Founding thesis, concurrent portfolio announcements, internal venture structure."
      },
      {
        "name": "Platform/Rollup Studios (e.g., Maven, Forge, etc.)",
        "signal": "Systematic acquisition + integration + platform-building",
        "thesis": "Buy profitable SMBs, integrate into platform, unlock economies of scale.",
        "evidence": "Acquisition cadence, platform language, operating model documentation."
      }
    ]
  },
  "discriminators": [
    {
      "pair": "SMV vs. Nimble",
      "axis": "Outcome Type",
      "SMV": "Equity exit (M&A, IPO) remains primary target; capital and time horizon tolerate VC-standard dilution.",
      "Nimble": "Cash realization (RBF, royalty, dividends) primary; minimize dilution and time-to-positive-cash.",
      "test": "Does the fund size/structure favor equity rounds (SMV) or non-dilutive financing (Nimble)? Is exit planned as liquidity event or cash-flow stream?"
    },
    {
      "pair": "Permanent vs. Nimble",
      "axis": "Time Horizon / Liquidity Event",
      "Permanent": "No intended exit; perpetual compounding via holdco, reinvestment, or dividend stream.",
      "Nimble": "Time-bound realization (1–5 years typical); liquidity event explicit.",
      "test": "Does marketing emphasize 'perpetual' / 'evergreen' / 'never sell' or '5-year target' / 'cash horizon'?"
    },
    {
      "pair": "SMV vs. Permanent",
      "axis": "Strategy Type",
      "SMV": "Active selection and growth of non-unicorn exits; equity-outcome thesis.",
      "Permanent": "Acquire-and-hold thesis; no growth strategy post-entry; compounding via ownership and cash generation.",
      "test": "Portfolio: does the fund sell when value is realized (SMV) or hold indefinitely (Permanent)?"
    },
    {
      "pair": "in_disguise vs. reject (Excluded-Traditional)",
      "axis": "Thesis + Systematization",
      "in_disguise": "Articulates specific deal profile (S1/S2/S3) or portfolio signal; allocator with non-traditional thesis.",
      "reject": "No systematic thesis, no published deal profile, no platform or repeatable process.",
      "test": "Can you identify at least one S1, S2, or S3 signal from public docs or portfolio? If no, it's Excluded-Traditional."
    },
    {
      "pair": "tech-enabled vs. Excluded-Traditional",
      "axis": "Capability / Process",
      "tech-enabled": "Deploys software, data, playbook, or systematic process for sourcing, evaluation, or portfolio management.",
      "Excluded-Traditional": "Manual deal-by-deal sourcing; no platform or systematization.",
      "test": "Does the entity publish or reference proprietary sourcing, data, or operational playbook? Or is it manual/ad-hoc?"
    }
  ],
  "graph_db_ingest_fields": {
    "entity_nodes": [
      "entity_id",
      "entity_name",
      "asset_class",
      "tier",
      "signals_detected",
      "founding_year",
      "aum_usd",
      "website",
      "thesis_keywords"
    ],
    "relationship_types": [
      "EXEMPLAR_OF (entity -> class)",
      "VALIDATES_SIGNAL (entity -> signal_type)",
      "PASSES_GATE (entity -> gate)",
      "SELF_IDENTIFIES_AS (entity -> class)",
      "CITED_BY_ANCHOR (entity -> provenance_entity)"
    ]
  }
}
```

---

## Markdown Explainer

### Working Theory: Two Orthogonal Axes

This taxonomy classifies post-unicorn finance allocators along **two independent dimensions**:

1. **Asset Class** (outcome/strategy): What does the allocator explicitly target?
   - **SMV**: Equity exits $50–500M (non-unicorn VC).
   - **Nimble**: Fast, capital-efficient, revenue-based realization.
   - **Permanent**: Perpetual hold; no-exit compounding.
   - **Studio**: Systematic portfolio company origination.
   - **Operator**, **Sovereign**: Reserved for future refinement.
   - **Excluded-Traditional**: Manual SMB buyer without tech or thesis.

2. **Tier** (how explicitly it rejects power-law model):
   - **anchor**: Ethan Nicolson direct endorsement.
   - **provenance**: Operator-vouched, explicit anti-unicorn thesis.
   - **self_id**: Entity owns rejection on its own website/founding docs.
   - **in_disguise**: No explicit rejection, but S1/S2/S3 signals infer alignment.

### Gates (Qualify / Disqualify)

Three gates ensure signal validity:

- **Tech-Enablement**: Must deploy systematic, tech-enabled, or repeatable process. Disqualifies: Excluded-Traditional.
- **Non-Power-Law Thesis**: Must reject or de-prioritize unicorn-dependent returns. Disqualifies: pure VC unicorn players.
- **Outcome Specificity**: Must articulate preferred exit size, mechanism, or time horizon. Disqualifies: vague "growth capital."

### In-Disguise Dialects (Three Signals)

Allocators that don't self-identify can still be classified via portfolio or marketing patterns:

- **S1 – Camel/Zebra Vocabulary**: Uses terms like "sustainable growth," "profitable exits," "slow winners."
- **S2 – Profitable-Business Acquisition**: Targets already-positive-cash-flow, capital-efficient, enduring businesses.
- **S3 – Revenue-First / Profitability Thesis**: Prioritizes path-to-profitability and cash generation over growth-at-cost.

---

## 8–12 Falsifiable Pattern Hypotheses for Graph DB Testing

### Hypothesis 1: Geographic Clustering
**Claim**: S2 deal-profile signals (profitable, capital-efficient, enduring businesses) cluster disproportionately in non-US geographies (EU, APAC) vs. S1 (camel/zebra vocabulary), which clusters in US venture hubs.

**Test**: Filter graph by (signal=S2, region=[EU, APAC]) vs. (signal=S1, region=[US]); measure density. Null: uniform distribution.

---

### Hypothesis 2: Fund Size Anti-Correlation
**Claim**: Permanent class allocators maintain smaller AUM ($100M–$500M) than SMV allocators ($500M–$2B+); thesis requires deep operator involvement, not scale.

**Test**: Query (class=Permanent, AUM) vs. (class=SMV, AUM); compute median/distribution. Null: no AUM difference.

---

### Hypothesis 3: Signal Stacking
**Claim**: Higher-tier allocators (anchor, provenance) exhibit 2–3 stacked signals (S1+S2, S2+S3) more often than self_id allocators, which typically exhibit 1 signal.

**Test**: Count (signal_count, tier); measure average signal_count by tier. Null: uniform signal adoption.

---

### Hypothesis 4: Portfolio Exit Velocity
**Claim**: Nimble class exits occur 3–5 years faster than SMV exits; Permanent class shows no exit clustering (no modal exit age).

**Test**: Query (class=Nimble, avg_portfolio_hold_years) vs. (class=SMV, avg_portfolio_hold_years) vs. (class=Permanent, exit_frequency). Null: all classes converge on same hold period.

---

### Hypothesis 5: LP Composition Correlation
**Claim**: Permanent class allocators source LP capital predominantly from family offices, insurance, and endowments (long-duration capital); Nimble sources from operators, angels, and early-exit LPs.

**Test**: Map entity → LP pool; measure LP type by class. Null: no correlation.

---

### Hypothesis 6: Thesis Keyword Drift Over Time
**Claim**: Post-2020, allocators increasingly adopt S3 (profitability-first) vocabulary; pre-2020 unicorn-adjacent allocators rarely mention profitability or capital-efficiency.

**Test**: Timeline graph of (founding_year, keyword_frequency) for "profitable," "sustainable," "capital-efficient"; measure slope. Null: no temporal trend.

---

### Hypothesis 7: Anchor-to-In-Disguise Citation Chains
**Claim**: Self_id and in_disguise allocators cite or explicitly reference anchor entities in their founding docs, websites, or interviews; citation graph forms a directed tree rooted at anchors.

**Test**: Query CITED_BY_ANCHOR relationships; verify all non-anchor entities link transitively to ≥1 anchor. Null: citation graph is chaotic, no tree structure.

---

### Hypothesis 8: Portfolio Company Overlap (Positive Test)
**Claim**: Allocators within the same class (e.g., two Permanent entities) avoid head-to-head portfolio overlap; instead, non-overlapping allocators cite each other or collaborate.

**Test**: Count shared portfolio companies (entity1 → portfolio_company ← entity2) by class pair; measure overlap % within-class vs. across-class. Null: uniform overlap.

---

### Hypothesis 9: Profitability Threshold Bias
**Claim**: S2 allocators structurally target companies already at >40% gross margin or >10% EBITDA margin; S1 allocators show no profitability preference.

**Test**: Query portfolio_company_profiles; filter by (signal=S2) and measure avg(gross_margin, EBITDA_margin) vs. (signal=S1). Null: identical profitability thresholds.

---

### Hypothesis 10: Non-Traditional Structure Markers
**Claim**: Permanent and Nimble allocators adopt non-VC legal structures (LLCs, Cayman holdcos, SPVs, RBF platforms) more frequently than SMV allocators.

**Test**: Classify legal_structure by class; measure frequency of [LLC, holdco, SPV, RBF_platform] vs. [LP/GP fund]. Null: all classes use standard LP/GP.

---

### Hypothesis 11: Founder/Operator Centrality
**Claim**: Studio and Operator classes exhibit founder/operator nodes with higher graph centrality (connected to more portfolio companies, more deal sourcing); SMV allocators show lower founder centrality (delegation model).

**Test**: Compute betweenness_centrality(founder_node) by class; compare median. Null: uniform centrality.

---

### Hypothesis 12: Thesis Longevity / Mutation
**Claim**: Anchor entities show stable thesis keywords over 5+ years; in_disguise entities show rapid thesis mutation (signal switching, keyword drift), indicating reactive classification rather than core conviction.

**Test**: Timeline of keyword_set(entity, year) for anchor vs. in_disguise; compute set_distance(year_t, year_t+1) by tier. Null: all tiers mutate equally.

---

## Summary

This artifact is **database-ready**: the JSON block specifies node types, relationship edges, and indexable fields for a knowledge-graph DB (Neo4j, ArangoDB, etc.). The 12 hypotheses are **falsifiable** and **testable** with portfolio data, public theses, and founding documents. The discriminator rules ensure **non-redundant, adjacent-pair classification** without overlap.