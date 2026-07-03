# Fast-Exit Liquidity Lens - Codex Reverification Audit (2026-06-27)

## Scope

This audits Claude's `docs/research/fast_exit_liquidity_lens_2026-06-27.md` output against the user's added filter:

1. Every counted item must be tech-enabled.
2. Every counted item must not be PE/private equity.
3. Ambiguous cases are held for user review instead of assumed in.

Important source limitation: Claude's report references raw scratchpad files named `confirmed_digest.json` and `rejected_digest.json`, but those files were not present in the repo or the provided attachment during this audit. The durable report itself says "43 survived; ~30 are distinct" and "Do not cite 43." This audit therefore covers every named confirmed/distinct item in the durable report, not unrecoverable duplicate rows from the missing 43-row digest.

No atlas CSVs were edited. No rows were marked paper-ready.

## Bottom line

Claude's headline is too loose for the new user filter. After re-verification, the report should not be treated as "43 confirmed tech-enabled non-PE entities." The durable report contains roughly 30 named/distinct items, many of which are discourse rather than entities, and several confirmed items are explicitly PE or micro-PE.

Strictly usable as tech-enabled and non-PE entity/operator candidates: 14.

Hold for user review: 4.

Exclude under the user's "not PE/private equity" filter: 5 named items, including 3 operating funds/firms.

Discourse-only / not entity candidates: 9.

## Key corrections to Claude

1. **Do not cite 43.** The raw 43-row digest is unavailable, and Claude's own report says the 43 collapse to about 30 distinct items after duplicate cleanup.
2. **WebStreet is PE.** The source frames WebStreet as a "Micro Private Equity Model"; it is tech-enabled but fails a strict no-PE filter.
3. **Edited Capital is PE.** Its Fund III page explicitly calls the fund "the next evolution in private equity investing"; it is tech-enabled but fails a strict no-PE filter.
4. **LTV SaaS Fund is PE-like.** It buys, operates, and sells SaaS assets through investment funds. Even if it does not brand itself as PE on the cited page, it is an acquisition-fund model and should be excluded if the user's PE exclusion is literal.
5. **SquadS quote now reproduces, but the classification still should be held.** The investor page now contains the "Early Exits Model" language, but it also says "4X returns within 10 years," so the case is not a clean under-6-year fast-exit signal without deciding whether "capital recovery within 4 years" is enough.
6. **Favcy is not cleanly tech-enabled across the cited cohort evidence.** The program is a build-to-sell venture studio, but cited completed examples include non-tech or weakly tech-enabled businesses. Keep only as program-level / later-cohort evidence until entity-by-entity portfolio tech status is verified.
7. **Several "confirmed" items are not entities.** Venture Studio Forum, Startup Chai, Startup Funding Espresso, Romulus Strategy, SaaSCity, Surges, Jake's Insights, Superscout, wildwildmoney / buy-startups, and the Medium/Zenith item are discourse or infrastructure signals, not atlas entity candidates.

## Strict keep list - tech-enabled and not PE

| Item | Entity type | Exit horizon / length | Exit strategy | Source checked | Tech-enabled result | PE result | Disposition |
|---|---:|---|---|---|---|---|---|
| Sequel Capital | fund/investor | 2-3 years | Minority growth investment in agentic B2B SaaS, with a stated path to acquisition rather than a 10-year fund hold. | https://www.sequel-capital.com/ | Pass: Agentic B2B SaaS, $2M-$10M ARR | Pass with growth-equity caveat, not explicit PE/buyout | Keep |
| Cocreatd | venture studio/operator | Executed 8-month creation-to-exit for System7; 6 months from concept to LSE listing for a security venture | Self-funded studio co-founds ventures from day zero and exits via acquisition or public listing once the venture is packaged and validated. | https://startupsmagazine.co.uk/article-cocreatd-achieves-ps100m-portfolio-value-first-year | Pass: startups, software/security venture, LSE listing | Pass: studio/operator, not PE | Keep |
| AscendX Ventures AG | venture studio/operator | Targeting full returns within 12 months | Acquire/build/exit turnkey B2B SaaS and Salesforce-native digital businesses, then sell them through an auction or marketplace-style process. | https://ascendx.ventures/ | Pass: B2B SaaS/Salesforce/AI-native software assets | Pass: studio/auction model, not PE | Keep |
| FutureFirst | VC fund | 2-3 years after Series A, roughly 4-6 years from seed depending on start point | Seed vertical-AI companies, then treat a several-hundred-million-dollar sale as a successful outcome rather than holding for a unicorn IPO. | https://www.calcalistech.com/ctechnews/article/hy9uxu3ubx | Pass: vertical AI seed fund | Pass: VC, not PE | Keep |
| The2410 | SaaS builder/operator | 24-48 months before exit, with optional continued scaling | Build micro-SaaS assets, grow them, then sell at small acquisition values if the upside does not justify continued scaling. | https://2410.ee/en/service/invest-in-saas | Pass: SaaS assets | Pass: build/sell investment program, not explicit PE | Keep with small-scale caveat |
| FirstFounders (F2) | venture studio/operator | Within 36 months | AI-first venture studio co-builds startups with a target of acquisition inside three years, rather than simply growth for growth's sake. | https://thecondia.com/partners/firstfounders-africa-venture-studio-startup/ | Pass: AI-first FinTech/Consumer/Entertainment studio | Pass: venture studio, not PE | Keep |
| Napkin Ventures | venture studio/operator | Within 5 years / about 5-year horizon | Exit Napkin's primary management role through a larger preferred investor round, company sale, or company buyback of Napkin's interest. | https://www.napkinventures.fund/ | Pass: B2B SaaS studio | Pass: studio model, not PE | Keep |
| Mirai Ventures | venture fund/studio-adjacent | 24-36 months | Build or back ventures designed for strategic exits to corporates while corporate demand is high. | https://miraiventures.substack.com/p/how-mirai-ventures-delivers-superior | Pass: AI/software ventures | Pass: venture fund/studio language, not PE | Keep, self-published |
| Redbud VC | VC fund | 2-year material exit example | Sell a stake to a Series A investor to create early liquidity; this is a secondary/liquidity strategy rather than a full terminal company sale. | https://redbud.beehiiv.com/p/liquid-future-nimble-vcs-have-a-liquidity-advantage | Pass: VC-backed technology context | Pass: VC, not PE | Keep as secondary/liquidity signal, not full company-exit proof |
| Highline Beta / Ben Yoskovitz | venture studio + practitioner | 3-5 years for modest portfolio-company sales; "within a few years" for cash-on-cash returns | Studio takes larger early ownership positions and targets modest exits that can return meaningful cash quickly, instead of waiting for 7-10+ year venture outcomes. | https://www.highlinebeta.com/blog/why-exits-define-studio-success and https://www.focusedchaos.co/p/venture-studios-need-to-focus-on-exits | Pass: venture studio startups | Pass: studio/VC, not PE | Keep as operator + discourse |
| Teemu Raitaluoto / AIContentfy | operator/company | About 2 years | Build AIContentfy with an exit in mind, scale to $1M ARR, then sell through Acquire.com in an all-cash transaction. | https://blog.acquire.com/scaling-ai-content-to-1m-arr-and-a-successful-exit/ | Pass: AI content SaaS/software | Pass: founder/operator sale, not PE | Keep |
| Wasp.sh case study / Max's AI Etsy generator | operator/company | 5 months total | Build a software app, get traction quickly, then sell the app rather than continue operating it long-term. | https://wasp.sh/blog/2024/07/03/building-selling-saas-in-5-months | Pass: software app | Pass: founder/operator sale, not PE | Keep |
| Joshua Tiernan / Tiny Empires | operator | 1-3 years in Claude's source summary; serial five-acquisition pattern | Build and sell micro-businesses as a repeated operator model. | https://www.indiehackers.com/product/tiny-empires | Pass, based on micro-business / indie-web operator context | Pass: founder/operator, not PE | Keep with source-depth caveat |
| Fizan Muhammad / IntakeGenie | operator/company | About 2 weeks from listing to close in Claude's source summary | List and sell a SaaS startup through an acquisition marketplace; exact elapsed time still needs transcript-level confirmation. | https://creators.spotify.com/pod/profile/startup-acquisitions/episodes/How-to-Prime-Your-Business-For-a-Seamless-Acquisition-with-Sukhpal-Saini-e2u5ls7 | Pass: SaaS startup context | Pass: founder/operator sale, not PE | Keep, but exact "two weeks" quote needs transcript-level proof |

## Hold for user review

| Item | Exit horizon / length | Exit strategy | Why held | Source |
|---|---|---|---|---|
| SquadS Ventures | Capital recovery within 4 years; 4X returns within 10 years | Company-builder runs B2B SaaS portfolio and distributes exit proceeds progressively. | Tech-enabled B2B SaaS and not PE, but "capital recovery within 4 years" plus "4X returns within 10 years" is not a clean under-6-year exit. User should decide whether early capital recovery qualifies. | https://squads.ventures/angeles-inversionistas/ |
| Favcy Build-to-Sell (BTS) | 36-48 months to acquisition; cited exits at about 11-12 months | Co-build ventures from the ground up with EIRs, then sell them by acquisition. | Program is a build-to-sell venture studio and not PE, but cited cohort examples include sweets, blue-collar services, and wedding venues. Count only if using program-level tech-enabled status, not every underlying venture. | https://www.favcybts.com/btsfoundertribe and https://indianstartupnews.com/funding/favcy-venture-builders-raises-rs-1-8-crore-6900251 |
| Stuart Faught | Claimed most deals close in 30-45 days | Serial micro-SaaS exit operator; sell small SaaS businesses quickly after acquisition or build-up. | Appears to be a micro-SaaS operator/exiter, not PE, but the cited "rapid exit strategy" claim was only found via podcast/search surfaces during this pass. Needs transcript/page-level proof before paper use. | https://buyingonlinebusinesses.com/ep-371-how-stuart-faught-built-and-exited-20-micro-saas-businesses/ |
| Zenith Venture Studio / Medium item | Often within 5-6 years in Claude's source summary | Venture-studio thesis that studio-backed startups can exit faster than conventional startups. | Low-confidence discourse item, not a confirmed firm-level source. Treat as narrative evidence only unless the primary Zenith source is verified. | https://medium.com/the-freedom-startup-journal/beyond-the-mega-exit-how-small-scale-venture-studio-backed-startups-can-deliver-comparable-622efc89ae99 |

## Exclude under strict "not PE/private equity"

| Item | Exit horizon / length | Exit strategy | Reason | Source |
|---|---|---|---|---|
| WebStreet / Empire Flippers Capital | 2-4 years | Acquire online SaaS/e-commerce businesses, operate them, then sell at a premium. | Explicitly framed as a "Micro Private Equity Model." Tech-enabled, but fails no-PE. | https://www.prnewswire.com/news-releases/webstreet-unveils-a-new-investment-thesis-micro-private-equity-model-302189275.html |
| LTV SaaS Fund | 3-5-year term; Fund V liquidated over 2018-2023 in Claude's source summary | Acquire profitable B2B SaaS / Shopify app assets, operate them, then divest. | SaaS acquisition fund that buys/holds/sells software assets. Tech-enabled but PE-like enough to fail a literal no-PE filter. | https://ltv.fund/fund-category/ltv-saas-growth-v/ |
| Edited Capital Fund III | 7-year fund term, with possible extensions | Acquire majority/control positions in small B2B SaaS, grow them, and realize value during the fund term. | Explicitly private equity: "Fund III represents the next evolution in private equity investing." Tech-enabled, but fails no-PE. | https://editedcapital.com/fund-iii/ |
| Matt Williamson - "Grow & Flip" micro-PE | 3-5 years | Buy/grow a SaaS business and target a $25M-$50M exit. | Discourse, not an entity, and explicitly about micro private equity. | https://mattgiustwilliamson.substack.com/p/selling-your-saas-to-micro-private |
| Superscout glossary - Micro-PE | 3-5 years | Apply buyout tactics to small businesses, then exit after the value-creation period. | Discourse/glossary, not an entity, and explicitly private equity. | https://superscout.co/glossary/micro-private-equity |

## Discourse-only / not entity candidates

These can support the narrative that "fast, sub-unicorn liquidity" is a discourse trend, but they should not be counted as confirmed entities.

| Item | Treatment | Source |
|---|---|---|
| Venture Studio Forum - "The Illiquid Index Trap" | Narrative / mechanism evidence, not entity candidate | https://newsletter.venturestudioforum.org/p/the-illiquid-index-trap |
| Startup Chai - "Startups Built to Be Bought" | Narrative evidence | https://www.startupchai.in/p/the-weekend-insight-startups-built-to-be-bought-the-18-month-exit-game |
| Startup Funding Espresso - "3x3 Early Exit Framework" | Narrative framework; not a specific entity | https://www.startupfundingespresso.com/the-3x3-framework-for-predictable-startup-investing/ |
| Romulus Strategy - "Build for the Buyer" | Advisory/content; not a confirmed tech-enabled entity | https://romulusstrategy.substack.com/p/build-for-the-buyer-how-exit-strategy |
| SaaSCity.io - Micro-Exits guide | Narrative/how-to evidence | https://saascity.io/blog/buying-selling-codebases-guide-2026 |
| Surges.co - "12-Month Exit Blueprint" | Narrative/how-to evidence; mixed examples include e-commerce/content as well as tech | https://www.surges.co/guides/12-month-exit-blueprint/ |
| Jake's Insights | Could not reverify the quoted page/claim during this pass; do not count | jakeinsight.com |
| wildwildmoney / buy-startups.com | Could not reverify the cited "hold 18 to 36 months" claim during this pass; buy-startups.com is marketplace/content infrastructure, not an entity | buy-startups.com |
| Acquire.com / Flippa / Empire Flippers marketplace references | Infrastructure/discovery layer, not allocator/operator entity rows | https://acquire.com/ and related marketplaces |

## Recommended replacement language

Replace:

> "43 confirmed entities"

With:

> "Claude surfaced roughly 30 distinct named items after duplicate cleanup. On Codex re-verification, 14 are usable tech-enabled, non-PE firm/operator candidates; 4 require user review; 5 fail a strict no-PE/private-equity filter; and the remainder are discourse or infrastructure, not entity candidates."

## Open questions for user

1. Does "not PE/private equity" exclude **micro-PE** as well as classic institutional PE? I treated it as yes, because the user said not PE/private equity.
2. Should "tech-enabled" be judged at the **program level** for venture studios (Favcy, SquadS), or must every cited portfolio/example company be tech-enabled?
3. For SquadS, does "capital recovery within 4 years" count as in-band liquidity if the same page targets "4X returns within 10 years"?
