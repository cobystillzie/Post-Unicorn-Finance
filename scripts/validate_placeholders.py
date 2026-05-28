"""Test whether each placeholder asset class is an ENTITY SELF-IDENTITY.
Evidence 1: does the class's natural-language self-label appear in the entity's
            own fetched website text? (self-identification rate)
Evidence 2: how cohesive is the class across the emergent clusters?
Pure stdlib, grounded in captured source_pages text only.
"""
import csv, sqlite3, json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parents[1]; EV=ROOT/"data"/"evidence"; DB=ROOT/"data"/"atlas.sqlite"
def rd(u):
    try:h=urlparse(u if "//" in u else "//"+u).netloc.lower()
    except Exception:return ""
    h=h.split(":")[0]; h=h[4:] if h.startswith("www.") else h
    p=h.split("."); return ".".join(p[-2:]) if len(p)>=2 else h
def load(n):
    with open(EV/n,encoding="utf-8") as f: return list(csv.DictReader(f))
ents=load("industry_entities.csv"); claims=load("entity_claims.csv")
cb=defaultdict(list)
for c in claims: cb[c["entity_id"]].append(c)
conn=sqlite3.connect(DB); conn.row_factory=sqlite3.Row; pages={}
for r in conn.execute("SELECT source_url,raw_text FROM source_pages WHERE fetch_status='ok' AND raw_text IS NOT NULL"):
    d=rd(r["source_url"]); t=(r["raw_text"] or "").lower()
    if d and t and (d not in pages or len(t)>len(pages[d])): pages[d]=t
conn.close()
# natural-language self-labels per placeholder class (what an entity would SAY about itself)
LABELS={
 "Search/ETA":["search fund","entrepreneurship through acquisition"," eta "],
 "Sovereign Capital":["sovereign","sovereign wealth","national wealth"],
 "Patient Capital":["patient capital","permanent capital","permanent equity","hold forever","no forced exit","steward","evergreen"],
 "Portfolio Capital":["venture studio","startup studio","holding company","studio","acquire and operate"],
 "SMV":["strategic middle","middle venture","capital efficient","capital-efficient","bootstrapped","profitable growth"],
 "LMV":["micro venture","solo founder","indie","micro-saas","one-person","one person company"],
}
def entpage(e):
    cand=[rd(e["website"])]+[rd(c["source_url"]) for c in cb[e["entity_id"]]]
    best=""
    for d in cand:
        if d in pages and len(pages[d])>len(best): best=pages[d]
    return best
byclass=defaultdict(list)
for e in ents: byclass[e["primary_asset_class"]].append(e)
print("=== SELF-IDENTIFICATION RATE (entity's own website uses the class's self-label) ===")
print(f"{'class':18} {'#ents':>5} {'#withpage':>9} {'#self-id':>8} {'self-id% of paged':>18}")
for cls,members in sorted(byclass.items(), key=lambda x:-len(x[1])):
    labels=LABELS.get(cls,[])
    withpage=0; selfid=0
    for e in members:
        pg=entpage(e)
        if not pg: continue
        withpage+=1
        if any(l in pg for l in labels): selfid+=1
    pct = f"{(100*selfid/withpage):.0f}%" if withpage else "n/a"
    print(f"{cls:18} {len(members):5d} {withpage:9d} {selfid:8d} {pct:>18}")
print("\n=== does the literal analyst label appear ANYWHERE in any entity page? ===")
for probe in ["strategic middle","middle venture","leveraged micro","smv","lmv"]:
    n=sum(1 for t in pages.values() if probe in t)
    print(f"  '{probe}': {n} of {len(pages)} pages")
for probe in ["search fund","sovereign","permanent equity","patient capital","revenue-based","venture studio","steward","evergreen","hold forever"]:
    n=sum(1 for t in pages.values() if probe in t)
    print(f"  '{probe}': {n} of {len(pages)} pages")
