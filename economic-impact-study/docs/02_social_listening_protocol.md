# 02 — Social-Listening Protocol (Ethan's directive, operationalized)

The repeatable protocol for the baseline Ethan asked for. Pairs with the methodology
(`01_comparison_methodology.md`, parked) and feeds the dated findings under `../analysis/`.

## Objective (Ethan, verbatim intent)

> Before comparing funds, first **establish the state of value participation across ALL startups** — is
> meaningful employee value participation (ESOPs / employee participation / broad equity / profit-share)
> **becoming a trend**? And **where is the conversation in new PE and VC**?

SpaceX is a clean example of the *concept* (broad employee liquidity) but it is **not a startup** — the
question is whether *actual startups* are adopting this and whether it is rising.

## Scope of "value participation" (what we listen for)

ESOP ownership *plans* vs startup option *pools* (keep them distinct), broad/all-employee equity,
profit-sharing, phantom equity, RSUs, **EOTs**, worker co-ops, steward-ownership, and the liquidity side
(tender offers, secondaries) that lets workers realize value.

## Platforms (now credentialed via `.env.local.txt` → `~/.config/last30days/.env`)

| Platform | Role | Status |
|----------|------|--------|
| Reddit + subreddits | primary rank-and-file discussion | public JSON 403s here; **ScrapeCreators backup now keyed** |
| Hacker News | engineer sentiment (open) | ✅ works |
| X / Twitter | operator + VC/PE voices | ⚠️ **blocked** — `AUTH_TOKEN` and `CT0` are identical; need the two *distinct* cookies |
| YouTube | explainers / reactions | ✅ works |
| TikTok + Instagram | creator / influencer signal | ✅ **unlocked** (ScrapeCreators key) |
| Polymarket | any relevant prediction markets | ✅ works (rarely relevant here) |
| Brave web | LinkedIn posts, Substack/blogs, news grounding | ✅ **keyed** (`--auto-resolve` / grounding) |

## Target communities & voices (verify each before quoting)

- **Subreddits:** startups, ExperiencedDevs, cscareerquestions, fatFIRE, venturecapital,
  financialindependence, Entrepreneur, smallbusiness (succession/EOT), employeeownership/ESOP (if active).
- **Voices/handles to watch:** Carta / Peter Walker, Ownership Works, Pete Stavros, Bijan Sabet (Spark),
  Hunter Walk (Homebrew), Fred Wilson (USV); operator Substacks (Gal Ratner, The Fund CFO); institutions
  Aspen FSP, Rutgers (Kruse/Blasi), NCEO.
- **Blogs/benchmarks:** Carta Data, Index Ventures "Rewarding Talent," Ravio comp trends, ImpactAlpha.

## Discipline (binding — same rules as the atlas)

- Never fabricate a quote or figure; **every claim needs a real URL + a verbatim quote actually seen.**
- Report **rising / flat / unclear** honestly. Always separate *ownership plan* from *option pool*.
- Social platforms are **discovery**; verify via primary sources; **do not bypass site logins/protections.**
- Capture engagement metrics (upvotes/likes/views) where the credentialed run exposes them.

## The prompts (run each via the `/last30days` engine, `--emit=compact`, 30-day window)

| # | Topic | `/last30days` prompt | Lead sources |
|---|-------|----------------------|--------------|
| A | Employee sentiment on startup equity | `startup employee stock options equity worth it` | Reddit, HN, X |
| B | Employee-ownership trend (ESOP/EOT/co-op) | `employee ownership ESOP EOT worker cooperative trend` | Reddit, web, YouTube |
| C | Liquidity (tenders/secondaries) | `startup employee tender offer secondary liquidity` | X, Reddit, web |
| D | PE-vs-VC conversation on value sharing | `employee ownership private equity Ownership Works versus venture capital` | web, X, Reddit |
| E | Operator "keep your equity / no unicorn" thread | `you don't need a unicorn keep your equity startup founder` | X, Substack, HN |

Each run resolves subreddits + handles (Step 0.55 of the skill) before calling the engine, and passes a
4-subquery plan whose primary subquery hits reddit, x, youtube, tiktok, instagram, hackernews, polymarket.

## Cadence & output

- **Baseline now:** run A-E with full credentialed sources; archive each raw pull and a dated findings file
  under `../analysis/` (e.g. `social_listening_<topic>_<date>.md`).
- **Monthly re-run:** same prompts → detect trend movement (the point is the *delta* over time).
- Roll findings into `../analysis/state_of_value_participation_*.md`; tag each signal rising/flat/unclear.

## Known limits (state honestly in any output)

- **X is currently down** (token issue above) — fix `AUTH_TOKEN`/`CT0` to add the operator/VC voice layer.
- **LinkedIn** full text sits behind login → discovery only; verify via the post's primary source.
- Engagement counts appear only where the credentialed API path exposes them.

_Created 2026-06-18. Operationalizes Ethan's 2026-06-07 directive (`../../docs/research/ethan_guidance_2026-06-07.md`)._
