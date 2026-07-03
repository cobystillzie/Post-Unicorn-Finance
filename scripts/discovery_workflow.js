export const meta = {
  name: 'atlas-discovery',
  description: 'Fan out niche curation agents to web-verify real non-unicorn capital allocators for the Post-Unicorn Finance atlas',
  phases: [{ title: 'Curate', detail: 'one web-verifying agent per niche' }],
}

// Round number controls niche emphasis so successive rounds dig deeper / new regions.
const round = (args && args.round) || 1

const FIRM_SCHEMA = {
  type: 'object',
  additionalProperties: false,
  properties: {
    firms: {
      type: 'array',
      items: {
        type: 'object',
        additionalProperties: false,
        properties: {
          name: { type: 'string', description: 'Official firm name as it appears on its own website' },
          website: { type: 'string', description: 'Official homepage URL, https' },
          asset_class: { type: 'string', enum: ['SMV', 'Patient Capital', 'LMV', 'Search/ETA', 'Portfolio Capital', 'Sovereign Capital'] },
          entity_type: { type: 'string', description: 'short role, e.g. permanent equity holdco, revenue-based lender, search fund investor' },
          evidence_quote: { type: 'string', description: 'EXACT verbatim words copied from the homepage (8-20 words)' },
          source_checked: { type: 'string', description: 'the URL you actually fetched to confirm' },
        },
        required: ['name', 'website', 'asset_class', 'entity_type', 'evidence_quote', 'source_checked'],
      },
    },
  },
  required: ['firms'],
}

const COMMON_RULES = `
You are sourcing REAL capital-allocator firms for a "Post-Unicorn Finance" industry atlas: firms that fund or acquire companies OUTSIDE the classic unicorn-venture-capital model.

THE ALLOCATOR TEST (mandatory): include a firm ONLY if it DEPLOYS ITS OWN (or its LPs') CAPITAL into companies via equity, debt, revenue-share, or acquisition. If it does not put its own money into companies, EXCLUDE it.
EXCLUDE (these pollute the atlas and the gate cannot catch them):
- marketplaces / brokers that match buyers & sellers for a fee (e.g. Acquire.com, Flippa, Microns — "businesses for sale", "asking price", "for buyers/for sellers")
- embedded-finance PRODUCTS / SaaS infrastructure that power financing for OTHER platforms (unless the firm itself is the principal lender deploying its own capital)
- industry networks / membership / standards bodies (e.g. The GIIN)
- pure advisories / consultancies / law or comms firms / nonprofits that only advise
- accelerators or competitions that take no equity and deploy NO capital
- media / news / blogs / articles / listicles / directories
- classic seed/Series-A unicorn VC, mega buyout PE (KKR, Blackstone, Carlyle), and ordinary tech corporations

ANTI-HALLUCINATION RULES — these are the entire point:
1. Include a firm ONLY if you confirm it is REAL by actually fetching its website. Use WebSearch to find it and WebFetch to load its homepage. If those tools are not loaded, first call ToolSearch with query "select:WebSearch,WebFetch", then use them.
2. For each firm provide its real official https homepage URL and an EXACT verbatim quote (8-20 words) copied from text actually on that homepage. Copy real words; never paraphrase or invent. If you cannot fetch the page and copy a real quote, DROP the firm.
3. Do NOT invent firms. A short list of confirmed-real firms is far better than a long list with any fabricated entries. Better to return 6 real firms than 15 with 2 invented.
4. We already have 550+ well-known firms. AVOID the obvious household names; dig into lesser-known but real, verifiable firms.
5. Prefer firms whose website actually uses the target vocabulary for the asset class (given below) — that is how they qualify.

Return ONLY the structured object. Aim for 10-15 verified-real firms.`

const ROUND2_NICHES = [
  { key: 'pc-holdco-intl', ac: 'Patient Capital', focus: `Permanent-equity / buy-and-hold-forever holding companies acquiring small businesses OUTSIDE the US: UK, Ireland, Germany, Nordics, France, Canada, Australia, India. Vocabulary: "permanent equity","buy and hold","hold forever","no forced exit","permanent home".` },
  { key: 'pc-eot-intl', ac: 'Patient Capital', focus: `Steward-ownership and employee-ownership-trust (EOT) acquirers/advisors in the UK and Europe specifically. Vocabulary: "employee ownership trust","steward-ownership","perpetual purpose","we never sell".` },
  { key: 'pc-faith-impact', ac: 'Patient Capital', focus: `Faith-driven and values-driven patient-capital funds and foundations making long-hold direct investments. Vocabulary: "faith-based","values-aligned","mission-driven","impact capital","philanthropic","benefit corporation".` },
  { key: 'smv-rbf-intl', ac: 'SMV', focus: `Revenue-based financing and non-dilutive lenders OUTSIDE the US: Europe, UK, India, LatAm, Africa, SE Asia. Vocabulary: "revenue-based","non-dilutive","recurring revenue","flexible capital","working capital".` },
  { key: 'smv-microcap-software', ac: 'SMV', focus: `Micro-PE and lower-middle-market buyers of small, profitable, capital-efficient B2B/vertical software. Vocabulary: "micro private equity","lower middle market","capital-efficient","bootstrapped","vertical software","software businesses".` },
  { key: 'lmv-solo-longtail', ac: 'LMV', focus: `The long tail of solo-GP / nano / rolling / micro VC funds (Fund I, emerging managers, scout funds) beyond the famous names. Vocabulary: "solo gp","nano fund","rolling fund","first checks","emerging manager","fund i","syndicate".` },
  { key: 'lmv-accelerator-intl', ac: 'LMV', focus: `Equity-free accelerators, fellowships, residencies and founder-grant programs worldwide (incl. non-US). Vocabulary: "equity-free","fellowship","founder grant","residency program","no equity","accelerator","incubator".` },
  { key: 'eta-sponsors-longtail', ac: 'Search/ETA', focus: `The long tail of independent sponsors and fundless sponsors acquiring lower-middle-market SMBs (owner succession). There are hundreds — dig deep. Vocabulary: "independent sponsor","fundless sponsor","owner-operator","succession","lower middle market","main street".` },
  { key: 'eta-search-intl', ac: 'Search/ETA', focus: `Search funds and ETA investors by REGION: Europe, UK, Iberia, LatAm, India, Africa, SE Asia, Middle East. Vocabulary: "search fund","entrepreneurship through acquisition","acquire a business","owner-led","succession".` },
  { key: 'pf-vms-longtail', ac: 'Portfolio Capital', focus: `The long tail of vertical-market-software serial acquirers and software holdcos (Constellation-style decentralized buy-and-hold), beyond the famous ones, including regional ones. Vocabulary: "serial acquirer","operating group","acquire and hold","vertical software","we never sell".` },
  { key: 'pf-microsaas-acq', ac: 'Portfolio Capital', focus: `Micro-SaaS and small-software acquirers / holdcos that buy-and-hold bootstrapped apps and SaaS (acquire.com ecosystem style). Vocabulary: "holdco","acquire and operate","buy and hold","operate forever","wholly-owned","portfolio companies".` },
  { key: 'pf-rollup-longtail', ac: 'Portfolio Capital', focus: `Buy-and-build / roll-up operating groups consolidating services, healthcare, trades, home-services or industrial SMBs to hold. Vocabulary: "roll-up","buy-and-build","consolidation","operating companies","platform acquisition".` },
  { key: 'sov-climate-catalytic2', ac: 'Sovereign Capital', focus: `Catalytic-capital, blended-finance and climate-finance funds and institutional impact investors (incl. DFIs and climate funds) worldwide. Vocabulary: "catalytic capital","blended finance","concessional capital","climate finance","development finance","impact investing".` },
  { key: 'sov-swf-regional', ac: 'Sovereign Capital', focus: `Smaller regional/national sovereign wealth funds, public investment banks and strategic state investors beyond GIC/Temasek/PIF/Norges (e.g. Gulf, Africa, Asia, Europe, LatAm). Vocabulary: "sovereign wealth","public investment","state-owned","strategic investment","national".` },
  { key: 'sov-pension-endow2', ac: 'Sovereign Capital', focus: `Public pension funds, superannuation funds and large university endowments acting as strategic long-term allocators. Vocabulary: "public investment","strategic investment","long-term","capital allocator","pension","endowment".` },
]

const ROUND1_NICHES = [
  // Patient Capital
  { key: 'pc-holdco-smallbiz', ac: 'Patient Capital', focus: `Permanent-equity / "buy and hold forever" holding companies acquiring SMALL businesses (Permanent Equity / HoldCo style). Vocabulary: "permanent equity","buy and hold","hold forever","no forced exit","permanent home","long-term".` },
  { key: 'pc-steward-eot', ac: 'Patient Capital', focus: `Steward-ownership and employee-ownership (EOT/ESOP) acquirers and trusts that buy companies to hold permanently. Vocabulary: "steward","steward-ownership","employee ownership","purpose trust","perpetual purpose","we never sell".` },
  { key: 'pc-family-evergreen', ac: 'Patient Capital', focus: `Family offices and evergreen vehicles doing DIRECT long-hold operating-company investments (not fund-of-funds). Vocabulary: "evergreen","family office","multi-generational","wealth preservation","long duration","patient capital".` },
  { key: 'pc-impact-foundation', ac: 'Patient Capital', focus: `Mission/impact/faith-driven patient-capital LLCs, foundations and endowments that make long-hold direct investments. Vocabulary: "mission-driven","impact capital","faith-based","values-aligned","philanthropic","benefit corporation".` },
  // SMV
  { key: 'smv-rbf', ac: 'SMV', focus: `Revenue-based financing and non-dilutive growth capital lenders for SaaS / e-commerce. Vocabulary: "revenue-based","non-dilutive","no equity dilution","recurring revenue","founder-friendly","flexible capital".` },
  { key: 'smv-growth-credit', ac: 'SMV', focus: `Growth credit / structured growth capital for PROFITABLE, capital-efficient software companies (not classic VC). Vocabulary: "growth debt","growth equity","capital-efficient","profitable growth","recurring revenue","mission-critical".` },
  { key: 'smv-lmm-software-pe', ac: 'SMV', focus: `Lower-middle-market private equity focused on B2B / vertical SOFTWARE with long holds. Vocabulary: "lower middle market","vertical software","B2B software","software businesses","tech-enabled","bootstrapped".` },
  // LMV
  { key: 'lmv-solo-nano', ac: 'LMV', focus: `Solo-GP / nano / micro VC funds run by a single operator-investor writing first checks. Vocabulary: "solo gp","nano fund","micro fund","first checks","emerging manager","operator-investor","rolling fund".` },
  { key: 'lmv-equityfree-fellowship', ac: 'LMV', focus: `Equity-free accelerators, founder fellowships, residencies and grant programs for early founders. Vocabulary: "equity-free","fellowship","founder grant","micro-grant","residency program","no equity","community of founders".` },
  // Search/ETA
  { key: 'eta-searchfund-us', ac: 'Search/ETA', focus: `Search-fund investors and ETA (entrepreneurship-through-acquisition) funds in the US. Vocabulary: "search fund","entrepreneurship through acquisition","ETA","acquire a business","first-time CEO","self-funded search".` },
  { key: 'eta-sponsors', ac: 'Search/ETA', focus: `Independent sponsors and fundless sponsors acquiring lower-middle-market SMBs (owner succession). Vocabulary: "independent sponsor","fundless sponsor","owner-operator","succession","buy and grow","lower middle market","main street".` },
  { key: 'eta-intl', ac: 'Search/ETA', focus: `Search funds and ETA investors OUTSIDE the US (Europe, UK, LatAm, India, Africa, Asia). Vocabulary: "search fund","entrepreneurship through acquisition","acquire a business","owner-led","succession".` },
  // Portfolio Capital
  { key: 'pf-vms-serial', ac: 'Portfolio Capital', focus: `Vertical-market-software serial acquirers / holdcos in the Constellation Software style (decentralized operating groups), beyond the famous ones. Vocabulary: "serial acquirer","operating group","acquire and hold","vertical software","portfolio companies","we never sell".` },
  { key: 'pf-saas-microholdco', ac: 'Portfolio Capital', focus: `Bootstrapped / micro-SaaS acquirers and small software holding companies that buy-and-hold. Vocabulary: "holdco","acquire and operate","buy and hold","operate forever","wholly-owned","subsidiaries".` },
  { key: 'pf-rollup-services', ac: 'Portfolio Capital', focus: `Buy-and-build / roll-up operating groups consolidating services, healthcare, trades, or industrial SMBs to hold long-term. Vocabulary: "roll-up","buy-and-build","consolidation","operating companies","platform acquisition","acquire and operate".` },
  { key: 'pf-studio', ac: 'Portfolio Capital', focus: `Venture studios / startup studios / company builders that create and hold operating companies. Vocabulary: "venture studio","startup studio","venture builder","company creation","studio equity","portfolio companies".` },
  // Sovereign Capital
  { key: 'sov-swf-dfi', ac: 'Sovereign Capital', focus: `Sovereign wealth funds, public investment banks and development finance institutions, beyond the obvious (GIC/Temasek/PIF). Smaller national/regional ones globally. Vocabulary: "sovereign wealth","public investment","development finance","state-owned","strategic capital","national".` },
  { key: 'sov-climate-catalytic', ac: 'Sovereign Capital', focus: `Impact/climate institutional investors, catalytic-capital and blended-finance funds, and climate-finance networks. Vocabulary: "catalytic capital","blended finance","concessional capital","climate finance","development finance","impact investing".` },
  { key: 'sov-pension-endow', ac: 'Sovereign Capital', focus: `Public pension funds and large endowments that act as strategic long-term capital allocators (with a public/strategic mandate). Vocabulary: "public investment","strategic investment","long-term","capital allocator","national","strategic mandate".` },
]

const ROUND3_NICHES = [
  // LMV-heavy (thinnest class) — fresh long tail
  { key: 'l3-microvc-vertical', ac: 'LMV', focus: `Thesis/vertical-focused micro & nano VC funds (climate, fintech, health, dev tools, AI-native) run by 1-2 GPs writing first checks. Vocabulary: "micro fund","nano fund","solo gp","first checks","thesis-driven","emerging manager".` },
  { key: 'l3-syndicate-rolling', ac: 'LMV', focus: `Angel syndicates, rolling funds, scout programs and small operator-led vehicles (AngelList-era). Vocabulary: "syndicate","rolling fund","scout fund","operator-investor","first checks","writing first checks".` },
  { key: 'l3-microvc-region', ac: 'LMV', focus: `Emerging-manager / micro VC funds by REGION (Europe, LatAm, Africa, India, SE Asia, MENA, CEE) beyond the famous ones. Vocabulary: "micro fund","emerging manager","fund i","first checks","pre-seed","operator".` },
  { key: 'l3-accelerator-vertical', ac: 'LMV', focus: `Vertical & mission accelerators, fellowships and equity-free founder programs (climate, biotech, fintech, social impact, underrepresented founders). Vocabulary: "accelerator","fellowship","equity-free","founder grant","residency program","cohort".` },
  // Patient Capital verticals
  { key: 'l3-vertical-holdco', ac: 'Patient Capital', focus: `Permanent holdcos focused on a specific vertical they buy-and-hold: home services/HVAC/plumbing, dental/vet, healthcare services, manufacturing, e-commerce brands. Vocabulary: "permanent","buy and hold","hold forever","no intention of selling","operate","permanent home".` },
  { key: 'l3-family-holding-intl', ac: 'Patient Capital', focus: `Long-term family-controlled holding companies / industrial Mittelstand-style groups worldwide (Europe, Asia, LatAm) that hold for generations. Vocabulary: "family-owned","generations","evergreen","long-term","permanent capital","family business".` },
  // SMV verticals
  { key: 'l3-ecom-creator-finance', ac: 'SMV', focus: `Non-dilutive financing for e-commerce brands, marketplace sellers, creators and subscription businesses. Vocabulary: "non-dilutive","revenue-based","recurring revenue","working capital","flexible capital","merchant financing".` },
  { key: 'l3-vertical-growth', ac: 'SMV', focus: `Growth/structured-capital firms for capital-efficient vertical software & tech-enabled services (healthcare IT, fintech, govtech, industrial). Vocabulary: "growth equity","growth debt","capital-efficient","recurring revenue","lower middle market","vertical software".` },
  // Search/ETA fresh regions + communities
  { key: 'l3-eta-region2', ac: 'Search/ETA', focus: `Search funds & ETA investors in Canada, Australia/NZ, Nordics, Benelux, Italy, Brazil, Mexico, Japan. Vocabulary: "search fund","entrepreneurship through acquisition","acquire a business","owner-led","succession".` },
  { key: 'l3-eta-community', ac: 'Search/ETA', focus: `ETA/search-fund communities, accelerators and funds for women-led, veteran-led and diverse searchers, plus self-funded-search resources that also invest. Vocabulary: "search fund","self-funded search","entrepreneurship through acquisition","first-time ceo","acquire a business".` },
  // Portfolio Capital fresh
  { key: 'l3-studio-region', ac: 'Portfolio Capital', focus: `Venture studios / company builders by region & vertical (Europe, MENA, Asia, LatAm; fintech, climate, health studios). Vocabulary: "venture studio","startup studio","venture builder","company creation","studio equity","co-found".` },
  { key: 'l3-vms-region', ac: 'Portfolio Capital', focus: `Regional vertical-market-software acquirers & software holdcos (Nordics, DACH, France, UK, Canada, India, Brazil, Australia) that buy and hold. Vocabulary: "serial acquirer","operating group","acquire and hold","vertical software","portfolio companies","we never sell".` },
  // Sovereign fresh
  { key: 'l3-dfi-bilateral', ac: 'Sovereign Capital', focus: `Bilateral development finance institutions and regional development banks not commonly listed (e.g. FMO, Proparco, CDC/BII, DEG, Swedfund, Finnfund, FinDev Canada, BIO, SIFEM, regional dev banks). Vocabulary: "development finance","blended finance","impact","sovereign","public investment","catalytic capital".` },
  { key: 'l3-impact-asset-mgr', ac: 'Sovereign Capital', focus: `Mission/impact-focused institutional asset managers and large foundations with a strategic public-good investment mandate (distinct from family offices). Vocabulary: "impact investing","catalytic capital","blended finance","public good","sustainable development","strategic capital".` },
]

const NICHES = round >= 3 ? ROUND3_NICHES : round >= 2 ? ROUND2_NICHES : ROUND1_NICHES

phase('Curate')
const results = await parallel(
  NICHES.map((n) => () =>
    agent(`${COMMON_RULES}\n\nTHIS AGENT'S NICHE: ${n.focus}\nReturn asset_class = "${n.ac}" for every firm.`, {
      label: `curate:${n.key}`,
      phase: 'Curate',
      schema: FIRM_SCHEMA,
    }).then((r) => (r && r.firms ? r.firms : []))
  )
)

// Flatten + dedupe by normalized name and by domain (cross-agent only; inject step dedupes vs existing atlas).
function norm(s) { return (s || '').toLowerCase().replace(/[^a-z0-9]+/g, '') }
function dom(u) {
  try {
    let h = (u || '').replace(/^https?:\/\//, '').split('/')[0].toLowerCase()
    if (h.indexOf('www.') === 0) h = h.slice(4)
    return h.split(':')[0]
  } catch (e) { return '' }
}
const seenName = new Set(), seenDom = new Set(), out = []
for (const firm of results.flat().filter(Boolean)) {
  if (!firm.name || !firm.website) continue
  const n = norm(firm.name), d = dom(firm.website)
  if (!n || seenName.has(n) || (d && seenDom.has(d))) continue
  seenName.add(n); if (d) seenDom.add(d)
  out.push(firm)
}
log(`Curated ${out.length} unique candidate firms across ${NICHES.length} niches`)
return { count: out.length, firms: out }
