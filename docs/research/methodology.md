# Research Methodology

## Evidence First

The primary unit of research is an **entity-claim row**: one source-backed claim about a firm, fund, platform, acquirer, studio, community, instrument provider, or capital source.

Company-event claims are still important, but they are supporting evidence for later paper chapters. They should not drive the first database.

Bad row:

> Firm X is an SMV firm.

Good row:

> Firm X describes itself as investing in profitable or acquisition-oriented technology companies, according to Source A. The research team classifies this as candidate SMV infrastructure until the source text is reviewed in detail.

This structure keeps factual claims separate from classification judgments.

## Evidence Statuses

- `verified_fact`: the source directly supports the claim.
- `candidate_evidence`: the source supports a useful fact, but classification needs more work.
- `inference`: a research judgment derived from evidence.
- `user_thesis`: part of the project thesis, not an external factual claim.
- `needs_verification`: lead retained for follow-up.

## Source Quality

- `primary`: company announcement, investor announcement, filing, official report, founder/company page.
- `credible_press`: reputable business/technology press.
- `research`: academic, institutional, or data-research source.
- `database_seed`: dataset or profile useful for discovery, not final proof.
- `discourse`: founder/investor essay, podcast, community post, or interview.
- `social`: social media or forum post.
- `unknown`: unresolved source quality.

## Research Priority Score

The industry-entity ranking script favors:

- strong asset-class fit,
- official or primary sources,
- active entities,
- clear non-unicorn thesis specificity,
- ecosystem roles with category-building importance,
- and verified facts over unverified leads.

The score is not an investment score. It only decides which atlas leads deserve human verification first.

## First Wave Research Focus

Start broad, then curate.

1. Firms, funds, platforms, acquirers, studios, communities, and providers.
2. Instrument families and provider usage.
3. SMV-specific capital providers and acquisition-first infrastructure.
4. Company outcomes and founder paths as supporting proof.
5. Discourse about the mismatch between power-law VC and most valuable businesses.

The first scrape should be global and tech-enabled. It should aim for volume, but every raw lead must enter a candidate queue until verified.

## Atlas Inclusion Bar

An industry entity can appear in the internal atlas when:

- it has a valid website or source URL,
- at least one claim row references that URL,
- its asset bucket uses the canonical taxonomy,
- its evidence status is explicit,
- its active status is explicit,
- and the row states why it matters to Post-Unicorn Finance.

An entity can appear in the public paper only after source text review confirms the claim.

## Paper Inclusion Bar

A company can appear in the main paper only when:

- the event claim is sourced,
- the capital/funding path claim is sourced if mentioned,
- the classification is clearly separated from the factual claim,
- and the row has a clear reason it helps prove the industry exists.

Unverified examples may appear in internal appendices only.
