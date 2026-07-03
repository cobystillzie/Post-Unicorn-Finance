# Social-Listening Run — Credentialed `/last30days` (2026-06-18)

First pull using the real keys (`.env.local.txt` → `~/.config/last30days/.env`). Archives the run the
protocol (`../docs/02_social_listening_protocol.md`) mandates. Raw saved at
`~/Documents/Last30Days/startup-employee-equity-esop-employee-ownership-value-participation-raw-v3b.md`.

## Run health

- **46 items / 4 live sources:** Reddit 9 threads (3,742 upvotes, 645 comments), TikTok 19 (8,731 views),
  Instagram 5 (21,346 views), Web 13. Window 2026-05-20 → 2026-06-19.
- **X = 0** (Bird search failed — `AUTH_TOKEN` and `CT0` are identical; fix to add the operator/VC voice).
  **YouTube / Hacker News / GitHub / Polymarket = 0** this pass (date-range + a GitHub 422).
- Sources now exposing **engagement metrics** (the gap in the earlier Exa-only read).

## New signal vs the earlier Exa pull

1. **A creator/advocacy layer is actively promoting *employee ownership* — and it's positive.** On TikTok the
   "power of ownership" framing is circulating, including Ownership Works content:
   - *"Imagine showing up to work as a welder, technician, or cafeteria employee… and waking up a millionaire.
     That's the power of ownership."* — @claim_mindset, 2026-06-17 (204 views).
   - *"Why workers should own a piece of the machine they operate… workers become shareholders."*
     #EmployeeOwnership #EconomicJustice — @connorwithhonor, 2026-06-18.
   - *"What if every employee owned a piece of the value they help create? Ownership Works is helping companies
     turn jobs into wealth-building opportunities."* — @tito4794, 2026-06-05 (724 views).
   Caveat: a chunk of the TikTok set is **generic finance-influencer noise** (options explainers, non-English
   posts), not startup-specific — weight the *ownership-advocacy* subset, not the raw count.
2. **Reddit confirms the skeptical employee/practitioner view — fresh and high-engagement:**
   - *"Am I being exploited or just paranoid? Co-founder wants me to build the entire product for 15% equity,
     no salary."* — r/developers, 2026-06-15, **126 comments**; top reply (16 upvotes): *"Run away, he is using
     you… Ideas aren't worth a fucking thing."*
   - *"At what point does startup equity become worth taking seriously?"* — r/jobhunting, 2026-06-11 (mixed
     "take the cash" vs "negotiate options" advice).
   - Notable: **r/indianstartups** surfaced strongly — ESOP discussion is lively in the India startup scene.
3. **Instagram** adds an ESOP-explainer creator layer (startupdaily, peoplematters, sharescart) — educational,
   not sentiment-heavy.

## Read (consistent with the baseline)

The split holds and is now visible *with engagement*: **creators/advocates push ownership as wealth-building
(populist, rising in the culture); practitioners/employees stay wary (dilution, exploitation, "ideas are
worthless").** True *ownership* advocacy is loud on social, but the concrete adoption is still
succession/PE-driven, and startup-employee skepticism about ordinary option grants persists.

## Gaps / next

- **Fix X tokens** (distinct `auth_token` + `ct0`) to add the operator/VC/PE voice layer — the richest missing
  channel for "where is the conversation in PE vs VC."
- Re-run Topics C-E from the protocol individually for depth; re-run monthly to measure the *delta*.

## X-layer (run #2 — X now authenticated, 2026-06-19)

X auth fixed (distinct `auth_token` 40-char / `ct0` 160-char). Pulled **18 X posts + 10 web**.
**ScrapeCreators hit HTTP 402 (credits exhausted)** this pass, so Reddit-backup / TikTok / Instagram returned
0 (they worked in run #1 — top up the ScrapeCreators key to restore them). New X signal (engagement modest —
treat as *presence of conversation*, not virality):

- **SpaceX IPO (Fri June 12, 2026) → ~4,400 employee millionaires** — *"one of the largest corporate wealth
  creation events in history."* (@Intellectualins, 2026-06-13, https://x.com/Intellectualins/status/2065693872664256654;
  @SebastinPatron3, 2026-06-13). Post-IPO planning context: creativeplanning.com, 2026-06-17
  (https://creativeplanning.com/private-wealth-management/spacex-employee-stock-planning/). The concept example
  is now a real, dated liquidity event.
- **Mastercard launched a global ESPP with Morgan Stanley at Work** for *"broad-based employee participation."*
  (@johntoomeyMS, 2026-06-18, https://x.com/johntoomeyMS/status/2067623471522140624) — a public-company
  broad-equity expansion.
- **Rhode Island Senate unanimously passed a bill to create a State Employee Ownership Center.** (@theNCEO,
  2026-06-18, https://x.com/theNCEO/status/2067739827194192326) — state-level, bipartisan policy momentum.
- ESOP-as-retention advocacy from advisors/SMBs (@jfpinsights, 2026-06-18).

**Read:** the X layer reinforces the baseline — value participation is real and accelerating, but the headline
events are **mature/public companies (SpaceX IPO, Mastercard ESPP) + policy (RI center)**, not venture-stage
startups. SpaceX is the liquidity-event archetype, now realized.

_Generated 2026-06-18; updated 2026-06-19 with credentialed X-layer (run #2). Pairs with
`social_listening_2026-06-18.md` (Exa) and `state_of_value_participation_2026-06-18.md`._
