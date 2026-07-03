# Social-Listening Pull — Startup Equity / Employee Ownership Conversation (2026-06-18)

The "comprehensive social listening" leg of the baseline (Ethan's directive: where is the conversation on
value participation, and is it a trend?). **Read the method note first — it changes how to weight this.**

## 0. Method note (binding)

- The native `/last30days` engine **returned no usable data in this environment**: Reddit answered HTTP 403 on
  every subreddit (startups, ExperiencedDevs, cscareerquestions, fatFIRE, venturecapital), X was not
  authenticated, and Hacker News / YouTube / Polymarket returned nothing on-topic. The only items it pulled
  were 3 unrelated GitHub digests (noise). So the engine added zero signal — **not reported as findings.**
- This read is therefore built from **Exa web search/fetch** over the open conversation (Hacker News threads,
  operator/Substack essays, LinkedIn posts, and analyst/press write-ups) — every item below has a real URL and
  a verbatim quote actually seen on the page. One Exa query hit the free-tier rate limit; HN sentiment was
  already saturated by then.
- Engagement *counts* (upvotes/likes) are mostly **not observable** through this path — treat the sentiment as
  directional/qualitative, not as a quantified volume metric. That gap is real; see §4.

## 1. Employee sentiment on conventional startup equity — deeply skeptical, persistent

The rank-and-file view of ordinary option grants is overwhelmingly negative, and it is **long-standing, not
new** (threads span 2018→2026 with the same refrain):

- **"That's normal and is why I count startup stock and options as $0."** — Hacker News (item 26098911). Same
  thread: *"startup hiring managers using worthless options as a negotiating tactic should be prosecuted for
  securities fraud."* (https://news.ycombinator.com/item?id=26098911)
- **"I find this type of compensation utterly worthless and frankly insulting to the workforce… there are a
  lot more ways for your options to be worth nothing than there are for you to become rich from them."** — HN
  (item 43677084), 2025. (https://news.ycombinator.com/item?id=43677084)
- **"Equity in a startup for an employee is worthless."** — HN (item 16150463). The same thread carries the
  steel-man rebuttal: *"Startup equity is likely worth nothing, but there's a small chance it's worth an
  extraordinary amount. That's not 'worthless.'"* — i.e. the debate is "EV-negative lottery ticket" vs "tail
  bet," not "good vs bad." (https://news.ycombinator.com/item?id=16150463)
- **"Early engineers have all the risk… but little upside."** — HN (item 40657540), on AMT, the 90-day
  exercise window, and 7-10 year illiquidity. (https://news.ycombinator.com/item?id=40657540)
- **Operator essay, recent and sharp:** Gal Ratner, "Stock Options Are Not a Salary. Stop Pretending They
  Are." (2026-04-27) — *"That is not a compensation strategy. That is a transfer of wealth from the people
  doing the work to the people structuring the deal."* Invokes Dan Luu ("if options were really worth that,
  the company could just pay cash") and Steve Blank ("the bargain has gotten worse").
  (https://galratner.substack.com/p/stock-options-are-not-a-salary-stop)
- **LinkedIn (71 comments):** Illai Gescheit, 2026-02-04 — options are *"more of a 'storytelling' tool to keep
  employees engaged"*; cites *"70%+ of startup employees never exercise."*
  (https://www.linkedin.com/posts/illaigescheit_most-people-who-join-startups-as-employees-activity-7424859308795793409-ChHO)

**Counter-signal (do not omit):** AngelList 2024 — **63% of under-30 employees said they'd take a lower
salary for more equity, up from 41% in 2021.** So appetite for equity-as-upside is *rising* among the young
even as trust in the instrument's mechanics is low. (per adplist, 2025-04: https://adplist.substack.com/p/equity-vs-salary-in-2025-what-should)

## 2. Employee OWNERSHIP (the real baseline question) — a genuine, accelerating trend, but NOT in startups

The conversation on true employee ownership is louder and more concrete than the startup-equity gripes — and
it is consistently framed as **business succession + mature/PE companies**, not venture-stage startups:

- **"Employee Ownership Plans Are Becoming Mainstream" (DOL/EBSA report)** — *"a 28% increase in the number of
  leveraged standalone ESOPs,"* EOTs and worker co-ops "taking hold"; co-ops up ~3.5x in the decade to 2023
  (~820, ~13,520 workers). ESOPs are used "as a succession tool by owners of mid-size privately held
  companies and as an employee retirement savings option offered by publicly held corporations." (rethinking65,
  2026-03-05: https://rethinking65.com/employee-ownership-plans-are-becoming-mainstream-dol/)
- **Aspen Institute, "What We Know from Recent Research (2026)"** — *"approximately 18% of employees, or about
  25 million workers… have some form of ownership stake,"* ~11M active in ESOPs; ~900-1,000 worker co-ops.
  (2026-05-29: https://www.aspeninstitute.org/publications/employee-ownership-and-esops-what-we-know-from-recent-research-2026/)
- **"Employee Ownership's Quiet Takeoff: A Moat or a Wealth Transfer?"** — since 2022, *">$1.3 billion has
  been distributed to 41,000 non-executive employees, with projections… exceed $20 billion in the coming
  decade"*; UN declared 2025 the International Year of Cooperatives. Frames the open risk: benefits may stay
  concentrated among existing employees (a wealth *transfer*, not new access). (AInvest, 2026-04-07:
  https://www.ainvest.com/news/employee-ownership-quiet-takeoff-moat-wealth-transfer-2604/)
- **"Financing Employee Ownership: A Growing Trend"** — the club of firms financing EO transitions *"has grown
  from a small handful of funds to a roster of more than three dozen active managers."* Transform Finance: ~$1T
  needed; Rutgers: ~140,000 businesses / 33M employees / $25T revenue *eligible* to convert; Apis & Heritage
  closed **$85M** on Fund II ($250M target, goal 3,000 new worker-owners). Pete Stavros: *"The problem with
  employee ownership is it's really hard… It takes years."* (ImpactAlpha, 2025-08-06:
  https://stg.impactalpha.com/fund-managers-step-up-to-finance-employee-ownership-as-proponents-debate-how-much-wealth-creation-is-enough/)
- **Concrete fresh example:** P. Terry's (Austin burger chain, ~1,800 staff) announced an **Employee Ownership
  Trust** with profit-sharing rising 5%→20%, advised by **Common Trust** — explicitly chosen as an
  alternative to "sell to private equity." (Austin Statesman, 2026-06-09:
  https://www.statesman.com/business/article/p-terrys-employee-ownership-profit-sharing-22297734.php)
- Institutional endorsement: **Norges Bank** (world's largest SWF) backing employee share ownership; **Walmart**
  expanding employee equity (per Miami Select / WDC, 2026-05-23).

**Read:** employee ownership IS having a real moment — but the engine is *retiring business-owner succession*
(the "silver tsunami"), PE shared-ownership (Ownership Works/KKR), and policy (bipartisan bills, state
centers), NOT venture-stage startups adopting it. Confirms the baseline: it is a mature-company / succession /
PE story.

## 3. Liquidity — the clearest and fastest-rising trend (fresher numbers than the baseline report)

- **Carta / Peter Walker:** total tender-offer transaction value bottomed at **$3.8B (2023)** and surged to
  **$16.5B (2025)**, nearly the 2021 peak; **16,538 employees** participated in tenders in 2025 (a record);
  7,222 sellers in Q4 2025 alone. (Topline/Carta, 2026-04-07:
  https://topline.beehiiv.com/p/3-8b-to-16-5b-in-2-years-employee-liquidity-is-having-its-moment)
- **PitchBook (via Earlyasset, 2026-06-15):** US startup tender offers reached **~$18.4B in 2025**; IPO
  activity in 2026 running **~55% below** prior year; OpenAI's Oct-2025 secondary let **600+ current/former
  employees sell ~$6.6B at a $500B valuation, some cashing out up to $30M each** — and *"the same period that
  produced record cash-outs also produced record holdouts"* (Anthropic employees electing to hold).
  (https://earlyasset.com/research/ai-employee-equity-private-market-liquidity/)
- **Fabrica Ventures (2026-06-14):** *">$100B of private-company shares changed hands through secondary
  transactions in the US"* in 2025; tender volume hit **$10.1B by May 26, 2026**, already above each full year
  2022-2025. (https://fabricaventures.com/tender-offers-the-new-engine-of-venture-liquidity/)
- **TechCrunch (2026-02-05):** *"Secondary sales shift from founder windfalls to employee-retention tools"* —
  Clay, Linear, ElevenLabs ran employee-wide tenders; the ZIRP-era founder-only payouts are now "frowned
  upon." (https://techcrunch.com/2026/02/05/secondary-sales-shift-from-founder-windfalls-to-employee-retention-tools/)
- **The tender is becoming a recurring *compensation instrument*** (multiple tenders at OpenAI, Stripe,
  Anthropic), not a one-time pre-IPO event — and startups now compete on it against OpenAI/SpaceX, which run
  regular tenders. (augment-pulse, 2026-05-28: https://augment-pulse.beehiiv.com/p/openai-s-6-6b-tender-comp-not-cash-out)

**SpaceX note (Ethan's example):** SpaceX/OpenAI recurring employee tenders are exactly this mechanism — broad
employee *liquidity*, at mature private companies. It is the model the conversation is converging on, and it is
about cashing out existing equity, not about new broad *ownership*.

## 4. What this adds to the baseline + caveats

- **Reinforces all three baseline movements** with fresher, dated 2026 sourcing: (1) conventional startup
  equity distrusted; (2) true employee ownership rising but as succession/PE/policy, not startups; (3)
  liquidity the clearest rising trend.
- **Sharpens one number:** full-year 2025 tender volume **$16.5B (Carta) / ~$18.4B (PitchBook)** and 2025
  secondaries **>$100B** are stronger headline figures than the report's Q2-YoY tender stat — usable in the brief.
- **Caveats:** native social-platform engagement metrics were **not captured** (Reddit 403 / no X auth), so
  "loudest/most-engaged" claims remain qualitative. The AngelList "63% of under-30" counter-signal is a single
  secondary cite. Several items are press/analyst write-ups, not primary filings — cite as attributed.

_Generated 2026-06-18. Social leg of the state-of-value-participation baseline; pairs with
`state_of_value_participation_2026-06-18.md` and the VC-dimension workflow output._
