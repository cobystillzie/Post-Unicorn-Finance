"""Render the 136-entity asset-class atlas (NEW taxonomy) to a self-contained HTML + PDF packet.

WHY THIS EXISTS
---------------
The existing packet tooling (`export_shareable_atlas.py`) renders the 866-row `industry_entities`
table from atlas.sqlite using the OLD taxonomy (Patient / Portfolio / LMV / Search-ETA / Sovereign).
This script instead renders the CURRENT new-taxonomy classification layer
(`data/evidence/atlas_asset_class_audit.csv`, 136 rows: SMV / Nimble / Permanent / Studio / Impact Capital /
Reserved / Excluded-Traditional), enriched with the verbatim self-ID quotes from `funds_verified.csv`.

It is a CURRENT-STATE SNAPSHOT, organized in Ethan's "Active Experiments vs Trends/Watch" structure.
It is explicitly PRE-RECONCILIATION: the SMV/Nimble split is still by instrument and is flagged.

The PDF is produced by reusing `export_atlas_pdf.render_pdf` (headless Chrome/Edge).

USAGE
-----
    python scripts/render_asset_class_packet.py
    python scripts/render_asset_class_packet.py --no-pdf   # HTML only
"""
from __future__ import annotations

import argparse
import csv
import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT_CSV = ROOT / "data" / "evidence" / "atlas_asset_class_audit.csv"
VERIFIED_CSV = ROOT / "data" / "evidence" / "funds_verified.csv"
OUT_HTML = ROOT / "site" / "post_unicorn_atlas_packet.html"
OUT_PDF = ROOT / "site" / "post_unicorn_atlas_packet.pdf"
SNAPSHOT = "2026-06-08"

# section, display title, definition (definition text is plain; rendered escaped)
CLASS_META = {
    "SMV": ("Active Experiments", "SMV - Small-to-Medium Venture",
            "Equity targeting venture-scale, non-unicorn $50M-500M outcomes. NOTE: the SMV/Nimble split "
            "is currently by instrument and is PENDING reconciliation with Ethan (market-size + exit-speed)."),
    "Nimble": ("Active Experiments", "Nimble Capital",
               "Capital-efficient / non-dilutive / revenue-based / micro, fast realization. NOTE: under "
               "Ethan's market-size definition these may not be 'Nimble' and Nimble may have no true funds "
               "yet - PENDING reconciliation."),
    "Permanent": ("Active Experiments", "Permanent Capital",
                  "No exit required: buy-and-hold holdcos, evergreen, permanent equity, steward-ownership. "
                  "(50% of the atlas - the dominant archetype.)"),
    "Studio": ("Active Experiments", "Studio Capital",
               "Systematic company creation as the investment activity (venture studios)."),
    "Impact Capital": ("Active Experiments", "Impact Capital",
                       "Tech-enabled, mission/impact-driven allocators that explicitly reject the unicorn / "
                       "power-law model (frontier-market & catalytic VC, impact funds). Tech-enabled is "
                       "required going forward; Delta Fund is a documented operator-vouched non-tech "
                       "exception. Distinct from the reserved Sovereign Capital (sovereign wealth / DFI / "
                       "blended-finance) class."),
    "Reserved": ("Trends / Watch", "Reserved - Operator / Sovereign candidates",
                 "Parked pending a finalized definition (search/ETA 'Operator'; sovereign / DFI / impact "
                 "'Sovereign'). Per Ethan, empty/forming classes are watched, never dropped."),
    "Excluded-Traditional": ("Appendix", "Excluded - Traditional / Real-Economy",
                             "Shown for transparency: real-economy or power-law firms that do NOT meet the "
                             "tech-enabled non-unicorn thesis."),
    "Under Review": ("Under Review", "Under Review - pending classification",
                     "In the atlas and carried for review, but NOT yet assigned an asset class "
                     "(operator unsure / pre-deal / needs Ethan). Not in the asset-classified total."),
}
CLASS_ORDER = ["SMV", "Nimble", "Permanent", "Studio", "Impact Capital", "Reserved", "Excluded-Traditional", "Under Review"]
SECTION_ORDER = ["Active Experiments", "Trends / Watch", "Appendix", "Under Review"]
TIER_RANK = {"verified": 0, "self_id": 1, "anchor": 2, "in_disguise": 3, "provenance": 4, "": 5}
TIER_COLOR = {"verified": "#1a7f37", "self_id": "#0969da", "anchor": "#0969da",
              "in_disguise": "#9a6700", "provenance": "#57606a", "": "#57606a"}


def _load(path: Path, key: str) -> dict[str, dict]:
    with open(path, encoding="utf-8", errors="ignore") as f:
        return {(r.get(key) or "").strip(): r for r in csv.DictReader(f)}


def _trim(text: str, n: int) -> str:
    text = " ".join((text or "").split())
    return text if len(text) <= n else text[: n - 1].rstrip() + "…"


def build_rows() -> list[dict]:
    audit = _load(AUDIT_CSV, "fund_id")
    verified = _load(VERIFIED_CSV, "fund_id")
    rows: list[dict] = []
    for fid, a in audit.items():
        v = verified.get(fid, {})
        descriptor = (v.get("niche") or "").strip() or _trim(a.get("flag", ""), 220)
        quote = (v.get("self_id_quote") or "").strip()
        url = (v.get("evidence_url") or a.get("evidence_url") or "").strip()
        rows.append({
            "name": (a.get("name") or v.get("name") or fid).strip(),
            "asset_class": (a.get("asset_class") or "").strip(),
            "tier": (a.get("tier") or "").strip(),
            "confidence": (a.get("confidence") or "").strip(),
            "tech_enabled": (a.get("tech_enabled") or "").strip(),
            "descriptor": descriptor,
            "quote": quote,
            "url": url,
            "has_quote": bool(quote),
        })
    return rows


def _badge(text: str, color: str) -> str:
    return f'<span class="badge" style="background:{color}">{html.escape(text)}</span>'


def render_entity(e: dict) -> str:
    parts = ['<article class="entity">']
    head = [f'<h4>{html.escape(e["name"])}</h4>']
    if e["tier"]:
        head.append(_badge(e["tier"], TIER_COLOR.get(e["tier"], "#57606a")))
    if e["confidence"]:
        head.append(_badge("conf: " + e["confidence"], "#6e7781"))
    if e["tech_enabled"]:
        head.append(_badge("tech: " + e["tech_enabled"], "#1f2328"))
    parts.append('<div class="ehead">' + "".join(head) + "</div>")
    if e["descriptor"]:
        parts.append(f'<p class="desc">{html.escape(_trim(e["descriptor"], 320))}</p>')
    if e["quote"]:
        parts.append(f'<blockquote>{html.escape(_trim(e["quote"], 340))}</blockquote>')
    if e["url"]:
        u = html.escape(e["url"])
        parts.append(f'<p class="src"><a href="{u}">{u}</a></p>')
    parts.append("</article>")
    return "\n".join(parts)


def render_html(rows: list[dict]) -> str:
    from collections import Counter
    by_class = Counter(r["asset_class"] for r in rows)
    by_tier = Counter(r["tier"] for r in rows)
    quoted = sum(1 for r in rows if r["has_quote"])
    review_ct = by_class.get("Under Review", 0)
    classified_ct = sum(v for k, v in by_class.items() if k != "Under Review")

    # cover summary table
    summ = ['<table class="summary"><thead><tr><th>Asset class</th><th>Section</th><th>Count</th></tr></thead><tbody>']
    for cls in CLASS_ORDER:
        if by_class.get(cls):
            sec = CLASS_META[cls][0]
            summ.append(f'<tr><td>{html.escape(cls)}</td><td>{html.escape(sec)}</td><td class="num">{by_class[cls]}</td></tr>')
    summ.append(f'<tr class="total"><td>TOTAL (asset-classified)</td><td></td><td class="num">{classified_ct}</td></tr>')
    summ.append("</tbody></table>")
    tier_line = " &middot; ".join(f"{t or '(none)'}: {n}" for t, n in by_tier.most_common())

    # body sections
    body = []
    for section in SECTION_ORDER:
        classes_here = [c for c in CLASS_ORDER if CLASS_META[c][0] == section and by_class.get(c)]
        if not classes_here:
            continue
        body.append(f'<h2 class="section">{html.escape(section)}</h2>')
        for cls in classes_here:
            _, title, definition = CLASS_META[cls]
            ents = [r for r in rows if r["asset_class"] == cls]
            ents.sort(key=lambda r: (TIER_RANK.get(r["tier"], 9), r["name"].lower()))
            body.append(f'<h3 class="cls">{html.escape(title)} <span class="cnt">{len(ents)}</span></h3>')
            body.append(f'<p class="clsdef">{html.escape(definition)}</p>')
            body.append('<div class="entities">' + "\n".join(render_entity(e) for e in ents) + "</div>")

    css = """
    @page { size: Letter; margin: 16mm 15mm 18mm; }
    * { box-sizing: border-box; }
    body { font: 11pt/1.5 -apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; color:#1f2328; margin:0; }
    .cover { padding: 4mm 0 6mm; border-bottom: 3px solid #312e81; margin-bottom: 8mm; }
    .kicker { letter-spacing:.16em; text-transform:uppercase; font-size:9pt; color:#312e81; font-weight:700; margin:0; }
    h1 { font-size:30pt; line-height:1.08; margin:.15em 0 .1em; letter-spacing:-.01em; }
    .sub { font-size:12pt; color:#57606a; margin:.2em 0 0; }
    .caveats { background:#fff8e6; border:1px solid #f0d264; border-left:5px solid #d4a72c; padding:10px 14px; margin:7mm 0; font-size:9.5pt; }
    .caveats b { color:#7a5c00; }
    table.summary { border-collapse:collapse; width:100%; font-size:10pt; margin:5mm 0 2mm; }
    table.summary th, table.summary td { border-bottom:1px solid #d0d7de; padding:5px 8px; text-align:left; }
    table.summary th { background:#f6f8fa; font-size:8.5pt; letter-spacing:.05em; text-transform:uppercase; color:#57606a; }
    table.summary td.num { text-align:right; font-variant-numeric:tabular-nums; font-weight:600; }
    table.summary tr.total td { border-top:2px solid #312e81; font-weight:700; }
    .tiers { font-size:9pt; color:#57606a; margin:2mm 0 0; }
    h2.section { font-size:16pt; margin:11mm 0 1mm; padding-top:3mm; border-top:2px solid #312e81; color:#312e81; letter-spacing:.01em; }
    h3.cls { font-size:13.5pt; margin:6mm 0 .5mm; }
    h3.cls .cnt { display:inline-block; background:#312e81; color:#fff; border-radius:10px; font-size:9pt; padding:1px 9px; vertical-align:middle; margin-left:6px; }
    p.clsdef { font-size:9.5pt; color:#57606a; margin:.2em 0 3mm; max-width:62em; }
    .entities { display:block; }
    article.entity { break-inside:avoid; page-break-inside:avoid; border-left:3px solid #d0d7de; padding:2px 0 6px 11px; margin:0 0 5mm; }
    .ehead { display:flex; flex-wrap:wrap; align-items:center; gap:6px; }
    article.entity h4 { font-size:11.5pt; margin:0 4px 0 0; }
    .badge { color:#fff; font-size:7.5pt; font-weight:700; letter-spacing:.03em; text-transform:uppercase; border-radius:4px; padding:2px 6px; }
    p.desc { margin:3px 0 0; font-size:10pt; }
    blockquote { margin:5px 0 0; padding:4px 0 4px 10px; border-left:2px solid #c9c2f0; color:#3a3a3a; font-style:italic; font-size:9.5pt; }
    p.src { margin:3px 0 0; font-size:8pt; }
    p.src a { color:#0969da; word-break:break-all; text-decoration:none; }
    .foot { margin-top:9mm; padding-top:3mm; border-top:1px solid #d0d7de; font-size:8.5pt; color:#8c959f; }
    """

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Post-Unicorn Finance Atlas (snapshot {SNAPSHOT})</title>
<style>{css}</style></head><body>
<header class="cover">
  <p class="kicker">Post-Unicorn Finance &middot; Capital-Allocator Atlas</p>
  <h1>The Post-Unicorn Finance Atlas</h1>
  <p class="sub">New-taxonomy classification snapshot &middot; {SNAPSHOT} &middot; {classified_ct} asset-classified + {review_ct} under review &middot; {quoted} with verbatim self-ID quotes</p>
</header>

<div class="caveats">
  <b>Read me first - this is a current-state snapshot, not the final report.</b> It reflects the data exactly
  as classified today. The <b>SMV / Nimble</b> split is still by <i>instrument</i> and is <b>pending
  reconciliation with Ethan</b> (who defines them by market size + liquidity speed); some rows here may move.
  <b>Permanent Capital is 50%</b> of the set - an archetype concentration we are deliberately working to
  broaden (this snapshot adds a new <b>Impact Capital</b> class). Structure follows Ethan's
  <b>"Active Experiments vs Trends / Watch"</b> directive.
</div>

{''.join(summ)}
<p class="tiers"><b>By evidence tier:</b> {tier_line}</p>

{''.join(body)}

<p class="foot">Source: data/evidence/atlas_asset_class_audit.csv ({classified_ct} classified + {review_ct} under review) joined to funds_verified.csv (127) on fund_id.
Generated by scripts/render_asset_class_packet.py. Snapshot {SNAPSHOT}. Pre-reconciliation; do not treat class
assignments as final.</p>
</body></html>"""


def main() -> int:
    ap = argparse.ArgumentParser(description="Render the 136-entity new-taxonomy atlas packet (HTML+PDF).")
    ap.add_argument("--no-pdf", action="store_true", help="write HTML only, skip the Chrome PDF render")
    args = ap.parse_args()

    rows = build_rows()
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    OUT_HTML.write_text(render_html(rows), encoding="utf-8")
    print(f"HTML written: {OUT_HTML}  ({len(rows)} entities)")

    if args.no_pdf:
        return 0
    sys.path.insert(0, str(ROOT / "scripts"))
    from export_atlas_pdf import render_pdf  # noqa: E402
    pdf = render_pdf(OUT_HTML, OUT_PDF)
    size = pdf.stat().st_size
    print(f"PDF written:  {pdf}  ({size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
