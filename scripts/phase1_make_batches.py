"""Phase 1 — Build per-entity vetting batches from atlas + cached homepages.

Output: data/runtime/phase1_batches/batch_NN.json
Each batch has ~30 entities with: name, website, current_class, evidence_quote,
page_title, page_text (truncated 6000 chars), fetch_status.

Vetting agents read one batch and return one verdict per entity.
"""
import csv, json, sqlite3
from pathlib import Path

ATLAS_CSV = Path("data/evidence/industry_entities.csv")
DB = Path("data/atlas.sqlite")
OUT_DIR = Path("data/runtime/phase1_batches")
OUT_DIR.mkdir(parents=True, exist_ok=True)

BATCH_SIZE = 30
TEXT_MAX = 6000

entities = []
with ATLAS_CSV.open(encoding="utf-8") as f:
    for r in csv.DictReader(f):
        entities.append({
            "name": r.get("name", "").strip(),
            "legal_name": r.get("legal_name", "").strip(),
            "website": r.get("website", "").strip(),
            "current_class": r.get("primary_asset_class", "").strip(),
            "entity_type": r.get("entity_type", "").strip(),
        })

c = sqlite3.connect(DB)
cur = c.cursor()
cur.execute("SELECT source_url, title, raw_text, fetch_status FROM source_pages")
cache = {url: (title or "", txt or "", status or "") for url, title, txt, status in cur.fetchall()}
c.close()

for e in entities:
    cached = cache.get(e["website"], ("", "", "no_cache"))
    e["page_title"] = cached[0][:200]
    e["page_text"] = (cached[1] or "")[:TEXT_MAX]
    e["fetch_status"] = cached[2]

n = len(entities)
batches = [entities[i:i+BATCH_SIZE] for i in range(0, n, BATCH_SIZE)]
for i, batch in enumerate(batches):
    out = OUT_DIR / f"batch_{i:02d}.json"
    out.write_text(json.dumps({"entities": batch}, indent=2), encoding="utf-8")

print(f"wrote {len(batches)} batches covering {n} entities to {OUT_DIR}")
no_cache = sum(1 for e in entities if e["fetch_status"] == "no_cache")
thin = sum(1 for e in entities if len(e["page_text"]) < 400)
print(f"  no_cache: {no_cache}")
print(f"  thin_page (<400 chars): {thin}")
