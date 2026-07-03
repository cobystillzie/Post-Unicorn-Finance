"""
Render the boundary/taxonomy appendix sections for the Atlas packet HTML.

Consumed by export_shareable_atlas.build_report: loads
data/runtime/boundary_appendix_2026-06-01.json and returns a self-contained HTML
block (scoped <style> + four <section>s) using CSS classes that do NOT collide
with the publisher's validated counters ('entity-card', 'claim').

Sections:
  1. Taxonomy diagram  - visual layered map + full matrix (mechanism, instrument, one-line test)
  2. Mechanism axes    - the five axes that separate the classes
  3. Boundary resolutions - grouped by overlap pair; every contested company with
                            what-it-looks-like / why / what-decided / final class / verbatim quote
  4. Two non-allocator layers - Ecosystem roster + UVC-adjacent excluded roster
"""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPENDIX_PATH = ROOT / "data" / "runtime" / "boundary_appendix_2026-06-01.json"


def load_boundary_appendix(path: Path = APPENDIX_PATH) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


APPENDIX_CSS = """
<style>
  .apx { margin: 46px 0; }
  .apx h2 { font-family: Georgia, "Times New Roman", serif; font-size: 30px; margin: 0 0 6px; padding-bottom: 10px; border-bottom: 1px solid var(--line); }
  .apx h2 span { font-family: inherit; color: var(--muted); font-size: 18px; font-weight: 400; }
  .apx-lead { color: #403a34; max-width: 880px; margin: 8px 0 18px; }
  .taxo-map { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 12px 0; }
  .taxo-tile { border: 1px solid var(--line); background: var(--panel); padding: 12px; }
  .taxo-tile .k { font-weight: 700; font-size: 15px; }
  .taxo-tile .n { font-size: 26px; color: var(--accent); font-weight: 700; line-height: 1.1; }
  .taxo-tile .m { font-size: 12px; color: var(--muted); }
  .taxo-band { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: var(--accent-2); font-weight: 700; margin: 16px 0 6px; }
  .taxo-layers { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .taxo-layer { border: 1px dashed var(--line); background: #f4efe5; padding: 12px; }
  .taxo-table { width: 100%; border-collapse: collapse; border: 1px solid var(--line); background: var(--panel); font-size: 13px; margin-top: 16px; }
  .taxo-table th, .taxo-table td { border-bottom: 1px solid var(--line); padding: 10px; vertical-align: top; text-align: left; }
  .taxo-table th { font-size: 11px; text-transform: uppercase; letter-spacing: .07em; color: var(--muted); }
  .taxo-table .lyr td { background: #f4efe5; }
  .axis-grid { display: grid; gap: 10px; }
  .axis-card { border: 1px solid var(--line); background: var(--panel); padding: 14px; border-left: 4px solid var(--accent); }
  .axis-card .ax { font-weight: 700; font-size: 16px; }
  .axis-card .sp { color: var(--ink); margin: 5px 0; font-size: 14px; }
  .axis-card .nt { color: var(--muted); font-size: 13px; }
  .bnd-group { border: 1px solid var(--line); background: var(--panel); margin: 14px 0; break-inside: avoid; }
  .bnd-pair { display: flex; justify-content: space-between; gap: 12px; align-items: baseline; background: #f4efe5; border-bottom: 1px solid var(--line); padding: 11px 14px; }
  .bnd-pair .pl { font-weight: 700; font-size: 17px; }
  .bnd-pair .ct { color: var(--muted); font-size: 13px; white-space: nowrap; }
  .bnd-triad { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; padding: 12px 14px; border-bottom: 1px solid #eee7db; }
  .bnd-triad div span { display: block; font-size: 11px; text-transform: uppercase; letter-spacing: .06em; color: var(--accent-2); margin-bottom: 3px; font-weight: 700; }
  .bnd-triad div p { margin: 0; font-size: 13px; }
  .bnd-row { padding: 11px 14px; border-top: 1px solid #eee7db; break-inside: avoid; }
  .bnd-row .co { display: flex; justify-content: space-between; gap: 10px; align-items: baseline; }
  .bnd-row .nm { font-weight: 700; }
  .bnd-row .fc { color: var(--accent-2); font-weight: 700; font-size: 13px; white-space: nowrap; }
  .bnd-row .vd { color: #3d3831; font-size: 13px; margin: 4px 0 0; }
  .bnd-row .qt { color: #4a443c; font-size: 13px; border-left: 3px solid var(--line); background: #f8f3e9; padding: 6px 10px; margin: 6px 0 0; font-style: italic; }
  .layer-intro { color: var(--muted); font-size: 13px; margin: 4px 0 12px; }
  .layer-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }
  .layer-card { border: 1px solid var(--line); background: var(--panel); padding: 11px 13px; break-inside: avoid; }
  .layer-card .nm { font-weight: 700; }
  .layer-card .meta { color: var(--muted); font-size: 12px; }
  .layer-card .qt { color: #4a443c; font-size: 12px; font-style: italic; margin-top: 5px; }
  @media (max-width: 820px) {
    .taxo-map { grid-template-columns: repeat(2, 1fr); }
    .taxo-layers { grid-template-columns: 1fr; }
    .bnd-triad { grid-template-columns: 1fr; }
    .layer-grid { grid-template-columns: 1fr; }
  }
  @media print {
    .bnd-group, .bnd-row, .axis-card, .layer-card, .taxo-tile { break-inside: avoid; page-break-inside: avoid; }
    .apx h2 { break-after: avoid; }
  }
</style>
"""


def _render_taxonomy(taxonomy: list[dict]) -> str:
    allocators = [t for t in taxonomy if t.get("layer") == "allocator"]
    layers = [t for t in taxonomy if t.get("layer") != "allocator"]

    tiles = "".join(
        '<div class="taxo-tile">'
        f'<div class="k">{_esc(t["klass"])}</div>'
        f'<div class="n">{_esc(t["count"])}</div>'
        f'<div class="m">{_esc(t["mechanism"])}</div>'
        "</div>"
        for t in allocators
    )
    layer_tiles = "".join(
        '<div class="taxo-layer">'
        f'<div class="k"><strong>{_esc(t["klass"])}</strong> &middot; {_esc(t["count"])}</div>'
        f'<div class="m">{_esc(t["mechanism"])}</div>'
        "</div>"
        for t in layers
    )
    body_rows = []
    for t in taxonomy:
        cls = ' class="lyr"' if t.get("layer") != "allocator" else ""
        body_rows.append(
            f"<tr{cls}>"
            f"<td><strong>{_esc(t['klass'])}</strong></td>"
            f"<td>{_esc(t['mechanism'])}</td>"
            f"<td>{_esc(t['instrument'])}</td>"
            f"<td>{_esc(t['test'])}</td>"
            f"<td>{_esc(t['count'])}</td>"
            "</tr>"
        )
    return f"""
    <section class="apx" id="apx-taxonomy">
      <h2>The Post-Unicorn Stack <span>7 allocator classes + 2 non-allocator layers</span></h2>
      <p class="apx-lead">Each class is defined by its <strong>mechanism and instrument</strong>, not by hold period or marketing language. The visual map shows the allocator layer; the two non-allocator layers below it are part of the industry's infrastructure but are not asset classes.</p>
      <div class="taxo-map">{tiles}</div>
      <div class="taxo-band">Non-allocator layers (infrastructure &amp; excluded baseline)</div>
      <div class="taxo-layers">{layer_tiles}</div>
      <table class="taxo-table">
        <thead><tr><th>Class / Layer</th><th>Core mechanism</th><th>Instrument</th><th>One-line test</th><th>Count</th></tr></thead>
        <tbody>{''.join(body_rows)}</tbody>
      </table>
    </section>"""


def _render_axes(axes: list[dict]) -> str:
    cards = "".join(
        '<div class="axis-card">'
        f'<div class="ax">{_esc(a["axis"])}</div>'
        f'<div class="sp">{_esc(a["splits"])}</div>'
        f'<div class="nt">{_esc(a["note"])}</div>'
        "</div>"
        for a in axes
    )
    return f"""
    <section class="apx" id="apx-axes">
      <h2>How the classes differ <span>five mechanism axes</span></h2>
      <p class="apx-lead">The classes look similar because they share the vocabulary of capital. They separate cleanly on five structural axes &mdash; these are the questions that resolve almost every boundary case.</p>
      <div class="axis-grid">{cards}</div>
    </section>"""


def _render_boundaries(overlap_pairs: list[dict]) -> str:
    groups = []
    for g in overlap_pairs:
        rows = []
        for c in g["companies"]:
            quote = (
                f'<p class="qt">&ldquo;{_esc(c["quote"])}&rdquo;</p>'
                if c.get("quote") else
                '<p class="qt">(no verbatim quote on file)</p>'
            )
            rows.append(
                '<div class="bnd-row">'
                '<div class="co">'
                f'<span class="nm">{_esc(c["name"])}</span>'
                f'<span class="fc">&rarr; {_esc(c["final_class"])}</span>'
                "</div>"
                f'<p class="vd">{_esc(c["verdict"])}</p>'
                f"{quote}"
                "</div>"
            )
        groups.append(
            '<div class="bnd-group">'
            '<div class="bnd-pair">'
            f'<span class="pl">{_esc(g["pair"])}</span>'
            f'<span class="ct">{_esc(g["count"])} {"company" if g["count"] == 1 else "companies"}</span>'
            "</div>"
            '<div class="bnd-triad">'
            f'<div><span>What it looks like</span><p>{_esc(g["looks_like"])}</p></div>'
            f'<div><span>Why it&rsquo;s confusing</span><p>{_esc(g["why"])}</p></div>'
            f'<div><span>What decides it</span><p>{_esc(g["what_decides"])}</p></div>'
            "</div>"
            f"{''.join(rows)}"
            "</div>"
        )
    total = sum(g["count"] for g in overlap_pairs)
    return f"""
    <section class="apx" id="apx-boundaries">
      <h2>Where the classes bleed <span>{total} contested companies, resolved</span></h2>
      <p class="apx-lead">Classification credibility is the core of this work. Every company below sat on a boundary between two classes. Each is shown with what it looked like, why it was ambiguous, what decided its final class, and &mdash; in its own words &mdash; the verbatim self-description that settled it. Groups are ordered by how much confusion they caused.</p>
      {''.join(groups)}
    </section>"""


def _render_layers(layers: dict) -> str:
    def grid(entries: list[dict]) -> str:
        cards = []
        for e in entries:
            meta = " &middot; ".join(filter(None, [_esc(e.get("former_class", "")), _esc(e.get("reason", ""))]))
            quote = f'<div class="qt">&ldquo;{_esc(e["quote"])}&rdquo;</div>' if e.get("quote") else ""
            cards.append(
                '<div class="layer-card">'
                f'<div class="nm">{_esc(e["name"])}</div>'
                f'<div class="meta">{meta}</div>'
                f"{quote}"
                "</div>"
            )
        return f'<div class="layer-grid">{"".join(cards)}</div>'

    eco = layers.get("ecosystem", [])
    uvc = layers.get("uvc", [])
    return f"""
    <section class="apx" id="apx-layers">
      <h2>The two non-allocator layers <span>{len(eco)} ecosystem &middot; {len(uvc)} excluded</span></h2>
      <p class="apx-lead">Not everything that uses the language of capital is an allocator. These two layers are kept separate so the allocator atlas stays credible.</p>
      <h3>Ecosystem / Infrastructure <span class="muted">&mdash; advisors, brokers, marketplaces, networks, grantmakers ({len(eco)})</span></h3>
      <p class="layer-intro">Real parts of the industry that make allocators findable, but deploy none of their own capital (principal-vs-agent test).</p>
      {grid(eco)}
      <h3 style="margin-top:24px;">UVC-adjacent &mdash; excluded baseline <span class="muted">&mdash; classic unicorn VC / CVC / buyout PE ({len(uvc)})</span></h3>
      <p class="layer-intro">Surfaced by the gate on founder-friendly or mission language, but structurally classic venture/PE. Held as an exclusion list so they are never re-promoted into the atlas.</p>
      {grid(uvc)}
    </section>"""


def render_appendix_sections(appendix: dict) -> str:
    """Return the full appendix HTML block (scoped style + 4 sections)."""
    if not appendix:
        return ""
    return (
        APPENDIX_CSS
        + _render_taxonomy(appendix.get("taxonomy", []))
        + _render_axes(appendix.get("axes", []))
        + _render_boundaries(appendix.get("overlap_pairs", []))
        + _render_layers(appendix.get("layers", {}))
    )
