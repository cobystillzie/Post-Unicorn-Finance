"""Export the authored Post-Unicorn Finance research dossier as static HTML."""

from __future__ import annotations

import argparse
import html
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from atlas_sqlite import DEFAULT_DB


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOSSIER = ROOT / "docs" / "research" / "post_unicorn_finance_research_dossier.md"
DEFAULT_EXPORT_DIR = ROOT / "site"


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "section"


def inline_markdown(text: str) -> str:
    escaped = esc(text)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"`(.+?)`", r"<code>\1</code>", escaped)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2" target="_blank" rel="noreferrer">\1</a>',
        escaped,
    )
    return escaped


def render_table(lines: list[str]) -> str:
    rows = []
    for index, line in enumerate(lines):
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if index == 1 and all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue
        tag = "th" if index == 0 else "td"
        rendered = "".join(f"<{tag}>{inline_markdown(cell)}</{tag}>" for cell in cells)
        rows.append(f"<tr>{rendered}</tr>")
    return "<table>\n" + "\n".join(rows) + "\n</table>"


def render_markdown(markdown: str) -> str:
    html_parts: list[str] = []
    paragraph: list[str] = []
    list_items: list[str] = []
    table_lines: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            html_parts.append(f"<p>{inline_markdown(' '.join(paragraph))}</p>")
            paragraph.clear()

    def flush_list() -> None:
        if list_items:
            html_parts.append("<ul>\n" + "\n".join(list_items) + "\n</ul>")
            list_items.clear()

    def flush_table() -> None:
        if table_lines:
            html_parts.append(render_table(table_lines))
            table_lines.clear()

    for raw_line in markdown.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            flush_paragraph()
            flush_list()
            flush_table()
            continue
        if line.startswith("|") and line.endswith("|"):
            flush_paragraph()
            flush_list()
            table_lines.append(line)
            continue
        flush_table()
        heading = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading:
            flush_paragraph()
            flush_list()
            level = len(heading.group(1))
            text = heading.group(2).strip()
            html_parts.append(f'<h{level} id="{slugify(text)}">{inline_markdown(text)}</h{level}>')
            continue
        if line.startswith("- "):
            flush_paragraph()
            list_items.append(f"<li>{inline_markdown(line[2:].strip())}</li>")
            continue
        if re.match(r"^\d+\.\s+", line):
            flush_paragraph()
            numbered_text = re.sub(r"^\d+\.\s+", "", line).strip()
            list_items.append(f"<li>{inline_markdown(numbered_text)}</li>")
            continue
        if line.startswith("> "):
            flush_paragraph()
            flush_list()
            html_parts.append(f"<blockquote>{inline_markdown(line[2:].strip())}</blockquote>")
            continue
        paragraph.append(line.strip())

    flush_paragraph()
    flush_list()
    flush_table()
    return "\n".join(html_parts)


def atlas_counts(db_path: Path) -> dict[str, int]:
    with sqlite3.connect(db_path) as conn:
        return {
            "entities": conn.execute("SELECT COUNT(*) FROM industry_entities").fetchone()[0],
            "claims": conn.execute("SELECT COUNT(*) FROM entity_claims").fetchone()[0],
            "verified_claims": conn.execute(
                "SELECT COUNT(*) FROM entity_claims WHERE evidence_status = 'verified_fact'"
            ).fetchone()[0],
            "instrument_mappings": conn.execute("SELECT COUNT(*) FROM instrument_provider_map").fetchone()[0],
            "source_pages": conn.execute("SELECT COUNT(*) FROM source_pages").fetchone()[0],
            "source_pages_ok": conn.execute("SELECT COUNT(*) FROM source_pages WHERE fetch_status = 'ok'").fetchone()[0],
            "paper_ready": conn.execute("SELECT COUNT(*) FROM entity_claims WHERE paper_ready = 1").fetchone()[0],
        }


def render_snapshot(counts: dict[str, int], generated_at: str) -> str:
    metrics = [
        ("Industry entities", counts["entities"]),
        ("Claim rows", counts["claims"]),
        ("Verified claim rows", counts["verified_claims"]),
        ("Instrument mappings", counts["instrument_mappings"]),
        ("OK source pages", counts["source_pages_ok"]),
        ("Paper-ready claims", counts["paper_ready"]),
    ]
    cards = "\n".join(
        f'<div class="metric"><span>{esc(label)}</span><strong>{value}</strong></div>'
        for label, value in metrics
    )
    return f"""
<section class="snapshot" aria-label="Live atlas snapshot">
  <div class="eyebrow">Live atlas snapshot</div>
  <div class="metrics">{cards}</div>
  <p class="muted">Generated {esc(generated_at)} from the local SQLite atlas. Counts can change as the research-agent loop discovers, fetches, and extracts more evidence. Source-page total: {counts["source_pages"]}; the card counts only successful fetches.</p>
</section>
"""


def render_html(markdown_html: str, counts: dict[str, int], generated_at: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Post-Unicorn Finance Research Dossier</title>
  <style>
    :root {{
      --ink: #161411;
      --muted: #6f675d;
      --line: #d8d0c5;
      --paper: #fbf8f1;
      --panel: #fffdf8;
      --accent: #0e5f5a;
      --accent-2: #9a5b17;
      --warn: #8a5a00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
    }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; overflow-wrap: anywhere; }}
    .page {{ max-width: 980px; margin: 0 auto; padding: 44px 28px 72px; }}
    header {{ border-bottom: 1px solid var(--line); padding-bottom: 28px; margin-bottom: 26px; }}
    .eyebrow {{ color: var(--accent-2); font-size: 12px; letter-spacing: .12em; text-transform: uppercase; font-weight: 700; }}
    h1 {{
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(36px, 6vw, 68px);
      line-height: .98;
      margin: 12px 0 18px;
      letter-spacing: 0;
    }}
    h2 {{
      font-family: Georgia, "Times New Roman", serif;
      font-size: 30px;
      margin: 44px 0 14px;
      padding-bottom: 8px;
      border-bottom: 1px solid var(--line);
    }}
    h3 {{ font-size: 20px; margin: 28px 0 10px; }}
    p {{ margin: 12px 0; }}
    .deck {{ max-width: 820px; font-size: 18px; color: #403a34; }}
    .links {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 18px; }}
    .link-pill {{
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 8px 11px;
      text-decoration: none;
      color: var(--ink);
      font-size: 14px;
    }}
    .status-note, blockquote {{
      margin: 18px 0;
      padding: 14px 16px;
      border: 1px solid var(--line);
      background: #f4efe5;
      color: #3f392f;
    }}
    .snapshot {{ margin: 28px 0 34px; }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(5, minmax(120px, 1fr));
      gap: 12px;
      margin: 14px 0;
    }}
    .metric {{ border: 1px solid var(--line); background: var(--panel); padding: 14px; min-height: 88px; }}
    .metric span {{ display: block; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
    .metric strong {{ display: block; font-size: 29px; margin-top: 7px; }}
    .content {{ background: transparent; }}
    ul {{ padding-left: 22px; }}
    li {{ margin: 6px 0; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); margin: 16px 0 22px; }}
    th, td {{ text-align: left; vertical-align: top; padding: 10px 11px; border-bottom: 1px solid var(--line); }}
    th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
    code {{ background: #f3eadc; padding: 1px 4px; }}
    .muted {{ color: var(--muted); }}
    footer {{ margin-top: 48px; padding-top: 20px; border-top: 1px solid var(--line); color: var(--muted); }}
    @media (max-width: 820px) {{
      .page {{ padding: 28px 16px 48px; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    @media print {{
      body {{ background: white; }}
      .page {{ max-width: none; padding: 24px; }}
      a {{ color: black; text-decoration: none; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <header>
      <div class="eyebrow">Industry-establishment dossier</div>
      <h1>Post-Unicorn Finance Research Dossier</h1>
      <p class="deck">An investor/economist-facing memo for establishing Post-Unicorn Finance as an emerging industry category, while preserving a serious bear case and evidence boundary.</p>
      <div class="status-note"><strong>Evidence boundary:</strong> this dossier is an authored research memo. It uses the atlas as evidence, but does not treat candidate evidence as paper-ready proof or imply that a fund or investment product is viable.</div>
      <div class="links">
        <a class="link-pill" href="index.html">Industry Atlas</a>
        <a class="link-pill" href="post_unicorn_industry_atlas_entities_claims.csv">Claims CSV</a>
        <a class="link-pill" href="publish_status.json">Publish Status</a>
      </div>
    </header>
    {render_snapshot(counts, generated_at)}
    <article class="content">
      {markdown_html}
    </article>
    <footer>
      <p>Exported from C:/Users/cobys/projects/post-unicorn-finance. Use the linked sources and atlas evidence statuses before escalating any claim into the paper.</p>
    </footer>
  </main>
</body>
</html>
"""


def build_dossier_html(markdown_path: Path, export_dir: Path, db_path: Path = DEFAULT_DB) -> Path:
    export_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    markdown = markdown_path.read_text(encoding="utf-8")
    if "# Post-Unicorn Finance Research Dossier" not in markdown:
        raise ValueError(f"{markdown_path} does not look like the research dossier")
    counts = atlas_counts(db_path)
    html_path = export_dir / "research_dossier.html"
    html_path.write_text(render_html(render_markdown(markdown), counts, generated_at), encoding="utf-8")
    return html_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export the Post-Unicorn Finance research dossier as HTML.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_DOSSIER)
    parser.add_argument("--export-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    args = parser.parse_args()

    html_path = build_dossier_html(args.markdown, args.export_dir, args.db)
    print(f"Wrote research dossier HTML: {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
