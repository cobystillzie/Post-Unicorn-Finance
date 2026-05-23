"""Seed the Post-Unicorn Finance industry atlas.

The atlas is intentionally entity-first: firms, funds, platforms, acquirers,
studios, communities, and instrument providers come before company proof cases.
Rows marked candidate_evidence are discovery leads, not publication-ready facts.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data" / "evidence"

TODAY = "2026-05-22"


def slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return normalized or "entity"


ASSET_CLASSES = [
    {
        "asset_class": "UVC",
        "classification_status": "asset_class",
        "definition": "Traditional venture capital optimized for power-law returns and billion-dollar-plus outcomes.",
        "return_model": "Equity upside from a small number of fund-returning winners.",
        "capital_source": "VC funds, institutional LPs, angels, corporate venture, growth funds.",
        "risk_type": "Company failure, market timing, follow-on financing, power-law concentration.",
        "liquidity_path": "IPO, mega-acquisition, secondary sales, fund distributions.",
        "company_stage": "Pre-seed through growth.",
        "founder_profile": "Hypergrowth founders pursuing large TAMs and venture-scale outcomes.",
        "industry_standard_signals": "Large TAM, rapid growth, repeated rounds, high ownership/dilution tolerance.",
        "notes": "Included as the baseline comparison, not as the enemy.",
    },
    {
        "asset_class": "SMV",
        "classification_status": "emerging_asset_class_candidate",
        "definition": "Strategic Middle Ventures: tech-enabled companies with strategic acquisition, profitable-growth, or middle-outcome logic.",
        "return_model": "Middle-market acquisition, cash-flow growth, strategic buyer value, or targeted portfolio compounding.",
        "capital_source": "Acquisition-first venture funds, micro-PE, SaaS acquirers, studios, family offices, strategic investors.",
        "risk_type": "Strategic buyer fit, integration value, market concentration, durability of niche workflow ownership.",
        "liquidity_path": "Strategic acquisition, PE/platform acquisition, dividend/earnings yield, secondary transactions.",
        "company_stage": "Seed through mature private company.",
        "founder_profile": "Builders of real tech-enabled businesses that may not need or fit unicorn math.",
        "industry_standard_signals": "Vertical depth, customer density, proprietary workflows, capital efficiency, acquisition fit.",
        "notes": "Primary first-wave research lane.",
    },
    {
        "asset_class": "Patient Capital",
        "classification_status": "asset_class_or_capital_strategy",
        "definition": "Long-duration capital for companies designed to compound without a forced sale.",
        "return_model": "Dividends, royalties, profit share, cash yield, permanent equity appreciation.",
        "capital_source": "Evergreen funds, family offices, foundations, permanent capital vehicles, impact investors.",
        "risk_type": "Lower liquidity, slower growth, governance alignment, operating durability.",
        "liquidity_path": "Distributions, buybacks, long-duration holds, optional acquisition.",
        "company_stage": "Revenue to mature private companies.",
        "founder_profile": "Founders who value control, durability, profitability, and lower exit pressure.",
        "industry_standard_signals": "No forced exit, cash-flow orientation, founder-friendly structures.",
        "notes": "Can overlap with SMV and Portfolio Capital.",
    },
    {
        "asset_class": "LMV",
        "classification_status": "emerging_asset_class_candidate",
        "definition": "Leveraged Micro Ventures: tiny AI/software-enabled teams creating outsized value with low capital needs.",
        "return_model": "High revenue per employee, small exits, cash yield, small checks with high MOIC potential.",
        "capital_source": "Indie funds, angels, accelerators, micro funds, grants, founder revenue.",
        "risk_type": "Key-person risk, distribution risk, defensibility, platform dependency.",
        "liquidity_path": "Small acquisition, profit distributions, founder buyback, revenue share.",
        "company_stage": "Idea through profitable micro-company.",
        "founder_profile": "Solo founders and tiny teams using automation, AI, and distribution leverage.",
        "industry_standard_signals": "1-10 person teams, low burn, automation-heavy, revenue early.",
        "notes": "Needs especially careful definition because evidence is emerging.",
    },
    {
        "asset_class": "Sovereign Capital",
        "classification_status": "source_of_capital_class",
        "definition": "Innovation capital deployed for national, regional, or strategic-interest reasons.",
        "return_model": "Financial return plus strategic, national, regional, security, or industrial-policy outcomes.",
        "capital_source": "Sovereign wealth funds, government-backed funds, national development agencies.",
        "risk_type": "Policy shift, geopolitical risk, mandate complexity, long-duration technology risk.",
        "liquidity_path": "Strategic exits, public listings, fund distributions, national strategic value.",
        "company_stage": "Seed through infrastructure-scale growth.",
        "founder_profile": "Founders in strategic sectors or regions aligned with national priorities.",
        "industry_standard_signals": "AI, defense, energy, semiconductors, climate, biotech, infrastructure, food security.",
        "notes": "A capital-source class, not always a standalone company asset class.",
    },
    {
        "asset_class": "Search/ETA",
        "classification_status": "adjacent_asset_class",
        "definition": "Entrepreneurship through acquisition: buying and operating an existing business.",
        "return_model": "Equity value creation through acquisition, debt paydown, operational improvement, and exit or hold.",
        "capital_source": "Search fund investors, acquisition debt, SBA-like debt, family offices, private investors.",
        "risk_type": "Operator execution, acquisition quality, debt service, succession, concentration.",
        "liquidity_path": "Resale, dividends, recapitalization, long hold.",
        "company_stage": "Existing profitable companies.",
        "founder_profile": "Operators/searchers who acquire rather than start from zero.",
        "industry_standard_signals": "Search capital, acquisition entrepreneurship, operator-led ownership.",
        "notes": "Distinct from VC and traditional PE because the operator is central.",
    },
    {
        "asset_class": "Camel Modifier",
        "classification_status": "modifier",
        "definition": "Capital-efficient, resilient, profitability-oriented operating philosophy.",
        "return_model": "Depends on the underlying asset class; reduces financing dependence and burn risk.",
        "capital_source": "Any source; usually fewer rounds, customer revenue, or small external capital.",
        "risk_type": "Growth constraints, slower scaling, less winner-take-most upside.",
        "liquidity_path": "Applies across acquisition, hold, profitability, and VC paths.",
        "company_stage": "Any stage.",
        "founder_profile": "Resilient founders prioritizing survival and sustainability before scale.",
        "industry_standard_signals": "Lower burn, faster path to profitability, fewer rounds.",
        "notes": "Not a standalone asset class unless a distinct vehicle model is proven.",
    },
    {
        "asset_class": "Portfolio Capital",
        "classification_status": "operating_model",
        "definition": "Studios, foundries, holding companies, or repeatable company-creation/acquisition platforms.",
        "return_model": "Portfolio-level equity, acquisition compounding, shared infrastructure leverage.",
        "capital_source": "Studio funds, holding companies, PE, family offices, venture funds, corporate partners.",
        "risk_type": "Platform execution, shared-services quality, portfolio concentration, talent allocation.",
        "liquidity_path": "Portfolio exits, fund distributions, dividends, public holding company value.",
        "company_stage": "Idea through mature acquisition portfolios.",
        "founder_profile": "Founders/operators who benefit from shared infrastructure or platform company creation.",
        "industry_standard_signals": "Repeatable creation/acquisition, shared operators, studio infrastructure.",
        "notes": "Becomes an asset-class candidate only when investors underwrite the platform itself.",
    },
    {
        "asset_class": "Instrument",
        "classification_status": "instrument_family",
        "definition": "Financing structures used across asset classes, including revenue share, royalties, capped returns, and milestone tranches.",
        "return_model": "Contractual repayment, yield, cap, royalty, revenue share, or milestone-triggered economics.",
        "capital_source": "Capital providers, lenders, funds, platforms, family offices, strategic financiers.",
        "risk_type": "Revenue volatility, underwriting quality, covenant structure, repayment misalignment.",
        "liquidity_path": "Repayment, yield, capped return, conversion, or contractual buyout.",
        "company_stage": "Revenue-stage companies primarily, but varies by instrument.",
        "founder_profile": "Founders seeking capital without classic VC ownership or exit pressure.",
        "industry_standard_signals": "Non-dilutive, revenue-linked, capped, staged, royalty-based, or profit-linked terms.",
        "notes": "Track instrument plus provider; instrument alone is not a firm.",
    },
]


ENTITIES = [
    # Revenue-based / non-dilutive / instrument providers
    ("TinySeed", "SMV", "Instrument;LMV", "accelerator/fund", "https://tinyseed.com/", "active", "United States", "B2B SaaS", "revenue-based / bootstrapped SaaS capital", "revenue_share", "B2B SaaS founders seeking growth without classic VC pressure", "accelerator and capital provider", 93, "TinySeed is a candidate industry entity for bootstrapped SaaS and revenue-linked startup capital."),
    ("Calm Company Fund", "Patient Capital", "Instrument;Camel Modifier", "capital provider", "https://calmfund.com/", "active", "United States", "calm companies / SaaS", "shared earnings / founder-friendly capital", "shared_earnings", "founders building durable companies without hypergrowth pressure", "capital provider and instrument pioneer", 91, "Calm Company Fund is a candidate entity for shared earnings and patient capital structures."),
    ("Earnest Capital", "Patient Capital", "Instrument;Camel Modifier", "historical fund", "https://earnestcapital.com/", "historical", "United States", "bootstrapped software", "shared earnings agreement", "shared_earnings", "bootstrapped founders seeking aligned capital", "historical capital experiment", 82, "Earnest Capital is retained as a historical lineage source for shared earnings and calm-company capital."),
    ("Indie.vc", "Patient Capital", "Instrument;Camel Modifier", "historical fund", "https://www.indie.vc/", "inactive", "United States", "independent startups", "alternative VC / revenue-linked experimentation", "revenue_share;capped_return", "founders pursuing profitability and optionality", "historical capital experiment", 82, "Indie.vc is retained as a historical experiment in alternatives to classic VC."),
    ("Lighter Capital", "SMV", "Instrument", "capital provider", "https://www.lightercapital.com/", "active", "United States", "SaaS / tech", "revenue-based financing", "revenue_based_financing", "revenue-stage technology companies", "capital provider", 88, "Lighter Capital is a candidate revenue-based financing provider for the industry atlas."),
    ("Capchase", "SMV", "Instrument", "capital platform", "https://www.capchase.com/", "active", "United States / Europe", "B2B SaaS", "non-dilutive SaaS financing / payment terms", "contract_financing;non_dilutive_capital", "B2B SaaS companies with recurring revenue", "capital platform", 86, "Capchase is a candidate non-dilutive capital platform for SaaS companies."),
    ("Founderpath", "SMV", "Instrument", "capital provider", "https://founderpath.com/", "active", "United States", "B2B SaaS", "non-dilutive SaaS capital", "non_dilutive_capital", "bootstrapped and revenue-stage SaaS founders", "capital provider", 87, "Founderpath is a candidate capital provider for recurring-revenue software companies."),
    ("Pipe", "SMV", "Instrument", "capital platform", "https://pipe.com/", "active", "United States", "recurring revenue businesses", "embedded capital / revenue financing", "revenue_based_financing", "companies with predictable revenue", "capital platform", 82, "Pipe is a candidate capital platform for revenue-based and embedded capital workflows."),
    ("Clearco", "SMV", "Instrument", "capital provider", "https://clear.co/", "active", "Canada / United States", "ecommerce / recurring revenue", "non-dilutive growth capital", "revenue_based_financing", "ecommerce and digital businesses", "capital provider", 82, "Clearco is a candidate non-dilutive capital provider for digital businesses."),
    ("Wayflyer", "SMV", "Instrument", "capital provider", "https://wayflyer.com/", "active", "Ireland / Global", "ecommerce / consumer brands", "revenue-based and inventory financing", "revenue_based_financing;inventory_financing", "consumer and ecommerce companies", "capital provider", 81, "Wayflyer is a candidate revenue-based financing provider for commerce businesses."),
    ("Uncapped", "SMV", "Instrument", "capital provider", "https://www.weareuncapped.com/", "active", "United Kingdom / Europe", "digital businesses", "non-dilutive growth capital", "revenue_based_financing", "online and recurring-revenue companies", "capital provider", 79, "Uncapped is a candidate non-dilutive financing provider."),
    ("Outfund", "SMV", "Instrument", "capital provider", "https://www.out.fund/", "active", "United Kingdom", "online businesses", "revenue-based financing", "revenue_based_financing", "online and ecommerce companies", "capital provider", 76, "Outfund is a candidate revenue-based financing provider."),
    ("Decathlon Capital Partners", "SMV", "Instrument", "capital provider", "https://decathloncapital.com/", "active", "United States", "growth companies", "revenue-based financing", "revenue_based_financing", "revenue-stage companies", "capital provider", 80, "Decathlon Capital is a candidate revenue-based financing provider."),
    ("SaaS Capital", "SMV", "Instrument", "capital provider", "https://www.saas-capital.com/", "active", "United States", "B2B SaaS", "growth debt for SaaS", "growth_debt", "B2B SaaS companies", "capital provider", 80, "SaaS Capital is a candidate SaaS debt and non-dilutive capital provider."),
    ("Novel Capital", "SMV", "Instrument", "capital provider", "https://www.novelcapital.com/", "active", "United States", "B2B software", "revenue-based and non-dilutive capital", "revenue_based_financing", "B2B software and recurring revenue companies", "capital provider", 79, "Novel Capital is a candidate non-dilutive capital provider."),
    ("Bigfoot Capital", "SMV", "Instrument", "capital provider", "https://bigfootcap.com/", "active", "United States", "B2B SaaS", "growth debt / revenue-based capital", "growth_debt", "SaaS and recurring-revenue companies", "capital provider", 76, "Bigfoot Capital is a candidate growth debt provider for software companies."),
    ("Espresso Capital", "SMV", "Instrument", "capital provider", "https://www.espressocapital.com/", "active", "Canada / United States", "technology companies", "venture debt / growth capital", "venture_debt", "technology and SaaS companies", "capital provider", 75, "Espresso Capital is a candidate venture debt and growth capital provider."),
    ("TIMIA Capital", "SMV", "Instrument", "capital provider", "https://timiacapital.com/", "active", "Canada", "SaaS", "revenue-based financing", "revenue_based_financing", "software companies with recurring revenue", "capital provider", 76, "TIMIA Capital is a candidate revenue-based financing provider."),
    ("Flow Capital", "SMV", "Instrument", "capital provider", "https://flowcap.com/", "active", "Canada / United States", "technology companies", "revenue-linked growth capital", "revenue_based_financing;venture_debt", "growth-stage technology companies", "capital provider", 75, "Flow Capital is a candidate revenue-linked growth capital provider."),
    ("Corl", "SMV", "Instrument", "capital provider", "https://corl.io/", "active", "Canada", "digital businesses", "revenue-based financing", "revenue_based_financing", "digital and recurring-revenue companies", "capital provider", 72, "Corl is a candidate revenue-based financing provider."),
    ("Braavo Capital", "LMV", "Instrument", "capital provider", "https://www.getbraavo.com/", "active", "United States", "mobile apps / games", "non-dilutive app financing", "non_dilutive_capital", "mobile app and game businesses", "capital provider", 74, "Braavo is a candidate non-dilutive capital provider for app businesses."),
    ("Vitt", "SMV", "Instrument", "capital provider", "https://www.vitt.com/", "active", "United Kingdom", "recurring revenue companies", "non-dilutive financing", "non_dilutive_capital", "SaaS and recurring-revenue companies", "capital provider", 70, "Vitt is a candidate recurring-revenue financing provider."),
    ("Levenue", "SMV", "Instrument", "capital marketplace", "https://www.levenue.com/", "active", "Europe", "recurring revenue companies", "revenue-based financing marketplace", "revenue_based_financing", "recurring-revenue companies", "capital marketplace", 73, "Levenue is a candidate marketplace for recurring-revenue financing."),
    ("Arc", "SMV", "Instrument", "capital platform", "https://www.arc.tech/", "active", "United States", "software startups", "startup banking and non-dilutive capital", "non_dilutive_capital", "software startups and recurring revenue businesses", "capital platform", 74, "Arc is a candidate capital and banking platform for startups."),
    ("Stripe Capital", "SMV", "Instrument", "embedded capital provider", "https://stripe.com/capital", "active", "Global", "Stripe merchants", "embedded merchant financing", "embedded_finance", "businesses processing payments through Stripe", "embedded capital provider", 70, "Stripe Capital is a candidate embedded-finance provider."),
    ("Shopify Capital", "SMV", "Instrument", "embedded capital provider", "https://www.shopify.com/capital", "active", "Global", "commerce", "merchant cash advances / loans", "embedded_finance", "Shopify merchants", "embedded capital provider", 70, "Shopify Capital is a candidate embedded capital provider for commerce businesses."),
    ("PayPal Working Capital", "SMV", "Instrument", "embedded capital provider", "https://www.paypal.com/us/business/financial-services/working-capital", "active", "Global", "small businesses", "working capital", "embedded_finance", "businesses using PayPal", "embedded capital provider", 68, "PayPal Working Capital is a candidate embedded small-business financing provider."),
    ("YouLend", "SMV", "Instrument", "embedded finance provider", "https://www.youlend.com/", "active", "United Kingdom / Global", "platform businesses", "embedded revenue-based finance", "embedded_finance", "platforms and merchants", "embedded capital provider", 72, "YouLend is a candidate embedded finance provider."),
    ("Liberis", "SMV", "Instrument", "embedded finance provider", "https://www.liberis.com/", "active", "United Kingdom / Global", "small businesses", "embedded business finance", "embedded_finance", "small businesses and platforms", "embedded capital provider", 70, "Liberis is a candidate embedded finance provider."),
    ("Parafin", "SMV", "Instrument", "embedded finance provider", "https://www.parafin.com/", "active", "United States", "platform businesses", "embedded capital", "embedded_finance", "platforms and merchants", "embedded capital provider", 70, "Parafin is a candidate embedded capital provider."),
    ("GetVantage", "SMV", "Instrument", "capital provider", "https://www.getvantage.co/", "active", "India", "digital businesses", "revenue-based financing", "revenue_based_financing", "digital businesses in India and emerging markets", "capital provider", 76, "GetVantage is a candidate revenue-based financing provider."),
    ("Velocity", "SMV", "Instrument", "capital provider", "https://velocity.in/", "active", "India", "digital businesses", "revenue-based financing", "revenue_based_financing", "Indian ecommerce and digital businesses", "capital provider", 74, "Velocity is a candidate revenue-based financing provider."),
    ("Klub", "SMV", "Instrument", "capital provider", "https://klubworks.com/", "active", "India", "consumer and digital businesses", "revenue-based financing", "revenue_based_financing", "Indian brands and digital businesses", "capital provider", 74, "Klub is a candidate revenue-based financing provider."),
    ("Recur Club", "SMV", "Instrument", "capital marketplace", "https://www.recurclub.com/", "active", "India", "recurring revenue businesses", "revenue financing marketplace", "revenue_based_financing", "subscription and recurring-revenue businesses", "capital marketplace", 73, "Recur Club is a candidate recurring-revenue financing marketplace."),
    # SMV acquirers / middle-market venture / software holding companies
    ("SV8", "SMV", "Instrument", "fund/syndicate", "https://sv8.vc/", "active", "United States", "early-stage startups", "acquisition-first venture", "equity;strategic_acquisition", "startups designed with M&A pathways in mind", "SMV capital provider", 92, "SV8 is a candidate acquisition-first venture entity for the SMV lane."),
    ("Tangle Ventures", "SMV", "Patient Capital;Portfolio Capital", "venture studio/acquirer", "https://tangleventures.io/", "active", "United States", "profitable digital businesses", "acquire and compound overlooked businesses", "permanent_equity", "profitable overlooked digital businesses", "SMV acquirer and operator", 90, "Tangle is a candidate overlooked-company acquisition and patient-capital platform."),
    ("DWP Capital", "SMV", "Patient Capital;Portfolio Capital", "growth equity firm", "https://dwpcapital.com/", "active", "United States", "vertical software / tech-enabled services", "early-stage growth equity with flexible hold periods", "growth_equity;patient_capital", "capital-efficient vertical software and tech-enabled services companies", "SMV capital provider", 88, "DWP Capital is a candidate SMV capital provider focused on capital-efficient vertical software and tech-enabled services."),
    ("Union Group Fund", "SMV", "Patient Capital;Camel Modifier", "development and investment firm", "https://www.uniongroupfund.com/", "active", "United States", "vertical SaaS", "development and growth partnerships for small bootstrapped vertical SaaS", "growth_equity;patient_capital", "small bootstrapped vertical SaaS companies and solopreneurs", "SMV capital provider", 87, "Union Group Fund is a candidate SMV entity for small bootstrapped vertical SaaS partnerships."),
    ("TVC Capital", "SMV", "Portfolio Capital", "software growth equity firm", "https://tvccapital.com/fund-focus/", "active", "United States", "B2B software", "software growth equity for capital-efficient companies", "growth_equity;recapitalization", "B2B software companies between classic VC and large growth equity focus", "SMV growth equity provider", 86, "TVC Capital is a candidate SMV entity for capital-efficient B2B software growth equity."),
    ("D2 Fund", "SMV", "Patient Capital;Camel Modifier", "venture fund", "https://www.d2.fund/", "active", "United Kingdom / Europe", "B2B software", "capital for efficient software businesses", "equity;secondary;debt_support", "capital-efficient B2B software businesses in the UK and Europe", "SMV capital provider", 84, "D2 Fund is a candidate SMV entity for capital-efficient software businesses."),
    ("SeedTwo Capital", "SMV", "LMV;Portfolio Capital", "growth fund", "https://www.seedtwo.com/", "active", "United States", "vertical SaaS / AI", "funding for vertical SaaS and AI companies between seed and Series A", "growth_equity;equity", "founder-led vertical SaaS and AI companies with traction", "SMV capital provider", 82, "SeedTwo Capital is a candidate SMV entity for capital-efficient vertical SaaS and AI companies."),
    ("Sequel Capital", "SMV", "Portfolio Capital", "growth equity investor", "https://www.sequel-capital.com/", "active", "United Kingdom / Europe", "agentic B2B SaaS", "exit-focused growth equity for bootstrapped capital-efficient B2B SaaS", "growth_equity;strategic_exit", "bootstrapped and capital-efficient B2B SaaS companies with clear exit paths", "SMV capital provider", 84, "Sequel Capital is a candidate SMV entity for exit-focused capital-efficient B2B SaaS."),
    ("Mainsail Partners", "SMV", "Portfolio Capital", "growth equity firm", "https://mainsailpartners.com/", "active", "United States", "B2B software / AI-enabled software", "growth equity for bootstrapped B2B software companies", "growth_equity;founder_liquidity", "founder-led bootstrapped B2B software companies", "SMV growth equity provider", 86, "Mainsail Partners is a candidate SMV entity for growth equity serving bootstrapped B2B software companies."),
    ("Serent Capital", "SMV", "Portfolio Capital", "growth equity firm", "https://serentcapital.com/why-serent/", "active", "United States", "B2B software", "growth equity and operating support for founder-led bootstrapped software", "growth_equity;operating_support", "founder-led and bootstrapped B2B software companies", "SMV growth equity provider", 86, "Serent Capital is a candidate SMV entity for founder-led and bootstrapped B2B software growth equity."),
    ("Mamba Growth", "SMV", "Portfolio Capital", "growth equity firm", "https://www.mambagrowth.com/investment-criteria/", "active", "United States", "B2B software / technology", "minority growth equity for capital-efficient founder-led software companies", "growth_equity;minority_equity", "bootstrapped or lightly capitalized B2B technology companies", "SMV growth equity provider", 83, "Mamba Growth is a candidate SMV entity for capital-efficient founder-led software growth equity."),
    ("Five Elms Capital", "SMV", "Portfolio Capital", "software growth equity firm", "https://www.fiveelms.com/", "active", "United States / Global", "B2B software", "growth capital and founder liquidity for founder-owned software businesses", "growth_equity;founder_liquidity", "founder-owned B2B software companies", "SMV growth equity provider", 84, "Five Elms Capital is a candidate SMV entity for founder-owned software growth equity."),
    ("Elsewhere Partners", "SMV", "Portfolio Capital", "lower middle-market software investor", "https://elsewhere.partners/", "active", "United States / Global", "B2B software", "lower middle-market software private equity for bootstrapped or lightly capitalized companies", "growth_equity;majority_recap", "bootstrapped or lightly capitalized software companies outside traditional capital hubs", "SMV software investor", 85, "Elsewhere Partners is a candidate SMV entity for lower-middle-market software capital."),
    ("Sunstone Partners", "SMV", "Portfolio Capital", "growth private equity firm", "https://sunstonepartners.com/", "active", "United States", "software / tech-enabled services", "majority and minority investments in capital-efficient technology companies", "growth_equity;majority_equity;minority_equity", "technology-enabled services and software businesses with capital-efficient histories", "SMV growth equity provider", 82, "Sunstone Partners is a candidate SMV entity for capital-efficient software and tech-enabled services growth capital."),
    ("Expedition Growth Capital", "SMV", "Portfolio Capital", "software growth equity firm", "https://expedition.capital/", "active", "United Kingdom / Europe", "software", "growth equity for ambitious bootstrapped software companies", "growth_equity", "bootstrapped software companies seeking growth capital", "SMV growth equity provider", 82, "Expedition Growth Capital is a candidate SMV entity for bootstrapped software growth equity."),
    ("Silversmith Capital Partners", "SMV", "Portfolio Capital", "growth equity firm", "https://www.silversmith.com/", "active", "United States", "technology and healthcare", "growth equity for profitable founder-led companies", "growth_equity", "profitable founder-led technology and healthcare companies", "SMV growth equity provider", 82, "Silversmith Capital Partners is a candidate SMV entity for profitable founder-led growth equity."),
    ("Level Equity", "SMV", "Portfolio Capital", "growth equity firm", "https://www.levelequity.com/", "active", "United States", "software / technology-enabled businesses", "lower middle-market growth equity for capital-efficient technology businesses", "growth_equity", "capital-efficient software and technology-enabled businesses", "SMV growth equity provider", 81, "Level Equity is a candidate SMV entity for capital-efficient software and technology-enabled growth equity."),
    ("SureSwift Capital", "Portfolio Capital", "SMV;Patient Capital", "SaaS holding company", "https://www.sureswiftcapital.com/", "active", "Canada / United States", "bootstrapped SaaS", "acquire and operate SaaS businesses", "acquisition_capital", "bootstrapped SaaS founders seeking exits", "SaaS acquirer", 88, "SureSwift is a candidate SaaS acquisition holding company."),
    ("Tiny", "Portfolio Capital", "SMV;Patient Capital", "holding company", "https://www.tiny.com/", "active", "Canada / Global", "internet businesses", "holding company acquisition and operation", "permanent_equity", "internet business founders and sellers", "holding company", 86, "Tiny is a candidate internet-business holding company in the atlas."),
    ("Constellation Software", "Portfolio Capital", "SMV;Patient Capital", "software holding company", "https://www.csisoftware.com/", "active", "Canada / Global", "vertical market software", "acquire and hold vertical market software", "permanent_equity;acquisition_capital", "vertical market software companies", "software acquirer", 93, "Constellation Software is a candidate anchor institution for software acquisition compounding."),
    ("Volaris Group", "Portfolio Capital", "SMV", "software acquirer", "https://www.volarisgroup.com/", "active", "Global", "vertical market software", "acquire and strengthen software businesses", "acquisition_capital", "software companies in vertical markets", "software acquirer", 91, "Volaris is a candidate software acquirer and operating group."),
    ("Valsoft", "Portfolio Capital", "SMV;Patient Capital", "software holding company", "https://www.valsoftcorp.com/", "active", "Canada / Global", "vertical software", "buy and hold software businesses", "permanent_equity", "vertical software companies", "software acquirer", 90, "Valsoft is a candidate buy-and-hold software acquirer."),
    ("Banyan Software", "Portfolio Capital", "SMV;Patient Capital", "software holding company", "https://www.banyansoftware.com/", "active", "United States", "enterprise software", "permanent home for software businesses", "permanent_equity", "software founders seeking long-term home", "software acquirer", 90, "Banyan Software is a candidate permanent-capital software acquirer."),
    ("saas.group", "Portfolio Capital", "SMV", "SaaS holding company", "https://saas.group/", "active", "Germany / Global", "SaaS", "acquire and grow SaaS companies", "acquisition_capital", "SaaS founders seeking exits", "SaaS acquirer", 86, "saas.group is a candidate SaaS acquisition platform."),
    ("Everfield", "Portfolio Capital", "SMV", "software acquirer", "https://everfield.com/", "active", "Europe", "B2B software", "acquire and grow B2B software companies", "acquisition_capital", "European B2B software companies", "software acquirer", 85, "Everfield is a candidate European B2B software acquirer."),
    ("Lumine Group", "Portfolio Capital", "SMV", "software holding company", "https://www.luminegroup.com/", "active", "Global", "communications and media software", "buy and hold vertical software businesses", "permanent_equity", "communications and media software companies", "software acquirer", 86, "Lumine Group is a candidate vertical software holding company."),
    ("Topicus", "Portfolio Capital", "SMV", "software holding company", "https://www.topicus.com/", "active", "Europe", "vertical software", "software acquisition and operation", "acquisition_capital", "vertical software businesses", "software acquirer", 80, "Topicus is a candidate software acquisition and operating platform."),
    ("Aspire Software", "Portfolio Capital", "SMV", "software operating group", "https://www.aspiresoftware.com/", "active", "Global", "software", "acquire and operate software businesses", "acquisition_capital", "software companies", "software operating group", 84, "Aspire Software is a candidate software operating group."),
    ("Jonas Software", "Portfolio Capital", "SMV", "software operating group", "https://www.jonassoftware.com/", "active", "Global", "vertical software", "acquire and operate software companies", "acquisition_capital", "vertical market software companies", "software operating group", 84, "Jonas Software is a candidate vertical software acquirer."),
    ("Harris Computer", "Portfolio Capital", "SMV", "software operating group", "https://www.harriscomputer.com/", "active", "Global", "vertical software", "acquire and operate software companies", "acquisition_capital", "vertical market software companies", "software operating group", 84, "Harris Computer is a candidate vertical software acquirer."),
    ("Perseus Group", "Portfolio Capital", "SMV", "software operating group", "https://www.csiperseus.com/", "active", "Global", "software", "acquire and operate software companies", "acquisition_capital", "software businesses", "software operating group", 82, "Perseus Group is a candidate software acquisition operating group."),
    ("ESW Capital", "Portfolio Capital", "SMV", "software acquirer", "https://www.eswcapital.com/", "active", "United States / Global", "enterprise software", "acquire and operate software companies", "acquisition_capital", "software companies", "software acquirer", 82, "ESW Capital is a candidate software acquirer."),
    ("Alpine Software Group", "Portfolio Capital", "SMV", "software holding company", "https://www.alpinesg.com/", "active", "United States", "vertical SaaS", "buy and build software businesses", "acquisition_capital", "vertical SaaS companies", "software acquirer", 84, "Alpine Software Group is a candidate vertical SaaS acquirer."),
    ("Scaleworks", "Portfolio Capital", "SMV", "venture equity / operator", "https://scaleworks.com/", "active", "United States", "B2B SaaS", "acquire and operate B2B SaaS companies", "acquisition_capital", "B2B SaaS companies", "operator-investor", 84, "Scaleworks is a candidate B2B SaaS acquisition and operating platform."),
    ("Greater Sum Ventures", "Portfolio Capital", "SMV", "growth equity / acquirer", "https://greatersumventures.com/", "active", "United States", "business software", "invest in and scale business software", "growth_equity", "business software companies", "software investor", 78, "Greater Sum Ventures is a candidate business software investor/acquirer."),
    ("Arcadea Group", "Portfolio Capital", "SMV;Patient Capital", "software acquirer", "https://www.arcadeagroup.com/", "active", "Canada / Global", "B2B software", "long-duration software acquisition", "permanent_equity", "software founders seeking permanent capital", "software acquirer", 88, "Arcadea is a candidate long-duration software acquirer."),
    ("TAG Software Group", "Portfolio Capital", "SMV;Patient Capital", "software acquirer", "https://www.tagsoftwaregroup.com/", "active", "Global", "mission-critical software", "permanent home for software businesses", "permanent_equity", "mission-critical software companies", "software acquirer", 86, "TAG Software Group is a candidate permanent-capital software acquirer."),
    ("Vertus Group", "Portfolio Capital", "SMV", "software acquirer", "https://www.vertusgroup.com/", "active", "Europe", "software", "acquire and develop software companies", "acquisition_capital", "software companies", "software acquirer", 80, "Vertus Group is a candidate software acquirer."),
    ("Software Circle", "Portfolio Capital", "SMV", "software acquirer", "https://www.softwarecircle.com/", "active", "United Kingdom", "software", "software acquisition and operation", "acquisition_capital", "software businesses", "software acquirer", 78, "Software Circle is a candidate public software acquisition platform."),
    ("Chapters Group", "Portfolio Capital", "SMV", "holding company", "https://www.chaptersgroup.com/", "active", "Germany / Europe", "software and digital businesses", "acquisition holding company", "acquisition_capital", "small and medium software/digital businesses", "holding company", 78, "Chapters Group is a candidate acquisition holding company."),
    ("Visma", "Portfolio Capital", "SMV", "software company/acquirer", "https://www.visma.com/", "active", "Europe", "business software", "software acquisition and operation", "acquisition_capital", "business software companies", "software acquirer", 78, "Visma is a candidate European software acquirer."),
    ("Main Capital Partners", "Portfolio Capital", "SMV", "software investor", "https://main.nl/", "active", "Europe / United States", "enterprise software", "software private equity", "growth_equity;acquisition_capital", "software companies", "software investor", 78, "Main Capital Partners is a candidate software-focused investor."),
    # Search / ETA and acquisition entrepreneurship
    ("Searchfunder", "Search/ETA", "Portfolio Capital", "community/platform", "https://www.searchfunder.com/", "active", "Global", "search funds", "search fund community and resources", "search_capital", "searchers and ETA investors", "community platform", 88, "Searchfunder is a candidate central ecosystem platform for search funds."),
    ("Search Fund Alliance", "Search/ETA", "Portfolio Capital", "industry association", "https://www.searchfundalliance.org/", "active", "United States", "search funds", "search fund investor/member network", "search_capital", "search fund investors and searchers", "industry network", 84, "Search Fund Alliance is a candidate search fund ecosystem network."),
    ("Stanford Search Fund Center", "Search/ETA", "Search/ETA", "research center", "https://www.gsb.stanford.edu/experience/about/centers-institutes/ces/research/search-funds", "active", "United States", "search funds", "research and education", "search_capital", "searchers and investors", "research institution", 84, "Stanford's search fund research center is a candidate authoritative source for ETA taxonomy."),
    ("Pacific Lake Partners", "Search/ETA", "Patient Capital", "search fund investor", "https://www.pacificlake.com/", "active", "United States", "search funds", "search fund investing", "search_capital", "search fund entrepreneurs", "search fund investor", 84, "Pacific Lake is a candidate dedicated search fund investor."),
    ("Relay Investments", "Search/ETA", "Patient Capital", "search fund investor", "https://www.relayinvestments.com/", "active", "United States", "search funds", "search fund investing", "search_capital", "search fund entrepreneurs", "search fund investor", 82, "Relay Investments is a candidate search fund investor."),
    ("Anacapa Partners", "Search/ETA", "Patient Capital", "search fund investor", "https://www.anacapapartners.com/", "active", "United States", "search funds", "search fund investing", "search_capital", "search fund entrepreneurs", "search fund investor", 82, "Anacapa Partners is a candidate search fund investor."),
    ("Search Fund Partners", "Search/ETA", "Patient Capital", "search fund investor", "https://www.searchfunds.net/", "active", "United States", "search funds", "search fund investing", "search_capital", "search fund entrepreneurs", "search fund investor", 82, "Search Fund Partners is a candidate search fund investor."),
    ("Trilogy Search Partners", "Search/ETA", "Patient Capital", "search fund investor", "https://www.trilogysearch.com/", "active", "United States", "search funds", "search fund investing", "search_capital", "search fund entrepreneurs", "search fund investor", 82, "Trilogy Search Partners is a candidate search fund investor."),
    ("Next Coast ETA", "Search/ETA", "Patient Capital", "search fund investor", "https://www.nextcoasteta.com/", "active", "United States", "search funds", "entrepreneurship through acquisition", "search_capital", "ETA entrepreneurs", "search fund investor", 80, "Next Coast ETA is a candidate ETA investor."),
    ("WSC & Company", "Search/ETA", "Patient Capital", "search fund investor", "https://www.wscandcompany.com/", "active", "United States", "search funds", "search fund investing", "search_capital", "search fund entrepreneurs", "search fund investor", 80, "WSC & Company is a candidate search fund investor."),
    ("Ambit Partners", "Search/ETA", "Patient Capital", "search fund investor", "https://www.ambit.partners/", "active", "United States", "search funds", "search fund investing", "search_capital", "search fund entrepreneurs", "search fund investor", 78, "Ambit Partners is a candidate search fund investor."),
    ("Miramar Equity Partners", "Search/ETA", "Patient Capital", "search fund investor", "https://www.miramarequity.com/", "active", "United States", "search funds / SMB", "operator-led investing", "search_capital", "entrepreneur-led acquisitions", "search/ETA investor", 76, "Miramar Equity Partners is a candidate operator-led acquisition investor."),
    ("Hunter Search Capital", "Search/ETA", "Patient Capital", "search fund investor", "https://www.huntersearchcapital.com/", "active", "United States", "search funds", "search fund investing", "search_capital", "search fund entrepreneurs", "search fund investor", 76, "Hunter Search Capital is a candidate search fund investor."),
    ("Alza Capital Partners", "Search/ETA", "Patient Capital", "search fund investor", "https://www.alzacapital.com/", "active", "Latin America / Global", "search funds", "search fund investing", "search_capital", "search fund entrepreneurs", "search fund investor", 76, "Alza Capital Partners is a candidate search fund investor."),
    ("Acquira", "Search/ETA", "Portfolio Capital", "acquisition platform", "https://www.acquira.com/", "active", "United States / Global", "SMB acquisition", "acquisition entrepreneurship platform", "acquisition_capital", "entrepreneurs acquiring businesses", "acquisition platform", 76, "Acquira is a candidate acquisition entrepreneurship platform."),
    ("Mainshares", "Search/ETA", "Patient Capital", "acquisition platform/investor", "https://mainshares.com/", "active", "United States", "small business acquisition", "entrepreneur-led acquisition investing", "acquisition_capital", "operators acquiring small businesses", "acquisition platform", 78, "Mainshares is a candidate acquisition entrepreneurship platform."),
    ("Teamshares", "Patient Capital", "Search/ETA", "ownership platform", "https://www.teamshares.com/", "active", "United States", "small businesses", "employee ownership acquisition model", "patient_capital", "small business owners and employees", "ownership transition platform", 78, "Teamshares is a candidate patient-capital ownership transition platform."),
    ("Permanent Equity", "Patient Capital", "Search/ETA;Portfolio Capital", "private equity firm", "https://www.permanentequity.com/", "active", "United States", "small and medium businesses", "long-duration private equity", "permanent_equity", "durable private businesses", "patient capital investor", 84, "Permanent Equity is a candidate long-duration capital provider."),
    ("CapitalPad", "Search/ETA", "Instrument", "investment platform", "https://capitalpad.com/", "active", "United States", "search funds / independent sponsors", "private investment platform", "search_capital", "accredited investors and search fund sponsors", "investment platform", 72, "CapitalPad is a candidate search fund/private investment platform."),
    # Acquisition marketplaces
    ("Acquire.com", "SMV", "Search/ETA;Instrument", "acquisition marketplace", "https://acquire.com/", "active", "Global", "startups and internet businesses", "startup acquisition marketplace", "marketplace", "startup founders and buyers", "acquisition marketplace", 88, "Acquire.com is a candidate acquisition marketplace for the industry atlas."),
    ("Flippa", "SMV", "Search/ETA", "acquisition marketplace", "https://flippa.com/", "active", "Global", "online businesses", "online business marketplace", "marketplace", "buyers and sellers of online businesses", "acquisition marketplace", 80, "Flippa is a candidate online business acquisition marketplace."),
    ("Empire Flippers", "SMV", "Search/ETA", "acquisition marketplace", "https://empireflippers.com/", "active", "Global", "online businesses", "vetted online business marketplace", "marketplace", "buyers and sellers of online businesses", "acquisition marketplace", 80, "Empire Flippers is a candidate online business acquisition marketplace."),
    ("FE International", "SMV", "Search/ETA", "M&A advisor", "https://feinternational.com/", "active", "Global", "SaaS / ecommerce / content", "technology business M&A advisory", "marketplace;m_and_a_advisory", "technology business buyers and sellers", "M&A advisor", 78, "FE International is a candidate M&A advisory platform for tech-enabled businesses."),
    ("Quiet Light", "SMV", "Search/ETA", "M&A advisor", "https://quietlight.com/", "active", "United States / Global", "online businesses", "online business brokerage", "marketplace;m_and_a_advisory", "online business buyers and sellers", "M&A advisor", 76, "Quiet Light is a candidate online business acquisition advisor."),
    ("BizBuySell", "Search/ETA", "SMV", "business marketplace", "https://www.bizbuysell.com/", "active", "United States", "small businesses", "business-for-sale marketplace", "marketplace", "business buyers and sellers", "acquisition marketplace", 75, "BizBuySell is a candidate SMB acquisition marketplace."),
    ("BizQuest", "Search/ETA", "SMV", "business marketplace", "https://www.bizquest.com/", "active", "United States", "small businesses", "business-for-sale marketplace", "marketplace", "business buyers and sellers", "acquisition marketplace", 72, "BizQuest is a candidate SMB acquisition marketplace."),
    ("Axial", "SMV", "Search/ETA;Instrument", "deal network", "https://www.axial.net/", "active", "United States", "lower middle market", "private deal network", "marketplace", "lower middle market buyers, sellers, and advisors", "deal marketplace", 74, "Axial is a candidate lower-middle-market deal network."),
    ("BitsForDigits", "SMV", "Search/ETA", "acquisition marketplace", "https://bitsfordigits.com/", "active", "Global", "internet businesses", "partial/full acquisition marketplace", "marketplace", "internet business owners and buyers", "acquisition marketplace", 72, "BitsForDigits is a candidate internet business acquisition marketplace."),
    ("Microns", "LMV", "SMV", "micro-startup marketplace", "https://www.microns.io/", "active", "Global", "micro-startups", "micro-startup acquisition marketplace", "marketplace", "micro-startup buyers and sellers", "acquisition marketplace", 70, "Microns is a candidate micro-startup marketplace."),
    # Patient capital / impact / founder-friendly funds
    ("Acumen", "Patient Capital", "Sovereign Capital", "impact investor", "https://acumen.org/", "active", "Global", "social enterprise", "patient capital impact investing", "patient_capital", "social enterprises and mission-driven companies", "patient capital investor", 82, "Acumen is a candidate patient-capital reference institution."),
    ("Founders First Capital Partners", "Patient Capital", "Instrument;SMV", "revenue-based investor", "https://foundersfirstcapitalpartners.com/", "active", "United States", "service businesses / diverse founders", "revenue-based growth capital", "revenue_based_financing", "founder-led companies", "patient/growth capital provider", 78, "Founders First is a candidate revenue-based and founder-friendly capital provider."),
    ("Purpose Ventures", "Patient Capital", "Camel Modifier", "venture fund", "https://purpose.ventures/", "active", "United States", "purpose-driven founders", "patient venture capital", "equity", "mission-driven founders", "patient capital investor", 72, "Purpose Ventures is a candidate patient-capital venture entity."),
    ("Candide Group", "Patient Capital", "Sovereign Capital", "impact investment advisor", "https://candidegroup.com/", "active", "United States", "impact investing", "mission-aligned capital", "patient_capital", "impact-oriented companies and funds", "impact capital advisor", 70, "Candide Group is a candidate impact/patient-capital ecosystem entity."),
    ("RSF Social Finance", "Patient Capital", "Instrument", "social finance provider", "https://rsfsocialfinance.org/", "active", "United States", "social enterprises", "loans and social finance", "patient_capital", "mission-driven organizations", "patient capital provider", 72, "RSF Social Finance is a candidate social-finance and patient-capital provider."),
    ("Common Future", "Patient Capital", "Instrument", "community finance organization", "https://www.commonfuture.co/", "active", "United States", "community wealth", "community-rooted capital", "patient_capital", "community-led enterprises and funds", "ecosystem organization", 68, "Common Future is a candidate community capital ecosystem entity."),
    ("Zebras Unite", "Patient Capital", "Camel Modifier", "community/cooperative", "https://www.zebrasunite.org/", "active", "Global", "zebra companies", "movement and capital ecosystem", "community", "founders building for profit and purpose", "community and discourse node", 82, "Zebras Unite is a candidate movement/community source for non-unicorn company models."),
    ("Village Capital", "Patient Capital", "Sovereign Capital", "accelerator/investor", "https://vilcap.com/", "active", "Global", "impact startups", "entrepreneur support and investment", "equity;ecosystem_capital", "impact-oriented entrepreneurs", "accelerator and ecosystem builder", 74, "Village Capital is a candidate ecosystem builder for alternative startup finance."),
    ("Collab Capital", "Patient Capital", "SMV", "investment fund", "https://collab.capital/", "active", "United States", "Black founders", "founder-friendly capital", "equity;patient_capital", "Black founders building scalable businesses", "founder-friendly investor", 72, "Collab Capital is a candidate founder-friendly capital provider."),
    ("Boston Impact Initiative", "Patient Capital", "Instrument", "impact investor", "https://bostonimpact.org/", "active", "United States", "local impact businesses", "integrated capital / impact investing", "patient_capital", "local impact enterprises", "impact capital provider", 70, "Boston Impact Initiative is a candidate integrated-capital provider."),
    # Sovereign / strategic innovation capital
    ("Temasek", "Sovereign Capital", "UVC", "state-owned investment company", "https://www.temasek.com.sg/", "active", "Singapore / Global", "global investment", "sovereign-linked strategic capital", "equity", "global growth and innovation companies", "sovereign-linked investor", 78, "Temasek is a candidate sovereign-linked innovation capital allocator."),
    ("GIC", "Sovereign Capital", "UVC", "sovereign wealth fund", "https://www.gic.com.sg/", "active", "Singapore / Global", "global investment", "sovereign wealth investment", "equity", "global public and private investments", "sovereign wealth investor", 76, "GIC is a candidate sovereign capital allocator."),
    ("Mubadala", "Sovereign Capital", "UVC", "sovereign investor", "https://www.mubadala.com/", "active", "United Arab Emirates / Global", "strategic sectors", "sovereign investment", "equity", "global strategic sectors", "sovereign investor", 78, "Mubadala is a candidate sovereign innovation capital allocator."),
    ("Sanabil Investments", "Sovereign Capital", "UVC", "investment company", "https://www.sanabil.com/", "active", "Saudi Arabia / Global", "private investments", "sovereign-backed private investment", "equity", "global private companies and funds", "sovereign-backed investor", 76, "Sanabil is a candidate sovereign-backed innovation investor."),
    ("Public Investment Fund", "Sovereign Capital", "UVC", "sovereign wealth fund", "https://www.pif.gov.sa/", "active", "Saudi Arabia / Global", "strategic sectors", "sovereign wealth investment", "equity", "strategic national and global investments", "sovereign wealth investor", 76, "PIF is a candidate sovereign capital allocator."),
    ("Qatar Investment Authority", "Sovereign Capital", "UVC", "sovereign wealth fund", "https://www.qia.qa/", "active", "Qatar / Global", "global investment", "sovereign wealth investment", "equity", "global private and public assets", "sovereign wealth investor", 74, "QIA is a candidate sovereign capital allocator."),
    ("Bpifrance", "Sovereign Capital", "SMV", "public investment bank", "https://www.bpifrance.com/", "active", "France", "innovation / SMEs", "state-backed innovation capital", "equity;debt;grants", "French startups and companies", "public innovation investor", 82, "Bpifrance is a candidate national innovation capital institution."),
    ("British Business Bank", "Sovereign Capital", "SMV", "public development bank", "https://www.british-business-bank.co.uk/", "active", "United Kingdom", "SMEs / venture", "state-backed business finance", "equity;debt;fund_of_funds", "UK smaller businesses and funds", "public capital institution", 78, "British Business Bank is a candidate public capital institution."),
    ("EIC Fund", "Sovereign Capital", "UVC;SMV", "EU innovation fund", "https://eic.ec.europa.eu/eic-fund_en", "active", "European Union", "deep tech / innovation", "EU-backed equity capital", "equity", "European innovation companies", "public innovation fund", 82, "EIC Fund is a candidate sovereign/public innovation capital vehicle."),
    ("European Investment Fund", "Sovereign Capital", "UVC;SMV", "public fund-of-funds", "https://www.eif.org/", "active", "European Union", "SMEs / venture", "EU-backed SME and venture financing", "fund_of_funds;guarantees", "European SMEs and fund managers", "public capital institution", 82, "EIF is a candidate public capital institution for SMEs and venture funds."),
    ("NATO Innovation Fund", "Sovereign Capital", "UVC", "multinational venture fund", "https://www.nif.fund/", "active", "NATO countries", "deep tech / defense", "strategic deep-tech venture capital", "equity", "deep-tech companies relevant to allied security", "strategic innovation fund", 82, "NATO Innovation Fund is a candidate strategic sovereign-linked innovation fund."),
    ("KfW Capital", "Sovereign Capital", "UVC;SMV", "public fund investor", "https://www.kfw-capital.de/", "active", "Germany", "venture / growth", "public-backed venture fund investment", "fund_of_funds", "German and European venture funds", "public capital institution", 78, "KfW Capital is a candidate public-backed venture fund investor."),
    ("EDBI", "Sovereign Capital", "UVC", "strategic investment arm", "https://www.edbi.com/", "active", "Singapore / Global", "strategic growth sectors", "strategic government-linked investment", "equity", "high-growth technology companies", "strategic investor", 76, "EDBI is a candidate strategic innovation capital entity."),
    ("SGInnovate", "Sovereign Capital", "UVC", "deep tech investor/ecosystem", "https://www.sginnovate.com/", "active", "Singapore", "deep tech", "state-linked deep tech ecosystem capital", "equity;ecosystem_capital", "deep tech founders", "public ecosystem investor", 76, "SGInnovate is a candidate sovereign-linked deep tech ecosystem investor."),
    ("Khazanah Nasional", "Sovereign Capital", "UVC", "sovereign wealth fund", "https://www.khazanah.com.my/", "active", "Malaysia / Global", "strategic investment", "sovereign wealth investment", "equity", "strategic Malaysian and global investments", "sovereign investor", 74, "Khazanah is a candidate sovereign capital allocator."),
    ("Israel Innovation Authority", "Sovereign Capital", "SMV", "public innovation agency", "https://innovationisrael.org.il/en/", "active", "Israel", "innovation / technology", "public innovation grants and support", "grants;ecosystem_capital", "Israeli technology companies", "public innovation agency", 78, "Israel Innovation Authority is a candidate public innovation capital institution."),
    ("Innovate UK", "Sovereign Capital", "SMV", "public innovation agency", "https://www.ukri.org/councils/innovate-uk/", "active", "United Kingdom", "innovation / technology", "public innovation grants and support", "grants;ecosystem_capital", "UK innovation companies", "public innovation agency", 76, "Innovate UK is a candidate public innovation capital institution."),
    ("In-Q-Tel", "Sovereign Capital", "UVC", "strategic venture investor", "https://www.iqt.org/", "active", "United States", "national security technology", "strategic venture capital", "equity;strategic_capital", "technology companies relevant to national security", "strategic investor", 80, "In-Q-Tel is a candidate strategic innovation capital entity."),
    # Studios / foundries / portfolio capital
    ("High Alpha", "Portfolio Capital", "UVC", "venture studio", "https://www.highalpha.com/", "active", "United States", "B2B SaaS", "venture studio and venture fund", "studio_equity", "B2B SaaS company formation", "venture studio", 84, "High Alpha is a candidate venture studio and portfolio capital entity."),
    ("Atomic", "Portfolio Capital", "UVC", "venture studio", "https://atomic.vc/", "active", "United States", "venture studio", "company creation platform", "studio_equity", "founders building companies from studio concepts", "venture studio", 82, "Atomic is a candidate venture studio."),
    ("Expa", "Portfolio Capital", "UVC", "startup studio/fund", "https://www.expa.com/", "active", "United States / Global", "startup creation", "startup studio and early capital", "studio_equity", "founders building new startups", "startup studio", 80, "Expa is a candidate startup studio."),
    ("Betaworks", "Portfolio Capital", "UVC", "startup studio", "https://betaworks.com/", "active", "United States", "internet / media / AI", "startup studio and investment", "studio_equity", "early internet and AI companies", "startup studio", 78, "Betaworks is a candidate startup studio."),
    ("Hexa", "Portfolio Capital", "UVC", "startup studio", "https://www.hexa.com/", "active", "France / Europe", "startup studio", "startup studio / company builder", "studio_equity", "founders joining studio-built companies", "startup studio", 82, "Hexa is a candidate startup studio."),
    ("Rocket Internet", "Portfolio Capital", "UVC", "venture builder", "https://www.rocket-internet.com/", "active", "Germany / Global", "internet companies", "venture builder", "studio_equity", "internet company formation", "venture builder", 78, "Rocket Internet is a candidate venture builder."),
    ("Idealab", "Portfolio Capital", "UVC", "startup studio", "https://www.idealab.com/", "active", "United States", "technology startups", "startup studio", "studio_equity", "technology startup formation", "startup studio", 78, "Idealab is a candidate startup studio."),
    ("Pioneer Square Labs", "Portfolio Capital", "UVC", "startup studio", "https://www.psl.com/", "active", "United States", "technology startups", "startup studio and venture fund", "studio_equity", "technology startup founders", "startup studio", 78, "Pioneer Square Labs is a candidate startup studio."),
    ("Human Ventures", "Portfolio Capital", "UVC", "startup studio", "https://human.vc/", "active", "United States", "consumer / technology", "startup studio and fund", "studio_equity", "founders building technology companies", "startup studio", 76, "Human Ventures is a candidate startup studio."),
    ("Science Inc.", "Portfolio Capital", "UVC", "startup studio", "https://www.science-inc.com/", "active", "United States", "digital businesses", "startup studio", "studio_equity", "digital company founders", "startup studio", 74, "Science Inc. is a candidate startup studio."),
    ("Wilbur Labs", "Portfolio Capital", "UVC", "startup studio", "https://www.wilburlabs.com/", "active", "United States", "startup creation", "startup studio", "studio_equity", "operators building studio companies", "startup studio", 76, "Wilbur Labs is a candidate startup studio."),
    ("Juxtapose", "Portfolio Capital", "UVC", "creation-oriented investment firm", "https://www.juxtapose.com/", "active", "United States", "company creation", "company creation and investment", "studio_equity", "founders building new companies", "company creation platform", 76, "Juxtapose is a candidate company creation platform."),
    ("Founders Factory", "Portfolio Capital", "UVC", "venture studio/accelerator", "https://foundersfactory.com/", "active", "United Kingdom / Global", "startup creation", "venture studio and accelerator", "studio_equity", "founders building with studio support", "venture studio", 78, "Founders Factory is a candidate venture studio."),
    ("Entrepreneur First", "Portfolio Capital", "UVC;LMV", "talent investor", "https://www.joinef.com/", "active", "Global", "founder formation", "talent investing and company formation", "equity", "pre-company founders", "talent investor", 78, "Entrepreneur First is a candidate company-formation capital platform."),
    ("Antler", "Portfolio Capital", "UVC;LMV", "startup generator/investor", "https://www.antler.co/", "active", "Global", "founder formation", "company formation and early investment", "equity", "pre-seed founders", "startup generator", 78, "Antler is a candidate global company-formation investor."),
    ("Enhance Ventures", "Portfolio Capital", "UVC", "venture studio", "https://enhance.online/", "active", "MENA", "digital businesses", "venture studio", "studio_equity", "founders building with studio infrastructure", "venture studio", 74, "Enhance Ventures is a candidate venture studio."),
    ("Team8", "Portfolio Capital", "UVC;Sovereign Capital", "venture group", "https://team8.vc/", "active", "Israel / United States", "cybersecurity / fintech / data", "company creation and venture capital", "studio_equity;equity", "founders building in strategic technology sectors", "venture group", 78, "Team8 is a candidate company creation and venture capital platform."),
    ("Fractal Software", "Portfolio Capital", "SMV", "vertical SaaS studio", "https://www.fractalsoftware.com/", "active", "United States", "vertical SaaS", "vertical SaaS company creation", "studio_equity", "operators building vertical SaaS companies", "vertical SaaS studio", 76, "Fractal Software is a candidate vertical SaaS studio."),
    # LMV / indie / micro venture and communities
    ("Weekend Fund", "LMV", "UVC", "venture fund", "https://weekend.fund/", "active", "United States / Global", "early-stage startups", "small early-stage investing", "equity", "early founders and makers", "micro fund", 68, "Weekend Fund is a candidate micro/early-stage fund for the LMV lane."),
    ("Pioneer", "LMV", "UVC", "founder platform", "https://pioneer.app/", "active", "Global", "early founders", "remote startup tournament / funding", "grants;equity", "early founders and internet-native builders", "founder platform", 70, "Pioneer is a candidate founder discovery and micro-capital platform."),
    ("AI Grant", "LMV", "UVC", "grant/fund", "https://aigrant.org/", "active", "Global", "AI startups", "AI startup grants and investment", "grants;equity", "AI founders", "grant and capital program", 72, "AI Grant is a candidate AI-era micro-capital entity."),
    ("HF0", "LMV", "UVC", "AI residency/fund", "https://www.hf0.com/", "active", "United States", "AI startups", "AI founder residency and funding", "equity", "AI-native founders", "AI startup program", 72, "HF0 is a candidate AI-native founder capital program."),
    ("Indie Hackers", "LMV", "Camel Modifier", "community", "https://www.indiehackers.com/", "active", "Global", "indie startups", "founder community and discourse", "community", "independent internet founders", "community and discourse node", 74, "Indie Hackers is a candidate discourse/community node for LMV and seedstrapping evidence."),
    ("MicroConf", "LMV", "Camel Modifier", "community/conference", "https://microconf.com/", "active", "Global", "bootstrapped SaaS", "bootstrapped founder community", "community", "self-funded and bootstrapped SaaS founders", "community and discourse node", 76, "MicroConf is a candidate community node for bootstrapped and calm company founders."),
]


INSTRUMENTS = [
    ("revenue_share", "Revenue share", "Capital where repayment or investor economics are linked to company revenue.", ["TinySeed"]),
    ("revenue_based_financing", "Revenue-based financing", "Repayment tied to revenue or recurring revenue rather than traditional VC equity.", ["Lighter Capital", "Decathlon Capital Partners", "TIMIA Capital", "Flow Capital", "Corl", "Wayflyer", "Clearco", "GetVantage", "Velocity", "Klub", "Recur Club"]),
    ("shared_earnings", "Shared earnings", "Investor return linked to shared earnings/profit rather than forced exit economics.", ["Calm Company Fund", "Earnest Capital", "Indie.vc"]),
    ("non_dilutive_capital", "Non-dilutive growth capital", "Capital positioned around preserving founder ownership while funding growth.", ["Founderpath", "Capchase", "Uncapped", "Arc", "Braavo Capital"]),
    ("growth_debt", "Growth debt", "Debt or structured capital for software companies that do not want or need more equity.", ["SaaS Capital", "Bigfoot Capital", "Espresso Capital"]),
    ("embedded_finance", "Embedded platform finance", "Capital embedded into payments, commerce, or platform workflows.", ["Stripe Capital", "Shopify Capital", "PayPal Working Capital", "YouLend", "Liberis", "Parafin"]),
    ("growth_equity_for_bootstrapped_software", "Growth equity for bootstrapped software", "Minority, majority, or flexible growth equity for founder-led, capital-efficient software companies that may not fit classic unicorn VC.", ["DWP Capital", "TVC Capital", "D2 Fund", "SeedTwo Capital", "Sequel Capital", "Mainsail Partners", "Serent Capital", "Mamba Growth", "Five Elms Capital", "Elsewhere Partners", "Sunstone Partners", "Expedition Growth Capital", "Silversmith Capital Partners", "Level Equity"]),
    ("permanent_equity", "Permanent equity", "Long-duration or no-forced-exit equity ownership.", ["Banyan Software", "Valsoft", "Constellation Software", "Arcadea Group", "TAG Software Group", "Permanent Equity", "Tiny"]),
    ("search_capital", "Search capital", "Capital used to fund searchers and acquisitions in ETA/search fund models.", ["Searchfunder", "Pacific Lake Partners", "Relay Investments", "Anacapa Partners", "Search Fund Partners", "Trilogy Search Partners", "Next Coast ETA"]),
    ("studio_equity", "Studio equity", "Equity created through venture studios or company formation platforms.", ["High Alpha", "Atomic", "Expa", "Hexa", "Founders Factory", "Fractal Software"]),
    ("marketplace", "Acquisition marketplace", "Marketplace or deal network connecting business buyers and sellers.", ["Acquire.com", "Flippa", "Empire Flippers", "FE International", "Quiet Light", "BizBuySell", "BizQuest", "Axial", "BitsForDigits", "Microns"]),
]


SCRAPE_TARGETS = [
    ("SMV", "SMV", "public_web", "acquisition-first venture fund startups M&A lens", "SV8;Tangle Ventures", "public_web", "high", "name;website;asset_class;claim;instrument;active_status", "Find firms explicitly designing startups around acquisitions or middle outcomes."),
    ("SMV", "SMV", "public_web", "bootstrapped founder-led B2B software growth equity capital efficient", "Mainsail Partners;Serent Capital;DWP Capital;Elsewhere Partners", "public_web", "high", "name;website;asset_class;claim;target_company_profile", "Find growth-equity firms serving bootstrapped and capital-efficient software companies."),
    ("SMV", "SMV", "public_web", "vertical SaaS capital efficient growth equity seed Series A not growth at all costs", "Union Group Fund;SeedTwo Capital;Sequel Capital;TVC Capital", "public_web", "high", "name;website;sector_focus;capital_model;claim", "Find vertical SaaS and capital-efficient B2B software capital providers."),
    ("SMV", "SMV", "public_web", "software holding company acquire bootstrapped SaaS founders permanent home", "Banyan Software;Valsoft;Arcadea Group", "public_web", "high", "name;website;target_company_profile;capital_model", "Find SaaS acquirers and holdcos."),
    ("SMV", "SMV", "public_web", "micro private equity SaaS acquisition holding company", "SureSwift Capital;saas.group", "public_web", "high", "name;website;sector_focus;claim", "Find micro-PE and SaaS acquisition platforms."),
    ("Instrument", "SMV", "public_web", "revenue based financing SaaS non dilutive capital providers", "Lighter Capital;Capchase;Founderpath", "public_web", "high", "provider;instrument;terms_language;target_customer", "Map instrument providers as entities in a real asset class while retaining instrument terms separately."),
    ("Patient Capital", "Patient Capital", "public_web", "patient capital evergreen fund founders no forced exit software", "Permanent Equity;Acumen;Banyan Software", "public_web", "high", "name;website;hold_period;liquidity_language", "Find long-duration capital providers."),
    ("LMV", "LMV", "public_web", "indie hacker fund AI micro venture solo founder capital", "TinySeed;AI Grant;HF0;Pioneer", "public_web", "medium", "name;website;team_size_language;capital_model", "Find AI-era micro venture and indie founder capital."),
    ("Search/ETA", "Search/ETA", "public_web", "search fund investors entrepreneurship through acquisition list", "Search Fund Alliance;Searchfunder;Pacific Lake Partners", "public_web", "high", "name;website;searcher_profile;capital_role", "Map search fund investor ecosystem."),
    ("Portfolio Capital", "Portfolio Capital", "public_web", "venture studio startup foundry company builder shared infrastructure", "High Alpha;Atomic;Hexa;Founders Factory", "public_web", "high", "name;website;studio_model;sector", "Map venture studios and foundries."),
    ("Sovereign Capital", "Sovereign Capital", "public_web", "sovereign innovation fund national technology startups AI defense climate", "NATO Innovation Fund;Bpifrance;EIC Fund", "public_web", "high", "name;website;mandate;strategic_sector", "Map strategic public/sovereign innovation capital."),
    ("All", "All", "open_dataset", "Hugging Face crunchbase startup funding investors acquisitions dataset", "opensporks/crunchbase;calebheinzman/Crunchbase_People", "open_dataset", "medium", "dataset;license;schema;candidate_entities", "Use datasets as seeds only, not authoritative proof."),
    ("All", "All", "paid_optional", "PitchBook alternative VC revenue based financing search funds software acquirers", "PitchBook;CB Insights;Preqin;Dealroom;Tracxn", "paid_optional", "low", "paid_source;access_status;fields_available", "Optional future connectors if access is available."),
]


ENTITY_INTAKE_QUEUE = [
    {
        "lead_id": "intake-onesixone-ventures",
        "name": "OneSixOne Ventures",
        "lead_type": "user_discovered_entity",
        "website": "https://www.onesixone.ventures/",
        "source_urls": "https://www.onesixone.ventures/;https://www.deep-tech-week.com/organizations/onesixone-fund;https://refreshmiami.com/news/meet-the-vc-duo-shaking-up-miamis-tech-scene/;https://www.linkedin.com/company/onesixone-ventures",
        "discovered_from": "user_instagram_lead",
        "target_asset_class": "Unknown Candidate",
        "target_entity_type": "pre-seed venture fund / platform / community",
        "active_status": "unknown",
        "source_tier": "public_web",
        "priority": "high",
        "evidence_status": "needs_verification",
        "review_status": "queued",
        "created_at": TODAY,
        "notes": "Queue only; do not add to industry_entities.csv or entity_claims.csv until source text supports a specific atlas classification.",
    },
]


EXTRA_SOURCES = [
    ("https://techcrunch.com/2021/06/08/network-security-startup-extrahop-skips-and-jumps-to-900m-exit/", "TechCrunch ExtraHop exit", "article", "credible_press", "public web", "Supporting company-event source from the earlier company proof layer."),
    ("https://techcrunch.com/2021/03/16/appfire-provider-of-atlassian-apps-raises-100m-to-continue-its-buying-spree/", "TechCrunch Appfire growth investment", "article", "credible_press", "public web", "Supporting company-event source from the earlier company proof layer."),
    ("https://theygotacquired.com/saas/baremetrics-acquired-by-xenon-partners/", "They Got Acquired Baremetrics", "article", "credible_press", "public web", "Supporting company-event source; verify before paper use."),
    ("https://startupfounderstories.com/stories/rob-walling-drip-bootstrapped-acquisition", "Startup Founder Stories Drip", "founder_story", "discourse", "public web", "Supporting founder-story source; verify before paper use."),
    ("https://en.wikipedia.org/wiki/David_Hauser", "David Hauser profile", "profile", "database_seed", "public web", "Lead source only; find primary/press source before paper use."),
    ("https://tinyseed.com/about", "TinySeed about", "company_site", "primary", "public web", "Source for TinySeed origin story and capital-efficiency framing."),
    ("https://calmfund.com/writing/shared-earnings-safe", "Calm Company Fund shared earnings SAFE", "company_site", "primary", "public web", "Source for shared earnings SAFE framing."),
    ("https://help.acquire.com/how-does-acquire.com-work", "Acquire.com help", "company_site", "primary", "public web", "Source for acquisition marketplace mechanics."),
    ("https://www.indiehackers.com/post/we-ve-acquired-40-bootstrapped-businesses-in-6-years-and-run-a-growing-portfolio-of-saas-products-ama-3f640f44fc", "Indie Hackers SureSwift AMA", "founder_discourse", "discourse", "public web", "Discourse source for SaaS acquisition holding company model; verify with company source before central claims."),
    ("https://www.venturestudioindex.com/p/the-largest-venture-studio-exits", "Venture Studio Index largest exits", "research", "research", "public web", "Research/media source for venture studio exits and methodology limitations."),
    ("https://www.breit.com/offering-terms/", "BREIT offering terms", "company_site", "primary", "public web", "Supporting liquidity-design analogy, not core industry proof."),
    ("https://www.onesixone.ventures/", "OneSixOne Ventures official site", "official_site", "primary", "public web", "Intake source only; verify source text before adding atlas claims."),
    ("https://www.deep-tech-week.com/organizations/onesixone-fund", "Deep Tech Week OneSixOne profile", "directory_profile", "research", "public web", "Intake source only; use as candidate evidence, not authoritative proof by itself."),
    ("https://refreshmiami.com/news/meet-the-vc-duo-shaking-up-miamis-tech-scene/", "Refresh Miami OneSixOne profile", "article", "credible_press", "public web", "Intake source only; useful for platform/community model verification."),
    ("https://www.linkedin.com/company/onesixone-ventures", "OneSixOne Ventures LinkedIn", "social_profile", "social", "public web", "Intake source only; corroborate with official or press sources before paper use."),
]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    entity_rows = []
    claim_rows = []
    source_rows = []
    seen_ids: set[str] = set()

    for item in ENTITIES:
        (
            name,
            primary_asset_class,
            secondary_asset_classes,
            entity_type,
            website,
            active_status,
            geography,
            sector_focus,
            capital_model,
            instrument_types,
            target_company_profile,
            ecosystem_role,
            fit_score,
            claim,
        ) = item
        base_id = slug(name)
        entity_id = base_id
        suffix = 2
        while entity_id in seen_ids:
            entity_id = f"{base_id}-{suffix}"
            suffix += 1
        seen_ids.add(entity_id)
        evidence_status = "verified_fact" if name in {"TinySeed", "Basecamp Bootstrapped Profitable Proud"} else "candidate_evidence"
        entity_rows.append(
            {
                "entity_id": entity_id,
                "name": name,
                "primary_asset_class": primary_asset_class,
                "secondary_asset_classes": secondary_asset_classes,
                "entity_type": entity_type,
                "website": website,
                "active_status": active_status,
                "source_tier": "public_web",
                "geography": geography,
                "sector_focus": sector_focus,
                "capital_model": capital_model,
                "instrument_types": instrument_types,
                "target_company_profile": target_company_profile,
                "non_unicorn_thesis": "candidate supports industry mapping outside or adjacent to classic unicorn VC",
                "ecosystem_role": ecosystem_role,
                "fit_score": str(fit_score),
                "evidence_status": evidence_status,
                "last_verified_at": TODAY,
                "notes": "Atlas seed row; verify source text before using as paper-ready evidence.",
            }
        )
        claim_rows.append(
            {
                "claim_id": f"claim-{entity_id}-001",
                "entity_id": entity_id,
                "entity_name": name,
                "claim_type": "classification",
                "claim": claim,
                "source_url": website,
                "source_type": "official_site",
                "source_quality": "primary",
                "source_tier": "public_web",
                "evidence_status": evidence_status,
                "last_verified_at": TODAY,
                "notes": "Use as discovery evidence until source text is reviewed and quoted/paraphrased in the paper.",
            }
        )
        source_rows.append(
            {
                "source_url": website,
                "source_name": f"{name} official site",
                "source_type": "official_site",
                "source_quality": "primary",
                "license_or_access": "public web",
                "notes": "Industry-atlas entity source; verify page-level claim before publication.",
                "last_checked": TODAY,
            }
        )

    instrument_rows = []
    entity_by_name = {row["name"]: row for row in entity_rows}
    for instrument_id, instrument_name, description, providers in INSTRUMENTS:
        for provider in providers:
            entity = entity_by_name.get(provider)
            if not entity:
                continue
            instrument_rows.append(
                {
                    "instrument_id": instrument_id,
                    "instrument_name": instrument_name,
                    "provider_entity_id": entity["entity_id"],
                    "provider_name": provider,
                    "asset_class": entity["primary_asset_class"],
                    "description": description,
                    "source_url": entity["website"],
                    "evidence_status": entity["evidence_status"],
                    "notes": "Provider-instrument mapping is seed-level and should be verified against provider pages.",
                }
            )

    scrape_rows = [
        {
            "lane": lane,
            "target_asset_class": target_asset_class,
            "source_family": source_family,
            "query": query,
            "seed_entities_or_sources": seeds,
            "source_tier": tier,
            "priority": priority,
            "expected_fields": expected_fields,
            "notes": notes,
        }
        for lane, target_asset_class, source_family, query, seeds, tier, priority, expected_fields, notes in SCRAPE_TARGETS
    ]

    write_csv(EVIDENCE / "asset_classes.csv", ASSET_CLASSES, list(ASSET_CLASSES[0].keys()))
    write_csv(EVIDENCE / "industry_entities.csv", entity_rows, list(entity_rows[0].keys()))
    write_csv(EVIDENCE / "entity_claims.csv", claim_rows, list(claim_rows[0].keys()))
    write_csv(EVIDENCE / "instrument_provider_map.csv", instrument_rows, list(instrument_rows[0].keys()))
    write_csv(EVIDENCE / "scrape_targets.csv", scrape_rows, list(scrape_rows[0].keys()))
    write_csv(EVIDENCE / "entity_intake_queue.csv", ENTITY_INTAKE_QUEUE, list(ENTITY_INTAKE_QUEUE[0].keys()))

    # Merge source rows with existing registry without dropping prior company evidence sources.
    registry_path = EVIDENCE / "source_registry.csv"
    existing: dict[str, dict[str, str]] = {}
    if registry_path.exists():
        with registry_path.open("r", encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                existing[row["source_url"]] = row
    for row in source_rows:
        existing.setdefault(row["source_url"], row)
    for url, name, source_type, quality, access, notes in EXTRA_SOURCES:
        existing.setdefault(
            url,
            {
                "source_url": url,
                "source_name": name,
                "source_type": source_type,
                "source_quality": quality,
                "license_or_access": access,
                "notes": notes,
                "last_checked": TODAY,
            },
        )
    write_csv(
        registry_path,
        list(existing.values()),
        ["source_url", "source_name", "source_type", "source_quality", "license_or_access", "notes", "last_checked"],
    )

    print(f"Wrote {len(entity_rows)} industry entities")
    print(f"Wrote {len(claim_rows)} entity claims")
    print(f"Wrote {len(instrument_rows)} instrument-provider mappings")
    print(f"Wrote {len(scrape_rows)} scrape targets")
    print(f"Wrote {len(ENTITY_INTAKE_QUEUE)} entity intake leads")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
