# Fast-Exit Liquidity Lens — Social Listening (2026-06-27)

**Question:** Who is deliberately pursuing a SHORT-HORIZON, time-boxed *"acquire/build → exit quickly"* strategy below unicorn scale — firms/funds/operators **and** the discourse framing it — that fits our liquidity lens (**Nimble** = exit < 6y; **SMV** = exit 7–9y; **excludes** 10y+ unicorn and permanent-hold)?

**Method:** Custom multi-agent workflow (run `wf_dbf78bfa-baf`). 20 finder agents fanned out by angle/source → 102 raw candidates → 88 deduped by firm/domain → 70 adversarially verified. Each verifier **independently re-fetched the source's raw page text (Exa), confirmed the exit-horizon quote was actually on the page, then tried to refute it** on four axes (genuine fast-exit vs. hold-forever / sub-unicorn / tech-enabled / within the 2-year window). Default verdict = REJECTED; "unverifiable" never counted as confirmed. **43 survived; ~30 are distinct** after collapsing near-duplicate finds (Surges ×4, Jake's Insights ×3, Favcy ×3, Yoskovitz ×2, Williamson ×2).

**Personal re-verification (main author, 2026-06-27):** I directly re-fetched the load-bearing pages and string-matched the quotes myself (not just trusting subagents). **Confirmed verbatim on the live page:** Sequel Capital, AscendX, Cocreatd, Edited Capital, and — contrary to the subagent's provenance worry — Napkin Ventures (the 5-year clause *is* in the page body). **Did NOT verify on direct re-fetch:** SquadS Ventures (quote not reproducible via WebFetch + a classification ambiguity) — downgraded below; see §3 and §5.

**Admission bar (liquidity lens — all three):** (1) tech-enabled; (2) a *quotable* stated exit horizon in the Nimble/SMV band; (3) explicit sub-unicorn / anti-power-law signal OR structural sub-unicorn traits. Allocator status **not** required — operators/studios/builders count.

---

## 1. Bottom line

**Yes — a deliberate, time-boxed, sub-unicorn fast-exit strategy is a real and visibly accelerating emerging phenomenon — but it lives almost entirely at the NIMBLE end (under 6 years), not in the SMV (7–9y) band.** The clearest signal is the appearance of firms that put an **explicit anti-"10-year fund" clock in their public-facing marketing** — Sequel Capital ("*We're not a 10-year fund. Our 2-3 year model…*"), WebStreet/Empire Flippers Capital (stated 2–4-year buy-grow-sell), AscendX (12-month-per-venture), Cocreatd (an executed 8-month creation-to-exit) — paired with a wave of **practitioner discourse** (Venture Studio Forum's "Illiquid Index Trap," Ben Yoskovitz / Highline Beta, Matt Williamson's "Grow & Flip" micro-PE) that reframes the venture-studio and micro-PE models around *compressed liquidity* as the headline feature. A notable structural pattern (held with one caveat below): **the SMV 7–9y band came back nearly empty.** Of ~30 distinct confirmed items, only **one** (Edited Capital Fund III, a standard 7-year PE fund term) lands in SMV. *Read this cautiously:* the finder vocabulary ("build-to-sell," "flip," "3-year," "micro-PE") is Nimble-flavored and structurally *under-samples* SMV-profile firms (venture-scale effort → 7–9y sub-unicorn outcome, stated in ordinary VC language), so some of the emptiness is search design, not absence. Still, the signal is directionally real: The innovation is happening *below* 6 years — in (a) **build-to-sell venture studios / company-builders** and (b) **micro-PE / micro-SaaS acquire-grow-sell funds** — while the 7–9y "venture-scale-effort, sub-unicorn-outcome" thesis remains largely a category we name rather than one the market is loudly populating.

---

## 2. Framing themes (the distinct fast-exit narratives observed)

1. **"We are not a 10-year fund" (explicit anti-duration positioning).** Funds/studios market the *short clock itself* as the product, contrasting against the standard VC fund life. Best exemplars: Sequel Capital, FutureFirst, WebStreet.
2. **Build-to-sell venture studios.** Company-builders that design ventures *for acquisition from day zero* on a 1–5-year clock, often using AI to compress the build. Exemplars: Cocreatd, AscendX, Favcy BTS, FirstFounders, The2410, Napkin Ventures; discourse from Highline Beta / Yoskovitz, Venture Studio Forum, Zenith.
3. **Micro-PE / micro-SaaS "acquire → improve → flip."** Buy small profitable software, operate 2–4 years, sell at a premium — "private equity, but small and fast." Exemplars: WebStreet (Empire Flippers Capital), LTV SaaS Fund; discourse from Matt Williamson ("Grow & Flip"), Superscout, wildwildmoney.
4. **The "exit-engineered" indie/solo builder.** A new founder archetype building specifically to flip on micro-acquisition marketplaces (Acquire.com, Flippa, Empire Flippers) in 6–18 months. Exemplars (executed): Teemu Raitaluoto/AIContentfy, Wasp.sh case study, Joshua Tiernan/Tiny Empires, Fizan Muhammad/IntakeGenie; how-to discourse: SaaSCity, Surges, Jake's Insights, buy-startups.com.
5. **"Studio secondary at Series A" liquidity engineering.** A more sophisticated studio-fund thesis: sell a *portion* of the studio's low-cost-basis stake at the portfolio company's Series A (~25 months) for 2–3x, rather than waiting for a terminal exit. Exemplar: Venture Studio Forum "Illiquid Index Trap"; Redbud VC ("nimble VC liquidity advantage").
6. **Compressed-horizon funds with anti-unicorn outcome targets.** Funds explicitly targeting *medium-sized* exits ("several hundred million," "$25–50M," "$50–75M") as a *win*, not a consolation. Exemplars: FutureFirst, Mirai Ventures, Williamson; and the lone SMV case, Edited Capital.

---

## 3. Case studies

> Confidence reflects source quality + how explicit/attributable the horizon is. **Band** is by *total* horizon from founding/entry. ⭐ = strongest evidence of an *executed* (not merely marketed) model.

### TIER 1 — Operating firms / funds (executed or actively-deploying model, explicit horizon)

**⭐ Sequel Capital** — UK · **Nimble** · tech-enabled: Y · **HIGH**
- *Profile:* Minority investor in vertical *agentic* B2B SaaS ($2–10M ARR) selling a 2–3-year path-to-acquisition as the core product.
- *Quote (front-page copy):* "**We're not a 10-year fund. Our 2-3 year model is built for founders ready to scale and exit — not wait.**"
- *Link:* https://www.sequel-capital.com/ · company-site · sub-unicorn: explicit niche/smaller-market, $2–10M ARR.
- *What/why:* The single cleanest "anti-duration" positioning found — the short clock *is* the pitch, on the front page, not buried in an LP deck. *Limits:* young firm; portfolio/track record not yet demonstrated.

**SquadS Ventures** — Latin America · band **ambiguous** · tech-enabled: Y · **LOW (⚠ unverified on direct re-fetch; classification disputed)**
- *Profile:* Company-builder running ~20 concurrent B2B SaaS startups on a shared playbook.
- *Subagent-reported quote (NOT reproduced on my re-fetch):* "*Early Exits Model: Prioritizing early exits, we aim to maximize the chances of capital recovery within 4 years and deliver 4X returns within 10 years. Returns are distributed progressively based on the 100% distribution of exit proceeds.*"
- *Link:* https://squads.ventures/angeles-inversionistas/ · company-site.
- **⚠ Two problems found on author re-check (2026-06-27):** (1) **Unverifiable** — neither https://squads.ventures/ nor the investor page reproduced the quote via WebFetch (truncated/JS-rendered); the homepage states only a *5-year build* horizon ("build a portfolio of 20 B2B SaaS companies over the next 5 years"). (2) **Classification dispute** — "capital recovery within 4 years" + "**4X returns within 10 years**" + "progressive distribution" reads at least as plausibly as **early DPI on a ~10-year hold** (the *excluded* "liquidity-without-exit" pattern) as it does a genuine 4-year fast exit. **Do not count SquadS as a confirmed Nimble fast-exit firm** until the investor page is read directly and the exit-vs-early-distribution question is settled.

**⭐ Cocreatd** — UK · **Nimble** · tech-enabled: Y · **HIGH**
- *Profile:* Self-funded venture studio co-founding day-zero startups; *proved* the build-to-exit thesis in year one.
- *Quote:* "**Notably, Cocreatd achieved a creation-to-exit timeline of just eight months for its System7 acquisition, and took its security venture from concept to LSE listing in six months.**"
- *Link:* https://startupsmagazine.co.uk/article-cocreatd-achieves-ps100m-portfolio-value-first-year · news · sub-unicorn: 95% self-funded, 7-figure exit, "not pursuing unicorn valuations through massive capital deployment."
- *What/why:* Strongest *executed* counter-evidence that fast exits require unicorn-scale capital — an 8-month exit and a 6-month-to-LSE listing in the studio's first calendar year.

**⭐ AscendX Ventures AG** — Switzerland · **Nimble** · tech-enabled: Y · **HIGH**
- *Profile:* AI-native studio that builds and *auctions* turnkey digital businesses; ~12-month exit target per venture.
- *Quote:* "**We acquire, build, and exit — targeting full returns within 12 months.**"
- *Link:* https://ascendx.ventures/ · company-site · sub-unicorn: sells on a micro-business marketplace; explicitly contrasts traditional VC.
- *What/why:* The most extreme clock in the dataset — a stated 12-month per-venture exit, two ventures already exited, agentic-OS-driven operations. *Limits:* very small/young; marketplace-flip flavor.

**⭐ Favcy Build-to-Sell (BTS)** — India · **Nimble** · tech-enabled: mostly Y (see limits) · **HIGH** (company-site + 2 independent news corroborations)
- *Profile:* India venture builder co-building startups from idea to acquisition on a 36–48-month clock; markets itself as India's first build-to-sell studio.
- *Quote (company-site):* "**We co-build these ventures with entrepreneurs in residence (EIRs) from the ground up to exit via acquisition over a 36-48 months time period.**" Corroborated in press: "Favcy strategically designs and builds startups… priming them for *acquisitions within 36-48 months*."
- *Link:* https://www.favcybts.com/btsfoundertribe (+ https://indianstartupnews.com/funding/favcy-venture-builders-raises-rs-1-8-crore-6900251) · sub-unicorn: Cohort-1 raised only ~Rs 1.8 cr (~$215K); explicit anti-unicorn thesis.
- *What/why:* Documented completed exits cited (TellerSpot SaaS ~30% IRR in 12 mo; InstaClaus fintech ~400% IRR in 11 mo). *Limits:* Cohort-1's three businesses skew non-tech (sweets, blue-collar services, wedding venues) though later cohort names fintech — treat "tech-enabled" as program-level, not blanket.

**WebStreet (Empire Flippers Capital)** — US · **Nimble** · tech-enabled: Y · **HIGH**
- *Profile:* Micro-PE fund acquiring online SaaS/e-commerce, operating, then selling within a stated 2–4-year window for accredited investors.
- *Quote:* "**They target exits within a two to four-year timeframe, aiming to sell at a premium to realize significant returns.**"
- *Link:* https://www.prnewswire.com/news-releases/webstreet-unveils-a-new-investment-thesis-micro-private-equity-model-302189275.html · news · sub-unicorn: 4–6 sub-$5M online businesses per fund; explicit micro-PE-not-VC.
- *What/why:* A *passive fund* (not a founder story) with an investor-facing sub-5-year exit commitment. Note: distinct from the Empire Flippers *marketplace* (which is excluded as ecosystem in the atlas) — this is the deploying-capital arm.

**LTV SaaS Fund** — North America · **Nimble** · tech-enabled: Y · **MED–HIGH**
- *Profile:* Micro-SaaS acquisition fund family (Funds V–VIII) buying profitable B2B SaaS / Shopify apps and exiting in 3–5 years.
- *Quote:* "**LTV SaaS Fund V seeks medium-term investment opportunities, with a return rate of approximately 174% over a 3-5 year term.**"
- *Link:* https://ltv.fund/fund-category/ltv-saas-growth-v/ · company-site · sub-unicorn: individual Shopify-app scale; $MM AUM.
- *What/why:* *Proven* clean exits — Fund V fully liquidated 2018–2023 (540% gross); Fund VI divested a brand at 461% over a 3-year hold. A real fast-exit operator, not hold-forever.

**FutureFirst** — Israel · **Nimble** (borderline → SMV) · tech-enabled: Y · **HIGH**
- *Profile:* $50M Vertical-AI seed fund targeting *medium-sized* exits a few years post-Series A.
- *Quote (GP, in Calcalist):* "**A company that is sold for several hundred million dollars after two or three years is a great outcome for a fund like ours.**"
- *Link:* https://www.calcalistech.com/ctechnews/article/hy9uxu3ubx · news · sub-unicorn: "exits currently considered medium-sized," $50M fund, $1.5M checks.
- *What/why:* Clean attributable GP quote rejecting unicorn-scale as the goal. *Band note:* 2–3y *post-Series-A* ≈ 4–6y from seed — sits on the Nimble/SMV boundary; flagged.

**The2410** — Estonia / Germany · **Nimble** · tech-enabled: Y · **MED**
- *Profile:* Build-to-sell micro-SaaS operator taking investor capital to build → grow → sell on a 24–48-month cycle.
- *Quote:* "**Most projects run for 24-48 months before exit, but selling isn't mandatory - if there's strong upside, we continue scaling.**"
- *Link:* https://2410.ee/en/service/invest-in-saas · company-site · sub-unicorn: explicit €150K–€450K per-asset exit range (nano-scale).
- *What/why:* Plainly states building assets *for acquisition* from day one. *Limits:* tiny scale; "selling isn't mandatory" softens the clock slightly.

**FirstFounders (F2)** — Nigeria · **Nimble** · tech-enabled: Y · **MED**
- *Profile:* AI-first venture studio co-building FinTech/Consumer/Entertainment ventures, targeting acquisition within 36 months.
- *Quote:* "**The goal is not just to grow companies, but to get them acquired within 36 months.**"
- *Link:* https://thecondia.com/partners/firstfounders-africa-venture-studio-startup/ · news · sub-unicorn: ~$7.5M target fund, small tickets, 50% IRR / 6.5x MOIC targets.
- *What/why:* Rare African build-to-sell studio with a formal IP-to-founders-at-exit structure; adds geographic diversity.

**Napkin Ventures** — US (Georgia) · **Nimble** · tech-enabled: Y · **MED→HIGH** (provenance re-checked OK)
- *Profile:* B2B SaaS venture studio co-building with executives on a ~5-year exit horizon, targeting $20M+ valuations at Series-A readiness.
- *Quote:* "**Napkin Ventures will exit the primary management role of these engagements within 5 years by either raising additional capital from a larger preferred investor, the sale of the company or a company buyback of Napkin Ventures' interest.**"
- *Link:* https://www.napkinventures.fund/ · company-site · sub-unicorn: $2–5M ARR / $20M+ target exit; motto "not every company will be a $1B unicorn."
- *What/why:* Founded Oct-2024, live page. **Provenance re-checked (2026-06-27):** an earlier verifier worried the 5-year clause wasn't on the live page; on my direct WebFetch the clause *is* present in the page body (plus "We work toward a ~5-year horizon"). Quote confirmed — flag relaxed. It is body copy, not a hero-banner headline.

### TIER 1b — Named operating funds whose best evidence is a self-published essay (firm-adjacent)

**Mirai Ventures** — **Nimble** · tech-enabled: Y · **MED** — "**By focusing on ventures that can achieve strategic exits within 24 to 36 months, we maximize IRR for our Limited Partners, capitalizing on the current 'corporate FOMO'…**" (https://miraiventures.substack.com/p/how-mirai-ventures-delivers-superior). Tightest stated fund thesis (sub-3-year). *Limit:* evidence is the fund's own Substack (self-published marketing).

**Redbud VC** — **Nimble** · tech-enabled: Y · **MED** — "**Redbud VC had a material exit in two years, selling to a Series A investor**" (https://redbud.beehiiv.com/p/liquid-future-nimble-vcs-have-a-liquidity-advantage). Named operating VC articulating the "nimble VC liquidity advantage" with a concrete 2-year example. *Limit:* single self-published essay.

**Highline Beta / Ben Yoskovitz** — Canada · **Nimble** · tech-enabled: Y · **HIGH** — operating studio + practitioner: "**If a portfolio company sells for a modest multiple within three to five years, those larger ownership positions translate into meaningful cash returns and IRR.**" (https://www.highlinebeta.com/blog/why-exits-define-studio-success) and Yoskovitz's "**…cash on cash returns quickly (say within a few years) versus the standard (7-10+ years)…**" (https://www.focusedchaos.co/p/venture-studios-need-to-focus-on-exits). Real studio *and* category-shaping voice.

### TIER 1c — The lone SMV (7–9y) case

**⭐ Edited Capital Fund III** — US · **SMV** · tech-enabled: Y · **MED** — $150M small-tech buyout fund acquiring B2B SaaS at $3M+ ARR. *Quote:* "**Fund Term: 7 years (with possible extensions)**" (https://editedcapital.com/fund-iii/); a warehoused deal cites a "3-4 years" MOIC-realization statement; Funds I/II deployed "3–5x faster than traditional PE." Sub-unicorn: explicitly targets companies "too small for mega funds." *Why it matters:* the **only** confirmed firm in the SMV band — and even here the 7-year term is a *standard PE structure*, not a distinctively articulated "fast, sub-unicorn" thesis. This is the empirical core of the asymmetry finding.

### TIER 2 — Practitioner discourse with concrete numbers (the strategy being theorized)

- **Venture Studio Forum — "The Illiquid Index Trap" (Matthew Burris, Apr-2026, Substack)** · Nimble · MED — "**…studio-built companies secure Series A funding in approximately 25 months on average… A studio running annual cohorts could see its entire portfolio approaching Series A milestones by year five, compared to traditional VC where the median unicorn has been held for nine-plus years…**"; sub-unicorn proof: "**even modest exits of $50-75 million deliver top-quartile returns, eliminating the 'unicorn-or-bust' dependency…**" (https://newsletter.venturestudioforum.org/p/the-illiquid-index-trap). The most rigorous articulation of the studio-secondary liquidity mechanism.
- **Matt Williamson — "Grow & Flip" micro-PE** · Nimble · HIGH — "**Aiming for a $25M–$50M exit in 3–5 years.**" (https://mattgiustwilliamson.substack.com/p/selling-your-saas-to-micro-private). Names a taxonomy and a sub-unicorn target.
- **Startup Chai — "Startups Built to Be Bought: The 18-Month Exit Game" (India)** · Nimble · MED — "**The result is a new founder archetype: the exit-engineered entrepreneur, building specifically for acquisition, often within 18 to 36 months.**" (https://www.startupchai.in/p/the-weekend-insight-startups-built-to-be-bought-the-18-month-exit-game).
- **Startup Funding Espresso — "3×3 Early Exit Framework"** · Nimble · MED — "**Traditional venture investing assumes holding periods of 8-12 years. The 3-3 Framework instead evaluates whether a company can reach meaningful de-risking or liquidity within 36 months.**" (https://www.startupfundingespresso.com/the-3x3-framework-for-predictable-startup-investing/).
- **Romulus Strategy — "Build for the Buyer"** · Nimble · MED — "**If you plan to exit in five years, your strategy today should reflect that. You're not just building a great company. You're building a great asset.**" (https://romulusstrategy.substack.com/p/build-for-the-buyer-how-exit-strategy).

### TIER 3 — "Flip culture" operator how-tos & executed indie exits (the meme mainstreaming)

*Weaker as authority (content-marketing/how-to), but collectively strong evidence the strategy is going mainstream; several are real executed exits.*

- **Teemu Raitaluoto / AIContentfy** (executed) · ~2y · HIGH — "**From the very beginning, he built with an exit in mind. Two years later… scaled to $1M ARR and… sold it in a clean, all-cash transaction on Acquire.com.**" (https://blog.acquire.com/scaling-ai-content-to-1m-arr-and-a-successful-exit/).
- **Wasp.sh case study — Max's AI Etsy generator** (executed) · 5 mo · MED — "**…ultimately selling his app in 5 months total.**" (https://wasp.sh/blog/2024/07/03/building-selling-saas-in-5-months).
- **Joshua Tiernan / Tiny Empires** (executed, serial) · 1–3y · MED — "**It seems my business model is building and selling micro-businesses.**" (five acquisitions) (indiehackers.com).
- **Fizan Muhammad / IntakeGenie** (executed, extreme) · ~2 wks listing-to-close · MED — "**…the fastest one was IntakeGenie… from listing to… the funds transferring… it took two weeks.**" (Acquire.com YouTube).
- **Stuart Faught — 20 micro-SaaS exits** · MED — "**Known for his rapid exit strategy, Stuart closes most deals in 30-45 days…**" (buyingonlinebusinesses.com podcast Ep 371).
- **SaaSCity.io — Developer Guide to Micro-Exits (2026)** · HIGH-as-discourse — "**The ideal exit window typically occurs 6-18 months after achieving initial traction…**" (https://saascity.io/blog/buying-selling-codebases-guide-2026).
- **Surges.co — "12-Month Exit Blueprint"** · HIGH-as-discourse — "**With platforms like Acquire, Flippa, and Empire Flippers, founders can now design, grow, and exit startups intentionally, sometimes even in under 12 months.**" (https://www.surges.co/guides/12-month-exit-blueprint/).
- **Jake's Insights — Micro-SaaS flip breakdown** · MED — "**A realistic build-to-flip timeline is 6-14 months from first line of code to closed sale.**" (jakeinsight.com).
- **Superscout glossary — Micro-PE** · MED — "**Micro-PE applies classic buy-out strategies… exit three to five years later — but targets deal sizes too small for traditional funds.**" (superscout.co/glossary/micro-private-equity).
- **wildwildmoney / buy-startups.com** · MED — "hold 18 to 36 months" framing of micro-SaaS portfolios as flip-or-annuity.
- **Zenith Venture Studio** · LOW — "**studio-built startups tend to exit roughly 31% faster — often within 5-6 years.**" (Medium).

---

## 4. Cut by the 2-year cap or by band (transparency)

**Out-of-window (dated before 2024-06-27):**
- **Launchbay Capital** — quote/horizon real & sub-unicorn, but source is a dated press release (London, Jan 23 2024).
- **MicroAngel Fund** — real, but dated post (published 2024-03-07).

**Real fast-exit + sub-unicorn but NOT tech-enabled (out of *our* lens, not out of the world):** — *these show the phenomenon is even larger if you drop the tech filter:*
- **Greg Geronemus — "Buy Well, Exit Better"** ($67.5M, ~4-year exit) — bricks-and-mortar.
- **Andy Rougeot / RG Maintenance** (SBA acquisition→exit) — blue-collar trades.
- **Yan Vinarskiy / Floor Guard** (independent sponsor) — epoxy-coatings manufacturer.
- **Novastone Capital Advisors / Formeds exit** (real verbatim <-5y horizon) — non-tech.

**Wrong model / not sub-unicorn / not a fast *exit*:**
- **FLEX Capital** — explicit unicorn/IPO-scale ambition.
- **REXX Studio** — own thesis page is not sub-unicorn.
- **AppHub (PSG-backed)** — PE roll-up, no quotable exit horizon.
- **Practical VC — PVC-3 "Halftime Fund"** — secondaries fund (faster DPI on the *same* unicorn/IPO exposure), not a sub-unicorn fast-exit builder.
- **RevUp Capital — Athena Growth Fund** — quote is a fund-life + revenue-share schedule, not an exit horizon.
- **Noosa Labs** — "5–7 years" is a $20M-ARR *growth* target, not an exit.
- **Summit Studio Capital / Sandbox Studios** — figures are distribution/return-of-capital schedules, not intentional exit horizons.

**Failed the quote gate (fast-exit vibe, no quotable in-band horizon on the page):** Backswing Ventures (Fund II), Lotus Venture, CT Acquisitions (also unfetchable), The Business Inquirer, and several AI-acquihire essays (Heavybit "Acqui-Hires in the Age of AI," Harbor Ridge "Rise of AI Acquihires," "What's Driving the Acquihire Battleground," "Vibe-Coding Micro-Flip Factory"). *Note:* the **AI-acquihire** theme is clearly emerging chatter but kept failing on a *quotable exit horizon* — worth a dedicated follow-up.

**Generic advisory (real horizons, but not tech-specific & not an executed model):** Buzzacott M&A ("5–8 year" hold-then-sell), IBBA search-fund insight ("5–7yr"), CFA Institute search-fund piece ("four- to seven-years," borderline band, LOW).

---

## 5. Caveats (binding)

- **Count discipline:** 43 "confirmed" collapses to **~30 distinct** items after de-duplicating near-identical finds. Do **not** cite 43. Of the ~30, ~11 are operating *firms/funds* with a verified explicit horizon (SquadS excluded as unverified); the rest are discourse (some self-published).
- **The SMV band came back near-empty — a real signal, but partly search-design.** Only Edited Capital (7yr PE term) qualified, and even that is a standard PE structure rather than a distinctively-articulated sub-unicorn-fast thesis. The deliberate fast-exit innovation we *did* find is concentrated **below 6 years (Nimble)**, in build-to-sell studios and micro-PE/micro-SaaS flips. **Caveat:** the finder vocabulary was Nimble-flavored and structurally under-samples SMV-language firms (venture-scale effort → 7–9y sub-unicorn outcome, in ordinary VC terms), so some of the emptiness is the query design, not the market. An **SMV-specific sweep** is the right next step before treating "SMV is empty" as settled. Several firms (FutureFirst) straddle the Nimble/SMV boundary depending on whether you count from seed or from Series A.
- **Self-published vs. executed:** Tier-1b (Mirai, Redbud) and most of Tier 2–3 are *marketing/discourse*, not audited track records. The strongest *executed* evidence is Cocreatd, LTV SaaS Fund, AscendX, Favcy, and the indie exits (Teemu, Wasp.sh, Tiernan, IntakeGenie). Treat marketed horizons as intent, not outcome.
- **Author-verified vs. subagent-reported:** the five load-bearing quotes (Sequel, AscendX, Cocreatd, Edited Capital, Napkin) were re-fetched and string-matched by the author on 2026-06-27. **SquadS is the one downgrade:** its quote did not reproduce on direct re-fetch and its "4yr recovery / 4X in 10yr" framing may be early-DPI-on-a-long-hold (excluded), so it is held as unverified/ambiguous — do not count it. Everything else still rests on subagent re-fetches (independent, but not author-re-checked); spot-check before any external/paper use.
- **Tech-enabled filter is doing heavy lifting.** A whole parallel universe of *non-tech* SMB ETA / independent-sponsor fast exits (Geronemus, RG Maintenance, Floor Guard, Novastone) is real and in-band but excluded by our lens. If the thesis ever broadens beyond tech-enabled, the population multiplies.
- **Marketplace adjacency:** Acquire.com / Flippa / Empire Flippers are the *infrastructure* enabling the indie flip wave (discovery-only / ecosystem, not allocators). WebStreet is the *fund* arm of Empire Flippers and does count.
- **SMV/Nimble split is provisional** per project taxonomy (pending Ethan reconciliation; see `CLAUDE.md`). Bands here were assigned strictly by the prompt's horizon thresholds (Nimble <6y / SMV 7–9y), with 6–7y treated as borderline.
- **Searched-but-thin:** explicit *7–9-year* sub-unicorn theses; AI-acquihire firms with a *quotable* exit clock; large/institutional (not micro) build-to-sell vehicles. These returned little — likely genuinely sparse, not a search miss, but a targeted second pass could confirm.

---

## 6. Plain English

**What we looked for:** people who *deliberately* build or buy a tech company in order to **sell it fast** — within about 1–6 years (we call that "Nimble") or 7–9 years ("SMV") — instead of the classic Silicon Valley plan of spending 10+ years trying to build a billion-dollar "unicorn." We only counted cases where the company itself *said*, in its own words on a real web page, how fast it plans to sell, and where the target is clearly *smaller than a unicorn*.

**What we found:** This is a real, growing trend — but almost all of it is **fast** (under 6 years), not medium (7–9 years). Two engines drive it:
1. **"Build-to-sell" studios** — outfits that *create* startups specifically to sell them on a short clock. Some are extreme: AscendX (Switzerland) aims to sell each venture in **12 months**; Cocreatd (UK) actually sold a company **8 months** after creating it. Favcy (India) and FirstFounders (Nigeria) build startups aiming for a buyer in **3 years**.
2. **"Micro private equity" / "micro-SaaS flipping"** — investors who *buy* small, profitable software businesses, improve them, and **resell in 2–5 years** (WebStreet, LTV SaaS Fund), plus a wave of solo founders who build a small app and sell it on marketplaces like Acquire.com in well under two years.

**The clearest single signal:** firms now *advertise the short timeline as the selling point*. Sequel Capital (UK) literally says on its homepage: *"We're not a 10-year fund. Our 2-3 year model is built for founders ready to scale and exit — not wait."* That kind of statement — rejecting the slow VC model out loud — is the heart of the trend.

**The big surprise:** the **7–9-year ("SMV") band is almost empty.** We found only one fund there (Edited Capital, and only because a 7-year fund term is normal in private equity). So the genuinely *new* behavior is happening in the **under-6-year** zone.

**Jargon used above, defined:**
- **Exit / liquidity:** turning an ownership stake into cash — by selling the company, selling your shares, or going public.
- **Unicorn:** a startup worth $1 billion+. The "power law" is the VC belief that one giant winner pays for many failures — the thing these firms reject.
- **Holdco / venture studio / company-builder:** an organization that *creates or owns* multiple companies. "Build-to-sell" = builds them to sell; "build-to-keep / permanent-hold" = never sells (the opposite, and out of scope here).
- **Micro-PE:** private equity (buy → improve → sell) but with very small companies.
- **ETA / search fund:** "Entrepreneurship Through Acquisition" — buying an existing small business to run instead of founding one.
- **ARR / MRR:** annual / monthly recurring revenue (subscription income).
- **DPI:** "distributions to paid-in" — how much cash a fund has actually returned to its investors (the real measure of whether money came back).
- **Secondary:** selling your shares to another investor before the company itself exits — a way to get cash out early.
- **IRR / MOIC:** rate of return / multiple on invested capital — two standard ways to measure investment performance.

---

*Generated from workflow `wf_dbf78bfa-baf` — 20-finder fan-out → dedup → 70 adversarial verifications. Raw confirmed/rejected digests: session scratchpad `confirmed_digest.json` / `rejected_digest.json`. Verbatim quotes were independently re-fetched from source pages during verification.*
