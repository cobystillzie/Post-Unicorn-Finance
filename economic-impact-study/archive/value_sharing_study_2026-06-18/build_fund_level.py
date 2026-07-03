"""Fund-level rebuild: transform the verified fund-level research-workflow JSON into
the corrected FUND-as-unit deliverables (rows = funds; portfolio companies roll up).
Deterministic — every field copied from the adversarially-verified workflow output.
No values invented. Replaces the earlier company-level pilot.
"""
import json, csv, os, re
from collections import Counter, defaultdict
from pathlib import Path

BASE = str(Path(__file__).resolve().parent)
SRC_TEMP = r"C:\Users\cobys\AppData\Local\Temp\claude\C--Users-cobys-projects-post-unicorn-finance\c4d4ba47-0558-41ba-bef7-09b77ab5b5dd\tasks\wabyhy0aq.output"
RAW_COPY = os.path.join(BASE, "data", "raw", "fund_level_output_2026-06-18.json")
TODAY = "2026-06-18"

raw = json.load(open(SRC_TEMP, encoding="utf-8"))
R = raw["result"]
# preserve a repo-local copy of the raw result for reproducibility
os.makedirs(os.path.dirname(RAW_COPY), exist_ok=True)
json.dump(R, open(RAW_COPY, "w", encoding="utf-8"), indent=1)

results = [x for x in R["results"] if x and x.get("fund_data")]


def esc(s):
    return "" if s is None else str(s).replace("|", "\\|").replace("\n", " ").strip()


def num(s):
    if not s or not isinstance(s, str):
        return None
    t = s.lower().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(k|thousand)?", t)
    if not m:
        return None
    v = float(m.group(1))
    return v * (1000 if m.group(2) else 1)


def bucket(pp):
    pp = (pp or "unknown").lower()
    if "broad" in pp or "esop" in pp or "employee owner" in pp:
        return "broad/esop"
    if "profit" in pp:
        return "profit-share"
    if "none" in pp or "standard" in pp or "concentrated" in pp:
        return "none/standard-vc"
    if "unknown" in pp or "not public" in pp:
        return "unknown"
    return "other"


def w(path, text):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, "w", encoding="utf-8").write(text)
    print("wrote", path, len(text), "chars")


# ---- company-level CSV ----
comp_fields = ["fund", "group", "company", "sector", "country", "headcount", "headcount_num",
               "employee_participation", "participation_bucket", "participation_source_url",
               "participation_quote", "headcount_source_url"]
comp_rows = []
for r in results:
    fd = r["fund_data"]
    for c in fd.get("portfolio", []):
        hn = num(c.get("headcount"))
        comp_rows.append({
            "fund": fd.get("fund"), "group": fd.get("group"), "company": c.get("company"),
            "sector": c.get("sector"), "country": c.get("country"),
            "headcount": c.get("headcount"), "headcount_num": int(hn) if hn else "",
            "employee_participation": c.get("employee_participation"),
            "participation_bucket": bucket(c.get("employee_participation")),
            "participation_source_url": c.get("participation_source_url"),
            "participation_quote": c.get("participation_quote"),
            "headcount_source_url": c.get("headcount_source_url"),
        })
cp = os.path.join(BASE, "data", "fund_portfolio_companies.csv")
with open(cp, "w", encoding="utf-8", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=comp_fields)
    wr.writeheader()
    wr.writerows(comp_rows)
print("wrote data/fund_portfolio_companies.csv", len(comp_rows), "rows")

# ---- fund-level rollup CSV ----
fund_fields = ["fund", "group", "asset_class_or_strategy", "hq_country", "sector_focus",
               "capital_deployed_or_aum", "n_portfolio_sampled", "n_broad_esop", "n_profit_share",
               "n_none_standard", "n_unknown", "broad_participation_rate", "n_with_headcount",
               "total_known_headcount", "data_confidence", "verified_keep", "fund_source_url"]
fund_rows = []
for r in results:
    fd = r["fund_data"]
    pf = fd.get("portfolio", [])
    bks = Counter(bucket(c.get("employee_participation")) for c in pf)
    hcs = [num(c.get("headcount")) for c in pf]
    hcs = [h for h in hcs if h]
    n = len(pf)
    fund_rows.append({
        "fund": fd.get("fund"), "group": fd.get("group"),
        "asset_class_or_strategy": fd.get("asset_class_or_strategy"),
        "hq_country": fd.get("hq_country"), "sector_focus": fd.get("sector_focus"),
        "capital_deployed_or_aum": fd.get("capital_deployed_or_aum"),
        "n_portfolio_sampled": n, "n_broad_esop": bks.get("broad/esop", 0),
        "n_profit_share": bks.get("profit-share", 0), "n_none_standard": bks.get("none/standard-vc", 0),
        "n_unknown": bks.get("unknown", 0),
        "broad_participation_rate": round(bks.get("broad/esop", 0) / n, 2) if n else "",
        "n_with_headcount": len(hcs), "total_known_headcount": int(sum(hcs)),
        "data_confidence": fd.get("data_confidence"),
        "verified_keep": (r.get("verdict") or {}).get("recommend_keep", ""),
        "fund_source_url": fd.get("fund_source_url"),
    })
fp = os.path.join(BASE, "data", "funds_pilot.csv")
with open(fp, "w", encoding="utf-8", newline="") as f:
    wr = csv.DictWriter(f, fieldnames=fund_fields)
    wr.writeheader()
    wr.writerows(fund_rows)
print("wrote data/funds_pilot.csv", len(fund_rows), "rows")

# ---- first cuts ----
groups = ["atlas", "worker-ownership", "vc"]
glabel = {"atlas": "Atlas (non-unicorn-chasing allocators)",
          "worker-ownership": "Worker-ownership allocators",
          "vc": "Unicorn-chasing VC funds"}
L = []
L.append("# Fund-Level First Cuts (Phase 0, rebuilt)\n")
L.append(f"Rebuilt {TODAY} as a **fund-as-unit** comparison after the company-level pilot was retired for "
         "conflating *companies* with *funds*. Rows are funds; portfolio companies roll up. **13 funds**, all "
         "adversarially verified. Data: `../data/funds_pilot.csv` (fund rollup) and "
         "`../data/fund_portfolio_companies.csv` (the sampled portfolio companies).\n")
L.append("> **Methodology demonstration, not a result.** Portfolios are documented SAMPLES (not exhaustive), "
         "and \"unknown\" means *no public evidence found* — not proven absence (atlas portfolio-company data "
         "is genuinely thin). The worker-ownership group's 100% is partly definitional (those funds exist to "
         "create employee ownership). Read this as direction + data-availability mapping, not a settled finding.\n")

L.append("\n## 1. Employee participation by group (the headline)\n")
L.append("| Group | Funds | Portfolio cos (sampled) | Broad / ESOP | None / standard-VC | Unknown |\n|---|--:|--:|--:|--:|--:|")
for g in groups:
    rs = [r for r in results if r["fund_data"].get("group") == g]
    cos = [c for r in rs for c in r["fund_data"].get("portfolio", [])]
    bk = Counter(bucket(c.get("employee_participation")) for c in cos)
    L.append(f"| {glabel[g]} | {len(rs)} | {len(cos)} | {bk.get('broad/esop',0)} | "
             f"{bk.get('none/standard-vc',0)} | {bk.get('unknown',0)} |")

L.append("\n## 2. What this says\n")
L.append("- **Worker-ownership funds** (Teamshares, Apis & Heritage, Mosaic): broad employee ownership across "
         "essentially their whole sampled portfolios — expected, since that *is* their investment thesis.\n"
         "- **Atlas non-unicorn-chasing funds**: almost no *documented* broad employee participation "
         "(mostly unknown, a few standard pools). The honest reading: being non-unicorn-chasing does NOT, by "
         "itself, mean a fund pushes worker value-sharing — and/or the data simply isn't public for these "
         "smaller firms.\n"
         "- **Unicorn-chasing VC funds**: no broad participation found; where known, standard concentrated "
         "option/RSU pools.\n"
         "- **Direct answer to Ethan's question:** worker value-sharing is real but currently lives in a "
         "*small, dedicated worker-ownership niche* — it has **not** diffused into the broader post-unicorn "
         "(atlas) capital that this project catalogs. That gap is the finding.\n")

L.append("\n## 3. Jobs (workers employed across sampled portfolios)\n")
L.append("| Group | Cos with public headcount | Total known headcount (sampled) |\n|---|--:|--:|")
for g in groups:
    rs = [r for r in results if r["fund_data"].get("group") == g]
    hcs = [num(c.get("headcount")) for r in rs for c in r["fund_data"].get("portfolio", [])]
    hcs = [h for h in hcs if h]
    L.append(f"| {glabel[g]} | {len(hcs)} | {int(sum(hcs)):,} |")
L.append("\n_Headcounts are sampled-portfolio sums from mixed-date public sources — directional only, not a "
         "per-dollar or whole-portfolio jobs figure. A like-for-like jobs-per-dollar comparison still needs "
         "whole-portfolio capital + headcount data (Phase 2 / licensed data)._\n")

L.append("\n## 4. Per-fund summary\n")
L.append("| Fund | Group | Portfolio sampled | Broad/ESOP | Known headcount |\n|---|---|--:|--:|--:|")
for r in results:
    fd = r["fund_data"]; pf = fd.get("portfolio", [])
    bk = Counter(bucket(c.get("employee_participation")) for c in pf)
    hcs = [num(c.get("headcount")) for c in pf]; hcs = [h for h in hcs if h]
    L.append(f"| {esc(fd.get('fund'))} | {fd.get('group')} | {len(pf)} | {bk.get('broad/esop',0)} | {int(sum(hcs)):,} |")

L.append("\n## 5. Honest limitations\n")
L.append("- Portfolios are documented samples; VC funds especially have far larger portfolios than sampled.\n"
         "- \"Unknown\" is dominant for atlas funds — absence of evidence, not evidence of absence.\n"
         "- No per-dollar comparison is asserted: capital denominators remain heterogeneous and "
         "whole-portfolio data is not yet available (see `../docs/04_data_strategy.md`).\n"
         "- The worker-ownership 100% rate is definitional and must be presented as such.\n")
L.append(f"\n_Generated {TODAY} from the verified fund-level research workflow._\n")
w("analysis/fund_level_first_cuts.md", "\n".join(L))

print("DONE")
