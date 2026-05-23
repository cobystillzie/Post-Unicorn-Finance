from __future__ import annotations

import argparse
import csv
import html
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from atlas_sqlite import ranked_rows_from_db


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "atlas.sqlite"
DEFAULT_EXPORT_DIR = ROOT / "data" / "exports"


def open_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def esc(value: object) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def compact(value: object, limit: int = 280) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def fetch_rows(conn: sqlite3.Connection, query: str) -> list[sqlite3.Row]:
    return list(conn.execute(query))


def export_claims_csv(path: Path, entities: list[sqlite3.Row], claims_by_entity: dict[str, list[sqlite3.Row]]) -> None:
    fieldnames = [
        "entity_id",
        "entity_name",
        "primary_asset_class",
        "entity_type",
        "website",
        "fit_score",
        "entity_evidence_status",
        "claim_id",
        "claim_type",
        "claim",
        "claim_evidence_status",
        "claim_confidence",
        "source_url",
        "source_quality",
        "source_tier",
        "source_text_snippet",
        "paper_ready",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for entity in entities:
            claims = claims_by_entity.get(entity["entity_id"]) or [None]
            for claim in claims:
                writer.writerow(
                    {
                        "entity_id": entity["entity_id"],
                        "entity_name": entity["name"],
                        "primary_asset_class": entity["primary_asset_class"],
                        "entity_type": entity["entity_type"],
                        "website": entity["website"],
                        "fit_score": entity["fit_score"],
                        "entity_evidence_status": entity["evidence_status"],
                        "claim_id": claim["claim_id"] if claim else "",
                        "claim_type": claim["claim_type"] if claim else "",
                        "claim": claim["claim"] if claim else "",
                        "claim_evidence_status": claim["evidence_status"] if claim else "",
                        "claim_confidence": claim["claim_confidence"] if claim else "",
                        "source_url": claim["source_url"] if claim else "",
                        "source_quality": claim["source_quality"] if claim else "",
                        "source_tier": claim["source_tier"] if claim else "",
                        "source_text_snippet": claim["source_text_snippet"] if claim else "",
                        "paper_ready": claim["paper_ready"] if claim else "",
                    }
                )


def badge(label: str) -> str:
    slug = "".join(ch if ch.isalnum() else "-" for ch in label.lower()).strip("-")
    return f'<span class="badge badge-{esc(slug)}">{esc(label)}</span>'


def linked_url(url: str) -> str:
    if not url:
        return ""
    safe_url = esc(url)
    return f'<a href="{safe_url}" target="_blank" rel="noreferrer">{safe_url}</a>'


def render_asset_nav(asset_counts: list[sqlite3.Row]) -> str:
    items = []
    for row in asset_counts:
        anchor = esc(row["primary_asset_class"].lower().replace("/", "-").replace(" ", "-"))
        items.append(
            f'<a class="nav-pill" href="#asset-{anchor}"><span>{esc(row["primary_asset_class"])}</span><strong>{row["count"]}</strong></a>'
        )
    return "\n".join(items)


def render_asset_definitions(asset_classes: list[sqlite3.Row]) -> str:
    rows = []
    for row in asset_classes:
        rows.append(
            "<tr>"
            f"<td><strong>{esc(row['asset_class'])}</strong><div>{badge(row['classification_status'])}</div></td>"
            f"<td>{esc(row['definition'])}</td>"
            f"<td>{esc(row['return_model'])}</td>"
            f"<td>{esc(row['liquidity_path'])}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def render_claims(claims: list[sqlite3.Row]) -> str:
    if not claims:
        return '<p class="muted">No claim rows attached yet.</p>'
    items = []
    for claim in claims:
        snippet = compact(claim["source_text_snippet"] or claim["notes"], 240)
        items.append(
            '<li class="claim">'
            '<div class="claim-head">'
            f"{badge(claim['evidence_status'])}"
            f"<span>{esc(claim['claim_type'])}</span>"
            f"<span>confidence {esc(claim['claim_confidence'])}</span>"
            "</div>"
            f"<p>{esc(claim['claim'])}</p>"
            f'<p class="source">{linked_url(claim["source_url"])}</p>'
            f'<p class="snippet">{esc(snippet)}</p>'
            "</li>"
        )
    return f'<ol class="claims">{"".join(items)}</ol>'


def render_entities_by_asset(
    asset_counts: list[sqlite3.Row],
    entities_by_asset: dict[str, list[sqlite3.Row]],
    claims_by_entity: dict[str, list[sqlite3.Row]],
    rank_by_entity: dict[str, sqlite3.Row],
) -> str:
    sections = []
    for asset in asset_counts:
        asset_name = asset["primary_asset_class"]
        anchor = esc(asset_name.lower().replace("/", "-").replace(" ", "-"))
        cards = []
        for entity in entities_by_asset[asset_name]:
            rank = rank_by_entity.get(entity["entity_id"])
            priority = rank["atlas_priority_score"] if rank and "atlas_priority_score" in rank.keys() else ""
            claims = claims_by_entity.get(entity["entity_id"], [])
            cards.append(
                '<article class="entity-card">'
                '<div class="entity-title-row">'
                f"<h3>{esc(entity['name'])}</h3>"
                f'<span class="score">fit {esc(entity["fit_score"])}{f" / priority {esc(priority)}" if priority != "" else ""}</span>'
                "</div>"
                '<div class="meta-grid">'
                f"<div><span>Type</span><strong>{esc(entity['entity_type'])}</strong></div>"
                f"<div><span>Status</span><strong>{esc(entity['active_status'])}</strong></div>"
                f"<div><span>Evidence</span><strong>{esc(entity['evidence_status'])}</strong></div>"
                f"<div><span>Claims</span><strong>{len(claims)}</strong></div>"
                "</div>"
                f'<p class="website">{linked_url(entity["website"])}</p>'
                f'<p class="thesis">{esc(compact(entity["non_unicorn_thesis"], 300))}</p>'
                f"{render_claims(claims)}"
                "</article>"
            )
        sections.append(
            f'<section class="asset-section" id="asset-{anchor}">'
            f"<h2>{esc(asset_name)} <span>{asset['count']} entities</span></h2>"
            f"{''.join(cards)}"
            "</section>"
        )
    return "\n".join(sections)


def render_instrument_providers(instrument_mappings: list[sqlite3.Row]) -> str:
    if not instrument_mappings:
        return '<p class="muted">No instrument-provider mappings are available yet.</p>'
    grouped: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for row in instrument_mappings:
        grouped[row["instrument_name"]].append(row)

    groups = []
    for instrument_name in sorted(grouped):
        providers = []
        for row in sorted(grouped[instrument_name], key=lambda item: item["provider_name"]):
            providers.append(
                '<li class="instrument-provider">'
                f"<strong>{esc(row['provider_name'])}</strong>"
                f"<span>{esc(row['asset_class'])}</span>"
                f"<span>{esc(row['entity_type'])}</span>"
                f"{linked_url(row['source_url'])}"
                "</li>"
            )
        groups.append(
            '<article class="instrument-card">'
            f"<h3>{esc(instrument_name)}</h3>"
            f'<p class="muted">{esc(compact(grouped[instrument_name][0]["description"], 220))}</p>'
            f'<ul class="instrument-list">{"".join(providers)}</ul>'
            "</article>"
        )
    return "".join(groups)


def render_html(
    *,
    asset_classes: list[sqlite3.Row],
    asset_counts: list[sqlite3.Row],
    instrument_mappings: list[sqlite3.Row],
    status_counts: list[sqlite3.Row],
    entities: list[sqlite3.Row],
    claims: list[sqlite3.Row],
    claims_by_entity: dict[str, list[sqlite3.Row]],
    rank_by_entity: dict[str, sqlite3.Row],
    source_count: int,
    paper_ready_count: int,
    generated_at: str,
) -> str:
    entities_by_asset: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for entity in entities:
        entities_by_asset[entity["primary_asset_class"]].append(entity)
    claim_status = ", ".join(f"{row['evidence_status']}: {row['count']}" for row in status_counts)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Post-Unicorn Finance Industry Atlas</title>
  <style>
    :root {{
      --ink: #161411;
      --muted: #6f675d;
      --line: #d8d0c5;
      --paper: #fbf8f1;
      --panel: #fffdf8;
      --accent: #0e5f5a;
      --accent-2: #9a5b17;
      --good: #245f35;
      --warn: #8a5a00;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      color: var(--ink);
      background: var(--paper);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.45;
    }}
    a {{ color: var(--accent); text-decoration-thickness: 1px; text-underline-offset: 3px; overflow-wrap: anywhere; }}
    .page {{ max-width: 1180px; margin: 0 auto; padding: 44px 28px 72px; }}
    header {{
      border-bottom: 1px solid var(--line);
      padding-bottom: 28px;
      margin-bottom: 28px;
    }}
    .eyebrow {{ color: var(--accent-2); font-size: 12px; letter-spacing: .12em; text-transform: uppercase; font-weight: 700; }}
    h1 {{
      font-family: Georgia, "Times New Roman", serif;
      font-size: clamp(38px, 6vw, 72px);
      line-height: .96;
      margin: 12px 0 18px;
      letter-spacing: 0;
      max-width: 900px;
    }}
    .deck {{ max-width: 880px; font-size: 18px; color: #403a34; }}
    .status-note {{
      margin-top: 18px;
      padding: 14px 16px;
      border: 1px solid var(--line);
      background: #f4efe5;
      color: #3f392f;
      max-width: 960px;
    }}
    .metrics {{
      display: grid;
      grid-template-columns: repeat(5, minmax(130px, 1fr));
      gap: 12px;
      margin: 28px 0;
    }}
    .metric {{
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 16px;
      min-height: 96px;
    }}
    .metric span {{ display: block; color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
    .metric strong {{ display: block; font-size: 30px; margin-top: 8px; }}
    .nav {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 24px 0 36px;
    }}
    .nav-pill {{
      display: inline-flex;
      gap: 12px;
      align-items: center;
      border: 1px solid var(--line);
      background: var(--panel);
      padding: 8px 11px;
      color: var(--ink);
      text-decoration: none;
    }}
    .nav-pill strong {{ color: var(--accent); }}
    section {{ margin: 42px 0; }}
    h2 {{
      font-family: Georgia, "Times New Roman", serif;
      font-size: 30px;
      margin: 0 0 16px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--line);
    }}
    h2 span {{ font-family: inherit; color: var(--muted); font-size: 18px; font-weight: 400; }}
    .definitions {{
      width: 100%;
      border-collapse: collapse;
      background: var(--panel);
      border: 1px solid var(--line);
    }}
    .definitions th,
    .definitions td {{
      text-align: left;
      vertical-align: top;
      padding: 12px;
      border-bottom: 1px solid var(--line);
    }}
    .definitions th {{ color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }}
    .entity-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 18px;
      margin: 12px 0;
    }}
    .instrument-card {{
      background: var(--panel);
      border: 1px solid var(--line);
      padding: 16px;
      margin: 12px 0;
    }}
    .instrument-list {{
      list-style: none;
      padding: 0;
      margin: 8px 0 0;
    }}
    .instrument-provider {{
      display: grid;
      grid-template-columns: minmax(150px, 1.2fr) minmax(90px, .6fr) minmax(140px, .8fr) minmax(180px, 1.5fr);
      gap: 10px;
      align-items: start;
      padding: 9px 0;
      border-top: 1px solid #eee7db;
      font-size: 14px;
    }}
    .instrument-provider span {{ color: var(--muted); }}
    .entity-title-row {{
      display: flex;
      justify-content: space-between;
      gap: 16px;
      align-items: baseline;
      border-bottom: 1px solid #eee7db;
      padding-bottom: 10px;
    }}
    h3 {{ margin: 0; font-size: 21px; }}
    .score {{ color: var(--accent-2); white-space: nowrap; font-weight: 700; }}
    .meta-grid {{
      display: grid;
      grid-template-columns: repeat(4, minmax(140px, 1fr));
      gap: 8px;
      margin: 14px 0;
    }}
    .meta-grid div {{
      background: #f8f3e9;
      border: 1px solid #ebe1d3;
      padding: 10px;
      min-height: 68px;
    }}
    .meta-grid span {{ display: block; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }}
    .meta-grid strong {{ display: block; margin-top: 5px; font-size: 14px; }}
    .website {{ margin: 8px 0; font-size: 14px; }}
    .thesis {{ color: #3d3831; margin: 10px 0 14px; }}
    .claims {{ padding-left: 22px; margin: 0; }}
    .claim {{ padding: 13px 0; border-top: 1px solid #eee7db; }}
    .claim p {{ margin: 6px 0; }}
    .claim-head {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; color: var(--muted); font-size: 12px; }}
    .source {{ font-size: 13px; }}
    .snippet {{
      color: var(--muted);
      font-size: 13px;
      background: #f8f3e9;
      border-left: 3px solid var(--line);
      padding: 8px 10px;
    }}
    .badge {{
      display: inline-block;
      border: 1px solid var(--line);
      background: #f8f3e9;
      color: var(--muted);
      padding: 2px 7px;
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: .06em;
    }}
    .badge-verified-fact {{ color: var(--good); border-color: #b9d4bd; background: #edf6ee; }}
    .badge-candidate-evidence {{ color: var(--warn); border-color: #e1ca93; background: #fff8df; }}
    .muted {{ color: var(--muted); }}
    footer {{ margin-top: 48px; padding-top: 20px; border-top: 1px solid var(--line); color: var(--muted); }}
    @media (max-width: 820px) {{
      .page {{ padding: 28px 16px 48px; }}
      .metrics {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .meta-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .instrument-provider {{ grid-template-columns: minmax(0, 1fr); }}
      .entity-title-row {{ display: block; }}
      .score {{ display: block; margin-top: 8px; }}
    }}
    @media print {{
      body {{ background: white; }}
      .page {{ max-width: none; padding: 24px; }}
      .entity-card {{ break-inside: avoid; }}
      a {{ color: black; text-decoration: none; }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <header>
      <div class="eyebrow">Working research atlas</div>
      <h1>Post-Unicorn Finance Industry Atlas</h1>
      <p class="deck">A source-backed map of firms, funds, platforms, studios, acquirers, and capital providers operating outside or adjacent to classic unicorn venture capital, plus the financing mechanisms they use.</p>
      <div class="status-note"><strong>Evidence boundary:</strong> this packet is a working research export. Candidate evidence is useful for mapping and follow-up, but it is not paper-ready. Instruments are financing mechanisms, not entity asset classes.</div>
    </header>

    <section class="metrics" aria-label="Atlas metrics">
      <div class="metric"><span>Entities</span><strong>{len(entities)}</strong></div>
      <div class="metric"><span>Claims</span><strong>{len(claims)}</strong></div>
      <div class="metric"><span>Entity groups</span><strong>{len(asset_counts)}</strong></div>
      <div class="metric"><span>Instrument links</span><strong>{len(instrument_mappings)}</strong></div>
      <div class="metric"><span>Paper-ready claims</span><strong>{paper_ready_count}</strong></div>
    </section>

    <p class="muted">Generated {esc(generated_at)} from local SQLite atlas with {source_count} registered source URLs. Claim evidence mix: {esc(claim_status)}.</p>
    <nav class="nav" aria-label="Asset class navigation">
      {render_asset_nav(asset_counts)}
    </nav>

    <section>
      <h2>Taxonomy <span>{len(asset_classes)} rows, including instrument family</span></h2>
      <p class="muted">Rows marked as instrument families describe financing mechanisms. They are not used as primary entity groups.</p>
      <table class="definitions">
        <thead>
          <tr><th>Bucket</th><th>Definition</th><th>Return Model</th><th>Liquidity Path</th></tr>
        </thead>
        <tbody>
          {render_asset_definitions(asset_classes)}
        </tbody>
      </table>
    </section>

    <section id="instrument-providers">
      <h2>Instrument Providers And Financing Mechanisms <span>{len(instrument_mappings)} mappings</span></h2>
      {render_instrument_providers(instrument_mappings)}
    </section>

    {render_entities_by_asset(asset_counts, entities_by_asset, claims_by_entity, rank_by_entity)}

    <footer>
      <p>Exported from C:/Users/cobys/projects/post-unicorn-finance. Use source URLs and evidence statuses when citing or escalating claims.</p>
    </footer>
  </main>
</body>
</html>
"""


def render_cover_note(
    *,
    entity_count: int,
    claim_count: int,
    source_count: int,
    instrument_map_count: int,
    asset_counts: list[sqlite3.Row],
    status_counts: list[sqlite3.Row],
    paper_ready_count: int,
    generated_at: str,
) -> str:
    asset_lines = "\n".join(
        f"- {row['primary_asset_class']}: {row['count']}" for row in asset_counts
    )
    status_lines = "\n".join(
        f"- {row['evidence_status']}: {row['count']}" for row in status_counts
    )
    return f"""Subject: Post-Unicorn Finance industry atlas export

Hi [Name],

I wanted to share the current working export from the Post-Unicorn Finance research atlas.

The attached HTML packet is designed as an accessible review artifact rather than just a raw data dump. It includes every current atlas entity, grouped by asset class, with the attached source-backed claims, source URLs, evidence status, fit score, entity type, website, and thesis notes. I also included a companion CSV for filtering or deeper review.

Current validated atlas snapshot:

- Industry entities: {entity_count}
- Claim rows: {claim_count}
- Registered source URLs: {source_count}
- Instrument-provider mappings: {instrument_map_count}
- Paper-ready claims: {paper_ready_count}

Entity coverage by current primary asset class:

{asset_lines}

Claim evidence mix:

{status_lines}

Important evidence boundary: this is a working research atlas, not a final paper-ready proof set. Candidate evidence is useful for mapping the industry and deciding where to research next. Paper-ready status remains gated by human review. Instruments are now presented as financing mechanisms used by entities, not as a primary asset class.

The main thing this demonstrates is that the project now has a durable structure for establishing the industry: a taxonomy, a source-backed entity atlas, claims tied to URLs, instrument mappings, intake and promotion logic for new leads, and validation tests to keep the data from drifting.

Generated: {generated_at}

Best,
Coby
"""


def build_report(db_path: Path, export_dir: Path) -> tuple[Path, Path, Path]:
    export_dir.mkdir(parents=True, exist_ok=True)
    html_path = export_dir / "post_unicorn_industry_atlas_packet.html"
    csv_path = export_dir / "post_unicorn_industry_atlas_entities_claims.csv"
    cover_note_path = export_dir / "post_unicorn_industry_atlas_cover_note.md"
    generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

    with open_db(db_path) as conn:
        entities = fetch_rows(
            conn,
            """
            SELECT *
            FROM industry_entities
            ORDER BY primary_asset_class, fit_score DESC, name
            """,
        )
        claims = fetch_rows(
            conn,
            """
            SELECT *
            FROM entity_claims
            ORDER BY entity_name, evidence_status DESC, claim_id
            """,
        )
        asset_classes = fetch_rows(conn, "SELECT * FROM asset_classes ORDER BY asset_class")
        asset_counts = fetch_rows(
            conn,
            """
            SELECT primary_asset_class, COUNT(*) AS count
            FROM industry_entities
            GROUP BY primary_asset_class
            ORDER BY count DESC, primary_asset_class
            """,
        )
        status_counts = fetch_rows(
            conn,
            """
            SELECT evidence_status, COUNT(*) AS count
            FROM entity_claims
            GROUP BY evidence_status
            ORDER BY count DESC, evidence_status
            """,
        )
        instrument_mappings = fetch_rows(
            conn,
            """
            SELECT
                m.instrument_id,
                m.instrument_name,
                m.provider_entity_id,
                m.provider_name,
                m.asset_class,
                m.description,
                m.source_url,
                m.evidence_status,
                e.entity_type,
                e.website,
                e.instrument_types
            FROM instrument_provider_map m
            LEFT JOIN industry_entities e
              ON e.entity_id = m.provider_entity_id
            ORDER BY m.instrument_name, m.provider_name
            """,
        )
        source_count = conn.execute("SELECT COUNT(*) FROM source_registry").fetchone()[0]
        paper_ready_count = conn.execute("SELECT COUNT(*) FROM entity_claims WHERE paper_ready = 1").fetchone()[0]

    claims_by_entity: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for claim in claims:
        claims_by_entity[claim["entity_id"]].append(claim)
    ranked = ranked_rows_from_db(db_path, 0)
    rank_by_entity = {row["entity_id"]: row for row in ranked}

    export_claims_csv(csv_path, entities, claims_by_entity)
    html_path.write_text(
        render_html(
            asset_classes=asset_classes,
            asset_counts=asset_counts,
            instrument_mappings=instrument_mappings,
            status_counts=status_counts,
            entities=entities,
            claims=claims,
            claims_by_entity=claims_by_entity,
            rank_by_entity=rank_by_entity,
            source_count=source_count,
            paper_ready_count=paper_ready_count,
            generated_at=generated_at,
        ),
        encoding="utf-8",
    )
    cover_note_path.write_text(
        render_cover_note(
            entity_count=len(entities),
            claim_count=len(claims),
            source_count=source_count,
            instrument_map_count=len(instrument_mappings),
            asset_counts=asset_counts,
            status_counts=status_counts,
            paper_ready_count=paper_ready_count,
            generated_at=generated_at,
        ),
        encoding="utf-8",
    )
    return html_path, csv_path, cover_note_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a shareable Post-Unicorn Finance atlas packet.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--export-dir", type=Path, default=DEFAULT_EXPORT_DIR)
    args = parser.parse_args()

    html_path, csv_path, cover_note_path = build_report(args.db, args.export_dir)
    print(f"Wrote HTML packet: {html_path}")
    print(f"Wrote claims CSV: {csv_path}")
    print(f"Wrote cover note: {cover_note_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
