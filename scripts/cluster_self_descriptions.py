"""Grounded clustering of entity self-descriptions (v3).

Corpus per entity = fetched website raw_text (primary) + genuine structured
descriptor fields (capital_model, target_company_profile, sector_focus,
instrument_types). EXCLUDES boilerplate non_unicorn_thesis and claim text and
placeholder-class tokens, so groupings reflect entity-authored language.
Clustering features = bigrams+trigrams only (domain-meaningful phrases).
Pure stdlib. Emits clusters + traceable verbatim snippets.
"""
from __future__ import annotations
import csv, math, re, sqlite3, json
from collections import Counter, defaultdict
from pathlib import Path
from urllib.parse import urlparse

ROOT=Path(__file__).resolve().parents[1]; EV=ROOT/"data"/"evidence"
OUT=ROOT/"data"/"analysis"; OUT.mkdir(parents=True,exist_ok=True); DB=ROOT/"data"/"atlas.sqlite"
def rootdom(u):
    try:h=urlparse(u if "//" in u else "//"+u).netloc.lower()
    except Exception:return ""
    h=h.split(":")[0]; h=h[4:] if h.startswith("www.") else h
    p=h.split("."); return ".".join(p[-2:]) if len(p)>=2 else h
def load(n):
    with open(EV/n,encoding="utf-8") as f: return list(csv.DictReader(f))
entities=load("industry_entities.csv"); claims=load("entity_claims.csv")
cb=defaultdict(list)
for c in claims: cb[c["entity_id"]].append(c)
conn=sqlite3.connect(DB); conn.row_factory=sqlite3.Row; pages={}
for r in conn.execute("SELECT source_url,title,raw_text FROM source_pages WHERE fetch_status='ok' AND raw_text IS NOT NULL"):
    rd=rootdom(r["source_url"]); t=(r["raw_text"] or "").strip()
    if rd and t and (rd not in pages or len(t)>len(pages[rd][1])): pages[rd]=(r["title"] or "",t)
conn.close()
STOP=set("""a an the and or of to in for with on at by from as is are be this that these those we our us you your they their it its will can may not but if then than so such other more most into over under about up out off down once here there all any each few many own same too very just also etc inc llc ltd co com www http https privacy policy cookie cookies terms conditions copyright rights reserved menu home contact team careers blog news read learn click page site website email subscribe newsletter sign log get started book demo schedule call today now please thank thanks follow social media linkedin twitter facebook instagram youtube what how who why when where which while been being do does did has have had was were will would should could more less back see one two three new next let yes accept reject manage settings""".split())
PROJECT=set("""smv lmv uvc candidate candidates supports support bucket buckets evidence source sourced atlas entity entities classic unicorn unicorns mapping placeholder thesis adjacent paper verified inference""".split())
STOP|=PROJECT
WORD=re.compile(r"[a-z][a-z\-&]{1,}")
def toks(t): return [w for w in WORD.findall(t.lower()) if w not in STOP and len(w)>2]
def grams(ts):
    out=[]
    for n in (2,3):
        for i in range(len(ts)-n+1):
            g=ts[i:i+n]
            if all(w not in STOP for w in g): out.append(" ".join(g))
    return out
docs={}; meta={}; verb={}
for e in entities:
    eid=e["entity_id"]; rd=rootdom(e["website"])
    cand=[rd]+[rootdom(c["source_url"]) for c in cb[eid]]; page=""; pt=""
    for d in cand:
        if d in pages and len(pages[d][1])>len(page): pt,page=pages[d]
    struct=" ".join(filter(None,[e.get("capital_model",""),e.get("target_company_profile",""),
        e.get("sector_focus",""),e.get("instrument_types","").replace(";"," ")]))
    full=(page+" "+struct).strip()
    t=toks(full); docs[eid]=grams(t)+toks(page)  # phrases for clustering; unigrams from page for signal only via separate path
    meta[eid]={"name":e["name"],"placeholder":e["primary_asset_class"],"type":e["entity_type"],
               "has_page":bool(page),"website":e["website"],"geo":e.get("geography",""),
               "phrases":grams(t)}
    verb[eid]=re.sub(r"\s+"," ",page)[:6000]
ids=[e for e in docs if meta[e]["phrases"]]
# df over phrases only
df=Counter()
for e in ids:
    for t in set(meta[e]["phrases"]): df[t]+=1
N=len(ids); vocab={t for t,c in df.items() if 3<=c<=0.5*N}
occ=Counter()
for e in ids:
    for t in meta[e]["phrases"]:
        if t in vocab: occ[t]+=1
signal=sorted(((t,df[t],occ[t]) for t in vocab),key=lambda x:(-x[1],-x[2]))
with open(OUT/"phrase_signals.csv","w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); w.writerow(["phrase","entity_count","total_occurrences"])
    for t,d,o in signal: w.writerow([t,d,o])
def tfidf(e,k=25):
    tf=Counter(t for t in meta[e]["phrases"] if t in vocab)
    if not tf: return set()
    sc={t:(1+math.log(c))*math.log(N/df[t]) for t,c in tf.items()}
    return set(t for t,_ in sorted(sc.items(),key=lambda x:-x[1])[:k])
top={e:tfidf(e) for e in ids}
ids=[e for e in ids if top[e]]
def jac(a,b): return len(a&b)/len(a|b) if a and b else 0.0
TH=0.18; clusters=[]
for e in sorted(ids,key=lambda e:-len(top[e])):
    best=None;bs=0.0
    for ci,c in enumerate(clusters):
        s=max(jac(top[e],top[m]) for m in c)   # single-linkage / best-match
        if s>bs: bs=s;best=ci
    if best is not None and bs>=TH: clusters[best].append(e)
    else: clusters.append([e])
clusters=sorted(clusters,key=len,reverse=True)
def cterms(ms,k=16):
    c=Counter()
    for m in ms:
        for t in top[m]: c[t]+=1
    return [(t,n) for t,n in c.most_common() if n>=2][:k]
report=[]
for i,ms in enumerate(clusters):
    report.append({"cluster":i,"size":len(ms),"shared_terms":[[t,n] for t,n in cterms(ms)],
        "placeholder_mix":dict(Counter(meta[m]["placeholder"] for m in ms)),
        "members":[{"id":m,"name":meta[m]["name"],"placeholder":meta[m]["placeholder"],"has_page":meta[m]["has_page"]} for m in ms]})
json.dump(report,open(OUT/"clusters.json","w"),indent=2)
json.dump({e:verb[e] for e in ids if verb[e]},open(OUT/"verbatim_snippets.json","w"),indent=2)
print(f"entities clustered: {N}  (>=80 have real page text; rest use structured descriptors)")
print(f"phrase vocab: {len(vocab)}   clusters: {len(clusters)}")
print("\n=== TOP 40 RECURRING MULTI-WORD SELF-DESCRIPTION PHRASES ===")
for t,d,o in signal[:40]: print(f"  {d:3d} {o:4d}  {t}")
print("\n=== CLUSTERS size>=3 ===")
for r in report:
    if r["size"]>=3:
        print(f"\n[C{r['cluster']}] n={r['size']} mix={r['placeholder_mix']}")
        print("  shared:", "; ".join(f"{t}({n})" for t,n in r['shared_terms'][:10]))
        print("  members:", ", ".join(m["name"] for m in r["members"]))
