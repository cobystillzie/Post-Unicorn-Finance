"""Mine grounded self-description text per atlas entity.

Sources, in priority order, all already captured in the repo (no hallucination):
  1. source_pages.raw_text  -- actual fetched website text
  2. industry_entities self-description fields
  3. entity_claims.claim text

Joins source_pages to entities by URL (root-domain match against entity website
and claim source_url). Writes data/analysis/entity_self_descriptions.csv.
"""
from __future__ import annotations
import csv, json, re, sqlite3
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "data" / "evidence"
OUT = ROOT / "data" / "analysis"
OUT.mkdir(parents=True, exist_ok=True)
DB = ROOT / "data" / "atlas.sqlite"

def rootdom(url: str) -> str:
    try:
        h = urlparse(url if "//" in url else "//"+url).netloc.lower()
    except Exception:
        return ""
    h = h.split(":")[0]
    if h.startswith("www."): h = h[4:]
    parts = h.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else h

def load_csv(name):
    with open(EV / name, encoding="utf-8") as f:
        return list(csv.DictReader(f))

entities = load_csv("industry_entities.csv")
claims = load_csv("entity_claims.csv")

# fetched page text keyed by root domain
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
pages = {}
for r in conn.execute("SELECT source_url, title, raw_text FROM source_pages WHERE fetch_status='ok' AND raw_text IS NOT NULL"):
    rd = rootdom(r["source_url"])
    txt = (r["raw_text"] or "").strip()
    if not rd or not txt:
        continue
    # keep longest text per domain
    if rd not in pages or len(txt) > len(pages[rd][1]):
        pages[rd] = (r["title"] or "", txt)
conn.close()

claims_by_entity = {}
for c in claims:
    claims_by_entity.setdefault(c["entity_id"], []).append(c)

rows = []
matched_pages = 0
for e in entities:
    eid = e["entity_id"]
    rd = rootdom(e["website"])
    page_title, page_text = pages.get(rd, ("", ""))
    if page_text:
        matched_pages += 1
    # structured self-description fields
    struct = " | ".join(filter(None, [
        e.get("capital_model",""), e.get("non_unicorn_thesis",""),
        e.get("target_company_profile",""), e.get("ecosystem_role",""),
        e.get("sector_focus",""), e.get("instrument_types","").replace(";"," "),
    ]))
    claim_text = " ".join(c["claim"] for c in claims_by_entity.get(eid, []))
    rows.append({
        "entity_id": eid,
        "name": e["name"],
        "placeholder_class": e["primary_asset_class"],
        "entity_type": e["entity_type"],
        "website": e["website"],
        "geography": e.get("geography",""),
        "page_root_domain": rd,
        "has_fetched_page": "yes" if page_text else "no",
        "page_title": page_title,
        "page_text_len": len(page_text),
        "structured_self_desc": struct,
        "claim_text": claim_text,
        "page_text": page_text,
    })

with open(OUT / "entity_self_descriptions.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

print(f"entities: {len(rows)}")
print(f"entities with fetched page text: {matched_pages}")
print(f"unique fetched domains available: {len(pages)}")
print(f"total page-text chars across matched entities: {sum(r['page_text_len'] for r in rows):,}")
print("wrote", OUT / "entity_self_descriptions.csv")
