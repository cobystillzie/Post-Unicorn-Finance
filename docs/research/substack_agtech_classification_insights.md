# Substack Article Insights: "2 Cows and Chickens and Bivalves"

_Source: https://agricultureisforpeople.substack.com/p/2-cows-and-chickens-and-bivalves_
_Captured 2026-05-28 during atlas-expansion session._

## What the article proposes

The author proposes a four-category taxonomy for agtech COMPANIES (not investors), using animal metaphors. The framing is intentionally counter to standard VC categorization — it classifies companies by their realistic capital path, not their sector or stage.

| Animal | Self-description | Target valuation | Capital path | Specific firms named |
|---|---|---|---|---|
| 🐄 **Cow** | Companies targeting incumbent acquisition; raise "substantive" VC, deliver "3-10x" returns to early investors | $100-500M acquisition | Standard VC → strategic exit | Bayer, John Deere, Cargill (as acquirers) |
| 🐔 **Chicken** | Hybrid tech/consulting reaching profitability quickly via "handshakes in fields and boots on the ground" | $10M-$250M | Mostly self-funded / strategic equity, NOT VC | (none specifically) |
| 🦪 **Bivalve** | Bootstrapped startups achieving "sustainable profitability" without VC | n/a | Self-funded, profit reinvestment | (none specifically) |
| 🦬 **Bison** | Climate-focused agtech with "direct and monetizable climate" benefits (biochar, rock dust, agroforestry MRV) | varies | Mixed VC/grant/impact capital | (none specifically) |

Notable quotes (verbatim):
- "Every now and then, you might stumble upon Knickers-the-giant-cow...but you just don't really get many cows with magical horns."
- "Right now, too many 🐔-companies are forcing themselves down the venture route."
- "the opportunity to bootstrap as a founder is massively impacted by systemic inequity and socioeconomic disparities."

## How this maps to our atlas

| Our taxonomy | Article equivalent | Notes |
|---|---|---|
| UVC | Cow | The standard unicorn-VC path. The article explicitly carves it out as ONE of many, not THE default. |
| SMV (capital-efficient growth equity, RBF) | Chicken | "Hybrid model" with strategic equity rather than VC. SMV providers like SaaS Capital, Capchase, and Founderpath finance this type. |
| LMV (indie, calm capital) | Bivalve | Self-funded path with optional indie-fund support. Earnest, TinySeed, Calm Company Fund. |
| Sovereign / Patient Capital / Impact | Bison | Climate-focused has grant + impact-investor capital paths. Lowercarbon Capital, Aligned Climate Capital fit here. |
| Patient Capital (steward, foundation) | (not surfaced) | The article does NOT discuss steward ownership, foundations, family offices, or permanent equity. This is a coverage gap in the article — our atlas captures these. |
| Portfolio Capital (holdcos, serial acquirers) | (not surfaced) | The article doesn't discuss holdco / acquire-and-hold models. |
| Search/ETA | (not surfaced) | Not mentioned. |

## What we adopted (without overwriting our taxonomy)

Per your instruction: this article's framework is NOT replacing our atlas taxonomy. Ethan will provide canonical classes tomorrow. What we DID adopt tonight as low-risk enrichment:

1. **Validated the "second dimension" idea**: Our atlas classifies CAPITAL PROVIDERS by structure. The article classifies COMPANIES by business model. These are orthogonal axes. Tomorrow's discussion with Ethan could explore whether we add a "target company type" column to industry_entities mapping each capital provider to which animal-shape of company they fund.

2. **No new keywords from the article**: The agriculture-specific vocabulary ("handshakes in fields", "boots on the ground", "MRV") isn't directly useful for our capital-provider keyword classifier. They'd cause false positives on agtech blog posts.

3. **Tonal validation**: The article's framing matches our atlas's reason for existing — challenging the unicorn-VC monoculture. The author's frustration that "too many chicken-companies are forcing themselves down the venture route" is exactly the problem our research investigates.

## Open question for tomorrow's Ethan discussion

Should our atlas track which "animal type" of company each capital provider funds? E.g.:
- Lowercarbon Capital → funds bisons (climate-monetizable agtech)
- Earnest Capital → funds bivalves + chickens (bootstrap/profit-first)
- Permanent Equity → funds chickens-becoming-cows (operating businesses with cash flow)
- Constellation Software → acquires bivalves (cash-flowing software businesses) and holds forever

This is potentially a high-leverage cross-reference if Ethan agrees the second-axis framing is useful.

## Did NOT change tonight

- `data/evidence/asset_classes.csv` (waiting on Ethan)
- The 6 placeholder asset-class labels (waiting on Ethan)
- The proposed v2 taxonomy in `self_description_taxonomy_findings_v2.md` (still the proposal of record)
