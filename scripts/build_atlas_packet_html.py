#!/usr/bin/env python3
"""Render the Post-Unicorn Finance Atlas Packet as a self-contained HTML file.

Source of truth: data/evidence/atlas.csv (Schema B: asset class + liquidity horizon per row).
Output: site/atlas_packet_<date>.html

The whole packet is framed as a *capital-innovation* catalog: every asset class is a
different way capital is being deployed away from the traditional unicorn / power-law
VC model. Capital innovation is the umbrella, not a section.
"""
import csv, os, html
from collections import defaultdict, Counter

EV = "data/evidence"
SRC = os.path.join(EV, "atlas.csv")
DATE = "2026-07-02"
OUT = os.path.join("site", "atlas_packet_%s.html" % DATE)

with open(SRC, encoding="utf-8") as fh:
    rows = list(csv.DictReader(fh))

# (class key, display title, one-line definition) in packet order
SECTIONS = [
    ("Nimble", "Nimble", "Smaller markets engineered for fast (&lt;6y) liquidity events — sub-unicorn by design."),
    ("SMV", "Strategic Middle Ventures (SMV)", "Large-ish markets targeting sub-unicorn liquidity at similar-or-better timing (~7–9y)."),
    ("Permanent", "Permanent Capital", "Evergreen / steward-owned equity with no forced exit — holdcos, family offices, perpetual owners."),
    ("Studio", "Venture Studios", "Build and own their own products — company creation is the investment activity."),
    ("Impact Capital", "Impact Capital", "Mission- and impact-driven capital models."),
    ("Reserved", "Trends / Watch (Reserved)", "Asset-class theses being watched — no real funds identified yet."),
    ("Excluded-Traditional", "Excluded — Traditional (contrast baseline)", "Classic unicorn-model VC/PE, kept only to contrast against the thesis."),
    ("Under Review", "Under Review", "Borderline or unplaced entries (incl. revenue-based lenders) — kept for review, not yet assigned a class."),
]
ACTIVE = {"Nimble", "SMV", "Permanent", "Studio", "Impact Capital"}

# Override the older provisional/instrument wording above with the current
# liquidity-horizon taxonomy used by the 2026-07-02 audit.
SECTIONS = [
    ("Nimble", "Nimble", "Smaller markets engineered for fast (&lt;6y, typically 3-5y) liquidity events."),
    ("SMV", "Strategic Middle Ventures (SMV)", "Large-ish markets targeting sub-unicorn $50M-$500M liquidity on a ~7-9y path."),
    ("Permanent", "Permanent Capital", "Evergreen / steward-owned equity with no forced exit - holdcos, family offices, perpetual owners."),
    ("Studio", "Venture Studios", "Build and own their own products - company creation is the investment activity."),
    ("Impact Capital", "Impact Capital", "Tech-enabled mission- and impact-driven capital models outside power-law VC."),
    ("Reserved", "Trends / Watch (Reserved)", "Asset-class theses being watched - no real funds identified yet."),
    ("Excluded-Traditional", "Excluded - Traditional (contrast baseline)", "Classic unicorn-model VC/PE, kept only to contrast against the thesis."),
    ("Under Review", "Under Review", "Borderline or unplaced entries, including revenue-based lenders whose return is repayment rather than company exit."),
]

by_class = defaultdict(list)
for r in rows:
    by_class[(r.get("asset_class", "") or "").strip()].append(r)

BAND_COLOR = {"Nimble": "#2e7d32", "SMV": "#b7791f", "Permanent": "#37568c", "Unicorn": "#9b2226"}
CONF_COLOR = {"high": "#2e7d32", "medium": "#b7791f", "med": "#b7791f", "low": "#9b2226"}


def esc(s):
    return html.escape((s or "").strip())


def link(u):
    u = (u or "").strip()
    if not u:
        return ""
    if not u.startswith("http"):
        u = "https://" + u
    return u


def band_pill(b):
    b = (b or "").strip()
    if not b:
        return '<span class="pill pill-none">&mdash;</span>'
    c = BAND_COLOR.get(b, "#6b6b6b")
    return '<span class="pill" style="background:%s">%s</span>' % (c, esc(b))


def conf_dot(c):
    c = (c or "").strip().lower()
    col = CONF_COLOR.get(c, "#b0b0b0")
    return '<span class="dot" style="background:%s" title="%s"></span>%s' % (col, esc(c), esc(c))


def horizon(h):
    h = (h or "").strip()
    if not h:
        return "&mdash;"
    if any(ch.isdigit() for ch in h):
        return esc(h) + "y"
    return esc(h)


def tech(t):
    t = (t or "").strip().lower()
    if t in ("yes", "true", "y", "1"):
        return '<span class="tech-yes">&#10003;</span>'
    if t in ("no", "false", "n", "0"):
        return '<span class="tech-no">&ndash;</span>'
    return "&mdash;"


def cell_notes(r):
    flag = (r.get("audit_flag", "") or "").strip()
    note = (r.get("source_note", "") or "").strip()
    out = ""
    if flag:
        out += '<span class="flag" title="%s">flag</span> ' % esc(flag)
    if note:
        short = note if len(note) <= 96 else note[:93] + "…"
        out += '<span class="note" title="%s">%s</span>' % (esc(note), esc(short))
    return out or "&mdash;"


def cell_signal(r):
    q = (r.get("exit_quote", "") or "").strip()
    if not q:
        return "&mdash;"
    short = q if len(q) <= 110 else q[:107] + "…"
    return '<span class="quote" title="%s">&ldquo;%s&rdquo;</span>' % (esc(q), esc(short))


def name_cell(r):
    nm = esc(r.get("name", ""))
    u = link(r.get("website", ""))
    tier = (r.get("tier", "") or "").strip()
    tier_html = ('<span class="tier">%s</span>' % esc(tier)) if tier else ""
    if u:
        return '<a href="%s" target="_blank" rel="noopener">%s</a>%s' % (esc(u), nm, tier_html)
    return nm + tier_html


def row_html(r):
    return (
        "<tr>"
        '<td class="c-name">%s</td>'
        '<td class="c-band">%s</td>'
        '<td class="c-hz">%s</td>'
        '<td class="c-tech">%s</td>'
        '<td class="c-conf">%s</td>'
        '<td class="c-sig">%s</td>'
        '<td class="c-note">%s</td>'
        "</tr>"
    ) % (name_cell(r), band_pill(r.get("liquidity_band")), horizon(r.get("horizon_years")),
         tech(r.get("tech_enabled")), conf_dot(r.get("confidence")), cell_signal(r), cell_notes(r))


def allocator_cell(a):
    a = (a or "").strip().lower()
    if a in ("yes", "true", "y", "1"):
        return '<span class="alloc-yes">yes</span>'
    if a in ("no", "false", "n", "0"):
        return '<span class="alloc-no">no</span>'
    return "&mdash;"


def country_cell(c):
    return esc(c) if (c or "").strip() else "&mdash;"


def cell_signal(r):
    sig = (r.get("evidence_signal", "") or "").strip()
    q = (r.get("exit_quote", "") or "").strip()
    liquidity_url = link(r.get("liquidity_evidence_url", ""))
    liquidity_note = (r.get("liquidity_evidence_note", "") or "").strip()
    hz = (r.get("horizon_years", "") or "").strip()
    if not sig and not q and not hz:
        return "&mdash;"
    out = ""
    if sig:
        short = sig if len(sig) <= 145 else sig[:142] + "..."
        out += '<span class="signal-main" title="%s">%s</span>' % (esc(sig), esc(short))
    if q:
        short_q = q if len(q) <= 100 else q[:97] + "..."
        note = (" (%s)" % esc(liquidity_note)) if liquidity_note else ""
        if liquidity_url:
            cls = "quote-secondary liquidity-warning" if "not relocated" in liquidity_note.lower() else "quote-secondary"
            out += (
                '<span class="%s" title="%s"><a href="%s" target="_blank" rel="noopener">'
                'Liquidity evidence</a>%s: &ldquo;%s&rdquo;</span>'
            ) % (cls, esc(q), esc(liquidity_url), note, esc(short_q))
        else:
            out += '<span class="quote-secondary" title="%s">Exit signal: &ldquo;%s&rdquo;</span>' % (esc(q), esc(short_q))
            if hz:
                out += '<span class="missing-liquidity">Liquidity evidence URL missing</span>'
    elif hz:
        if liquidity_url:
            note = (" (%s)" % esc(liquidity_note)) if liquidity_note else ""
            out += (
                '<span class="quote-secondary"><a href="%s" target="_blank" rel="noopener">'
                'Liquidity evidence</a>%s</span>'
            ) % (esc(liquidity_url), note)
        else:
            out += '<span class="missing-liquidity">Liquidity evidence URL missing</span>'
    return out


def row_html(r):
    return (
        "<tr>"
        '<td class="c-name">%s</td>'
        '<td class="c-country">%s</td>'
        '<td class="c-band">%s</td>'
        '<td class="c-hz">%s</td>'
        '<td class="c-alloc">%s</td>'
        '<td class="c-tech">%s</td>'
        '<td class="c-conf">%s</td>'
        '<td class="c-sig">%s</td>'
        '<td class="c-note">%s</td>'
        "</tr>"
    ) % (name_cell(r), country_cell(r.get("country")), band_pill(r.get("liquidity_band")),
         horizon(r.get("horizon_years")), allocator_cell(r.get("allocator")), tech(r.get("tech_enabled")),
         conf_dot(r.get("confidence")), cell_signal(r), cell_notes(r))


# ---- distribution strip ----
counts = Counter((r.get("asset_class", "") or "").strip() for r in rows)
total = len(rows)
active_n = sum(counts.get(k, 0) for k in ACTIVE)
dist_bars = ""
for key, title, _ in SECTIONS:
    n = counts.get(key, 0)
    if not n:
        continue
    pct = 100.0 * n / total
    col = BAND_COLOR.get(key, "#0f5257")
    dist_bars += (
        '<div class="dist-row"><span class="dist-label">%s</span>'
        '<span class="dist-track"><span class="dist-fill" style="width:%.1f%%;background:%s"></span></span>'
        '<span class="dist-n">%d</span></div>'
    ) % (esc(key), pct, col, n)

# ---- toc ----
toc = ""
for key, title, _ in SECTIONS:
    n = counts.get(key, 0)
    if not n:
        continue
    anchor = key.lower().replace(" ", "-")
    toc += '<a href="#%s">%s <span>%d</span></a>' % (anchor, title, n)

# ---- sections ----
sections_html = ""
for key, title, definition in SECTIONS:
    items = by_class.get(key, [])
    if not items:
        continue
    anchor = key.lower().replace(" ", "-")
    items = sorted(items, key=lambda r: (r.get("name", "") or "").lower())
    pending = ""
    if key == "SMV":
        pending = '<p class="pending">⚠ Group 6 reclassification (impact vs. growth-equity) is pending your ruling; rows shown in current homes.</p>'
    body = "".join(row_html(r) for r in items)
    sections_html += (
        '<section id="%s" class="cls %s">'
        '<div class="cls-head"><h2>%s</h2><span class="cls-count">%d</span></div>'
        '<p class="cls-def">%s</p>%s'
        '<div class="table-wrap"><table>'
        "<thead><tr>"
        "<th>Entity</th><th>Country</th><th>Liquidity band</th><th>Horizon</th><th>Allocator</th><th>Tech</th>"
        "<th>Confidence</th><th>Evidence signal</th><th>Notes / flags</th>"
        "</tr></thead><tbody>%s</tbody></table></div></section>"
    ) % (anchor, "active" if key in ACTIVE else "passive", title, len(items), definition, pending, body)

taxonomy_html = """
<section class="taxonomy">
  <div class="tax-head">
    <p class="eyebrow">Taxonomy first</p>
    <h2>The Post-Unicorn Stack</h2>
    <p>Capital innovation is the umbrella for the whole atlas. The rows below are sorted by how capital is deployed away from the 10-year unicorn power-law model, not by financing instrument alone.</p>
  </div>
  <div class="tax-grid">
    <div class="tax-block">
      <h3>How The Classes Differ</h3>
      <table class="tax-table">
        <thead><tr><th>Class</th><th>Input</th><th>Output</th></tr></thead>
        <tbody>
          <tr><td>Nimble</td><td>Smaller markets / capital-efficient companies</td><td>Fast liquidity under 6 years, usually 3-5 years</td></tr>
          <tr><td>SMV</td><td>Large-ish markets / sub-unicorn venture outcomes</td><td>$50M-$500M liquidity on a 7-9 year path</td></tr>
          <tr><td>Permanent</td><td>Durable companies suited to long ownership</td><td>No forced exit; hold indefinitely or for decades</td></tr>
          <tr><td>Studio</td><td>Systematic company creation</td><td>Build and own products; creation itself is investment</td></tr>
          <tr><td>Impact</td><td>Tech-enabled mission-driven companies</td><td>Impact and financial returns outside the power-law frame</td></tr>
        </tbody>
      </table>
    </div>
    <div class="tax-block">
      <h3>Where Classes Bleed</h3>
      <ul>
        <li>Permanent wins when a firm is both no-exit and capital-efficient.</li>
        <li>Revenue-based financing is an instrument; lenders with repayment returns stay Under Review unless company-exit evidence exists.</li>
        <li>SMV needs both medium-speed liquidity and sub-unicorn scale evidence; timing alone is not enough.</li>
        <li>SMV/Nimble swaps remain owner-review items until the market-size boundary is fully reconciled.</li>
      </ul>
    </div>
    <div class="tax-block">
      <h3>Non-Allocator Layers</h3>
      <p>Marketplaces, brokers, media, networks, pure advisories, and no-capital accelerators may be useful ecosystem infrastructure, but they are not allocator asset classes unless they deploy their own or LP capital.</p>
    </div>
    <div class="tax-block">
      <h3>Instruments</h3>
      <p>Equity, debt, revenue-share, SAFEs, acquisitions, and studio formation are mechanisms. The atlas class is assigned from the stated thesis, liquidity path, allocator role, and tech-enabled scope.</p>
    </div>
  </div>
</section>
"""

CSS = """
:root{--paper:#faf8f3;--ink:#191817;--muted:#6b675f;--rule:#e6e0d4;--accent:#0f5257;--accent2:#b7791f;}
*{box-sizing:border-box;}
body{margin:0;background:var(--paper);color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;
  font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased;}
.wrap{max-width:1120px;margin:0 auto;padding:0 28px 96px;}
a{color:var(--accent);text-decoration:none;}
a:hover{text-decoration:underline;}
h1,h2{font-family:Georgia,"Iowan Old Style","Times New Roman",serif;font-weight:600;letter-spacing:-0.01em;}
.masthead{padding:64px 0 28px;border-bottom:3px solid var(--ink);}
.eyebrow{font-size:12px;letter-spacing:0.28em;text-transform:uppercase;color:var(--accent);font-weight:700;}
.masthead h1{font-size:clamp(2.2rem,1.2rem+3.6vw,4rem);line-height:1.03;margin:14px 0 10px;}
.masthead .sub{font-size:1.12rem;color:var(--muted);max-width:64ch;}
.masthead .meta{margin-top:18px;font-size:13px;color:var(--muted);display:flex;gap:22px;flex-wrap:wrap;}
.masthead .meta b{color:var(--ink);}
.thesis{margin:34px 0;padding:22px 26px;background:#fff;border:1px solid var(--rule);border-left:4px solid var(--accent);border-radius:2px;}
.thesis h3{margin:0 0 6px;font-size:12px;letter-spacing:0.2em;text-transform:uppercase;color:var(--accent);}
.thesis p{margin:0;font-size:1.02rem;}
.taxonomy{margin:28px 0 44px;padding:28px 0;border-top:1px solid var(--rule);border-bottom:1px solid var(--rule);}
.tax-head h2{font-size:2rem;margin:6px 0 8px;}
.tax-head p{max-width:78ch;color:var(--muted);margin:0;}
.tax-grid{display:grid;grid-template-columns:1.25fr 0.75fr;gap:26px;margin-top:22px;}
@media(max-width:900px){.tax-grid{grid-template-columns:1fr;}}
.tax-block{background:#fff;border:1px solid var(--rule);border-radius:3px;padding:16px 18px;}
.tax-block h3{font-size:12px;letter-spacing:0.18em;text-transform:uppercase;color:var(--accent);margin:0 0 10px;}
.tax-block p,.tax-block li{font-size:13px;color:var(--muted);}
.tax-block ul{margin:0;padding-left:18px;}
.tax-table{font-size:12.5px;}
.tax-table td:first-child{font-weight:700;color:var(--ink);white-space:nowrap;}
.grid{display:grid;grid-template-columns:1.05fr 0.95fr;gap:40px;margin:40px 0 8px;align-items:start;}
@media(max-width:820px){.grid{grid-template-columns:1fr;gap:26px;}}
.panel h3{font-size:12px;letter-spacing:0.2em;text-transform:uppercase;color:var(--muted);margin:0 0 14px;}
.dist-row{display:flex;align-items:center;gap:12px;margin:7px 0;font-size:13px;}
.dist-label{width:150px;color:var(--ink);}
.dist-track{flex:1;height:9px;background:#efeadd;border-radius:5px;overflow:hidden;}
.dist-fill{display:block;height:100%;border-radius:5px;}
.dist-n{width:34px;text-align:right;font-variant-numeric:tabular-nums;color:var(--muted);}
.toc{display:flex;flex-direction:column;gap:2px;}
.toc a{display:flex;justify-content:space-between;padding:8px 12px;border:1px solid var(--rule);background:#fff;border-radius:3px;font-size:13.5px;}
.toc a span{color:var(--muted);font-variant-numeric:tabular-nums;}
.legend{margin:26px 0 6px;font-size:12.5px;color:var(--muted);display:flex;gap:18px;flex-wrap:wrap;align-items:center;}
.cls{margin:52px 0 0;scroll-margin-top:20px;}
.cls-head{display:flex;align-items:baseline;gap:14px;border-bottom:1px solid var(--ink);padding-bottom:8px;}
.cls-head h2{font-size:1.7rem;margin:0;}
.cls-count{font-size:13px;color:#fff;background:var(--ink);border-radius:20px;padding:2px 11px;font-variant-numeric:tabular-nums;}
.cls.passive .cls-count{background:var(--muted);}
.cls-def{color:var(--muted);margin:10px 0 6px;max-width:80ch;}
.pending{color:#9b2226;font-size:13px;margin:2px 0 8px;}
.table-wrap{overflow-x:auto;margin-top:10px;}
table{border-collapse:collapse;width:100%;font-size:13px;}
thead th{text-align:left;font-size:11px;letter-spacing:0.06em;text-transform:uppercase;color:var(--muted);
  border-bottom:1px solid var(--rule);padding:8px 10px;white-space:nowrap;font-weight:600;}
tbody td{padding:9px 10px;border-bottom:1px solid #f0ebe0;vertical-align:top;}
tbody tr:hover{background:#fffdf7;}
.c-name{min-width:180px;font-weight:600;}
.c-country{min-width:92px;color:var(--muted);}
.c-name a{font-weight:600;}
.tier{display:block;font-weight:400;font-size:11px;color:var(--muted);text-transform:capitalize;margin-top:1px;}
.pill{display:inline-block;color:#fff;font-size:11px;font-weight:600;padding:2px 9px;border-radius:20px;white-space:nowrap;}
.pill-none{background:#e6e0d4;color:var(--muted);}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:middle;}
.c-conf{white-space:nowrap;text-transform:capitalize;color:var(--muted);}
.c-hz{font-variant-numeric:tabular-nums;white-space:nowrap;}
.tech-yes{color:#2e7d32;font-weight:700;}.tech-no{color:#b0b0b0;}
.alloc-yes{color:#2e7d32;font-weight:700;}.alloc-no{color:#9b2226;font-weight:700;}
.c-alloc{text-transform:capitalize;white-space:nowrap;}
.c-sig{max-width:390px;}
.signal-main{display:block;color:var(--ink);}
.quote-secondary{display:block;margin-top:4px;color:var(--muted);font-style:italic;}
.quote-secondary a{font-style:normal;font-weight:700;color:var(--accent);}
.liquidity-warning{color:#9b2226;}
.missing-liquidity{display:block;margin-top:4px;color:#9b2226;font-weight:700;font-style:normal;}
.quote{color:var(--ink);font-style:italic;}
.c-note{max-width:260px;color:var(--muted);}
.flag{display:inline-block;background:#9b2226;color:#fff;font-size:10px;font-weight:700;text-transform:uppercase;padding:1px 6px;border-radius:3px;margin-right:4px;}
.note{font-size:12px;}
footer{margin-top:70px;padding-top:22px;border-top:1px solid var(--rule);font-size:12.5px;color:var(--muted);}
footer b{color:var(--ink);}
@media print{body{background:#fff;font-size:11px;}.toc,.thesis{break-inside:avoid;}.cls{break-inside:avoid;}a{color:var(--ink);}}
"""

legend = (
    '<span class="legend"><b style="color:var(--ink)">Liquidity bands:</b>'
    '%s Nimble &lt;6y &nbsp; %s SMV 7–9y &nbsp; %s Permanent (no exit) &nbsp; %s Unicorn 10y+ (excluded)</span>'
) % (band_pill("Nimble"), band_pill("SMV"), band_pill("Permanent"), band_pill("Unicorn"))

legend = (
    '<span class="legend"><b style="color:var(--ink)">Liquidity bands:</b>'
    '%s Nimble &lt;6y &nbsp; %s SMV $50M-$500M / 7-9y &nbsp; %s Permanent (no exit) &nbsp; %s Unicorn 10y+ (excluded)</span>'
) % (band_pill("Nimble"), band_pill("SMV"), band_pill("Permanent"), band_pill("Unicorn"))

HTML = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Post-Unicorn Finance &mdash; The Atlas Packet</title>
<style>%s</style></head><body><div class="wrap">
<header class="masthead">
  <div class="eyebrow">Capital Innovation Atlas</div>
  <h1>Post-Unicorn Finance<br>The Atlas Packet</h1>
  <p class="sub">A source-backed catalog of how capital is being deployed <em>away</em> from the traditional unicorn / power-law venture model &mdash; sorted by the kind of capital innovation each firm represents and, where stated, its liquidity horizon.</p>
  <div class="meta"><span>Rendered <b>%s</b></span><span><b>%d</b> entities catalogued</span><span><b>%d</b> in active experiment classes</span><span>Source: <b>data/evidence/atlas.csv</b></span></div>
</header>

<section class="thesis"><h3>The thesis in one line</h3>
<p>Capital innovation is not a category in this atlas &mdash; it is the <b>whole atlas</b>. Every class below (Nimble, SMV, Permanent, Studio, Impact, and the watch/contrast sets) is a distinct experiment in funding companies outside the 10-year unicorn power-law playbook.</p></section>

%s

<div class="grid">
  <div class="panel"><h3>Distribution</h3>%s</div>
  <div class="panel"><h3>Contents</h3><nav class="toc">%s</nav></div>
</div>
%s

%s

<footer>
<p><b>Method.</b> Each entity passed the admission gate (live page + non-unicorn vocabulary) and, for the liquidity-lens rows, carries a quotable stated exit horizon. Classification follows Ethan's taxonomy (Nimble / SMV / Permanent / Studio active; Reserved on watch; Traditional excluded as contrast). <b>Under Review</b> holds borderline entries and revenue-based lenders whose "return" is loan repayment, not a company exit.</p>
<p><b>Status.</b> Authoritative data lives in <b>data/evidence/atlas.csv</b>; this HTML is generated from it by <b>scripts/build_atlas_packet_html.py</b>. Open items: Group 6 impact-vs-growth-equity ruling; Gearbox/PeakSpan band tidy; deep self-description classification pass.</p>
</footer>
</div></body></html>
""" % (CSS, DATE, total, active_n, taxonomy_html, dist_bars, toc, legend, sections_html)

os.makedirs("site", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    fh.write(HTML)

# ---- verification to stdout ----
print("WROTE", OUT, "(%d bytes)" % len(HTML))
print("total entities:", total)
print("by class:", dict(counts))
ec = [r for r in by_class.get("SMV", []) if "edited capital" in (r.get("name", "") or "").lower()]
print("Edited Capital in SMV section:", bool(ec),
      "->", ec[0].get("liquidity_band") if ec else None)
