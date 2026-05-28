"""Build a self-contained interactive dashboard from grounded analysis files."""
import csv, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; AN=ROOT/"data"/"analysis"
phrases=[]
with open(AN/"phrase_signals.csv") as f:
    for r in csv.DictReader(f):
        phrases.append({"p":r["phrase"],"e":int(r["entity_count"]),"o":int(r["total_occurrences"])})
phrases=sorted(phrases,key=lambda x:(-x["e"],-x["o"]))[:200]
clusters=[c for c in json.load(open(AN/"clusters.json")) if c["size"]>=3]
for c in clusters:
    c["shared"]=[t for t,_ in c["shared_terms"][:12]]
    c["mem"]=[m["name"] for m in c["members"]]
verdicts=[
 ["Search / ETA","VALIDATED","cluster of 14, 100% pure","search fund · search capital · entrepreneurs search funds"],
 ["Sovereign Capital","VALIDATED","cluster of 8, 100% pure","sovereign wealth · global investment · capital allocator"],
 ["Portfolio Capital (acquirers)","VALIDATED, MIS-NAMED","cluster of 16, 15/16 pure","software acquisition capital · vertical software · permanent equity"],
 ["Portfolio Capital (studios)","CROSS-CUTTING","clusters 14 + 4","studio equity · company creation · startup studio"],
 ["Patient Capital","MERGE CANDIDATE","overlaps permanent/steward/evergreen","patient capital · permanent equity · no forced exit · steward"],
 ["SMV","ANALYST UMBRELLA (not self-identity)","65 entities scatter across 4 clusters","traits used (capital-efficient/bootstrapped); name used by none"],
 ["LMV","PREMATURE as entity class","thin (8), no clean cluster","archetype real (solo AI founders); entity infra barely exists"],
]
newents=[
 ["Everhold","everhold.com","Permanent / hold-forever holdco","\"We buy businesses. And hold them forever… We're not a private equity firm… we use permanent capital.\""],
 ["Purpose Evergreen Capital","purpose-economy.org","Steward / evergreen patient capital","\"patient, value-aligned capital… evergreen fund without pressure to force an exit… return rate is capped.\""],
 ["HOLD.co","hold.co","Permanent-capital holding company","Permanent-capital holding-company strategy (own blog)."],
 ["Upliift","upliift.com","Permanent equity","Permanent-equity approach."],
 ["Bending Spoons","bendingspoons.com","Acquire & hold tech brands","Holds Evernote, Vimeo, Meetup with no plans to sell."],
 ["Fund for Employee Ownership","evgoh.com","Patient capital → employee ownership","Acquires SMBs, converts to employee ownership, long-term."],
 ["Evergreen","evergreensg.com","Permanent home for businesses","\"A permanent home for businesses.\""],
]
selfid=[["strategic middle / SMV / LMV / leveraged micro",0,"coined names — never self-used"],
 ["search fund",8,"real self-label"],["patient capital",5,"real self-label"],
 ["revenue-based",5,"real (undercounted)"],["venture studio",5,"real self-label"],
 ["steward",2,"real self-label"],["evergreen",2,"real self-label"],
 ["sovereign",1,"real (undercounted)"],["permanent equity",0,"real (exact-match undercount)"]]
DATA=json.dumps({"phrases":phrases,"clusters":clusters,"verdicts":verdicts,"newents":newents,"selfid":selfid})
html = """<!DOCTYPE html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Post-Unicorn Finance — Self-Description Terms Atlas</title><style>
:root{--bg:#0f1115;--card:#171a21;--ink:#e7e9ee;--mut:#9aa3b2;--acc:#6ea8fe;--good:#4ade80;--warn:#fbbf24;--bad:#f87171;--line:#262b35}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.55 -apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:1100px;margin:0 auto;padding:28px 20px 80px}
h1{font-size:25px;margin:0 0 4px}h2{font-size:18px;margin:34px 0 12px;border-bottom:1px solid var(--line);padding-bottom:6px}
.sub{color:var(--mut);margin:0 0 8px}.pill{display:inline-block;font-size:11px;padding:2px 8px;border-radius:20px;background:#222836;color:var(--mut);margin-right:6px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:10px 0}
table{width:100%;border-collapse:collapse;font-size:13.5px}th,td{text-align:left;padding:8px 10px;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--mut);font-weight:600;cursor:pointer;user-select:none}tr:hover td{background:#1b1f28}
.tag{font-size:11px;font-weight:700;padding:2px 7px;border-radius:6px;white-space:nowrap}
.v-good{background:#10331f;color:var(--good)}.v-warn{background:#332a10;color:var(--warn)}.v-bad{background:#331515;color:var(--bad)}
input{background:#0c0e12;border:1px solid var(--line);color:var(--ink);padding:8px 11px;border-radius:8px;width:100%;max-width:340px;margin-bottom:10px}
.bar{height:8px;background:#222836;border-radius:6px;overflow:hidden;min-width:80px}.bar>i{display:block;height:100%;background:var(--acc)}
.cl{border-left:3px solid var(--acc);padding-left:12px;margin:12px 0}.cl b{font-size:15px}.terms{color:var(--acc);font-size:12.5px}.mem{color:var(--mut);font-size:12.5px}
.kv{font-family:ui-monospace,monospace;font-size:12px}.q{color:var(--mut);font-style:italic}.note{color:var(--mut);font-size:12.5px}
a{color:var(--acc);text-decoration:none}</style></head><body><div class=wrap>
<h1>Post-Unicorn Finance — Self-Description Terms Atlas</h1>
<p class=sub>How non-unicorn capital entities describe <b>themselves</b>, mined from 109 captured web pages + structured descriptors across 169 atlas entities. Generated 2026-05-27. Every term traces to real captured/fetched text.</p>
<p><span class=pill>169 entities</span><span class=pill>106 fetched domains</span><span class=pill>91 clusters</span><span class=pill>200 top phrases</span><span class=pill>7 new web entities</span></p>

<h2>Did the coined classes show up in how entities describe themselves?</h2>
<div class=card><table id=verd><thead><tr><th>Placeholder class</th><th>Verdict</th><th>Cluster evidence</th><th>Shared self-language</th></tr></thead><tbody></tbody></table></div>

<h2>Self-identification evidence — do entities use the class name?</h2>
<p class=note>Count of the 106 fetched entity pages whose own text contains the label. Coined names score 0; real-world labels appear. (Exact-string match undercounts hyphen/spacing variants.)</p>
<div class=card><table id=sid><thead><tr><th>Label</th><th>Pages</th><th></th><th>Type</th></tr></thead><tbody></tbody></table></div>

<h2>Recurring multi-word self-description phrases</h2>
<input id=q placeholder="filter phrases… (e.g. permanent, revenue, search, steward)">
<div class=card><table id=ph><thead><tr><th data-k=p>phrase</th><th data-k=e>entities ▾</th><th data-k=o>occurrences</th></tr></thead><tbody></tbody></table></div>

<h2>Emergent clusters (size ≥ 3)</h2>
<div id=cl></div>

<h2>New entities discovered on the open web (grounded)</h2>
<p class=note>A coherent Permanent / Steward / Evergreen identity currently split across three placeholder buckets.</p>
<div class=card><table id=ne><thead><tr><th>Entity</th><th>Site</th><th>Self-described as</th><th>Verbatim / source</th></tr></thead><tbody></tbody></table></div>

<p class=note style="margin-top:30px">Sources include entities' own websites (e.g. everhold.com, purpose-economy.org) and the atlas <span class=kv>source_pages</span> corpus. Coined-label counts: <span class=kv>strategic middle / SMV / LMV = 0 / 106</span>.</p>
</div><script>
const D=__DATA__;
function tag(v){let c='v-warn';if(/VALIDATED/.test(v))c='v-good';if(/UMBRELLA|PREMATURE/.test(v))c='v-bad';return '<span class="tag '+c+'">'+v+'</span>'}
document.querySelector('#verd tbody').innerHTML=D.verdicts.map(r=>`<tr><td><b>${r[0]}</b></td><td>${tag(r[1])}</td><td class=note>${r[2]}</td><td class=terms>${r[3]}</td></tr>`).join('');
const mx=Math.max(...D.selfid.map(r=>r[1]))||1;
document.querySelector('#sid tbody').innerHTML=D.selfid.map(r=>`<tr><td>${r[0]}</td><td class=kv>${r[1]}</td><td><div class=bar><i style="width:${100*r[1]/mx}%"></i></div></td><td class=note>${r[2]}</td></tr>`).join('');
let phs=D.phrases.slice(),sk='e',sd=-1;
function rph(){let q=document.getElementById('q').value.toLowerCase();let rows=phs.filter(x=>x.p.includes(q));rows.sort((a,b)=> sd*((sk=='p')?(a.p<b.p?-1:1):(b[sk]-a[sk])) );document.querySelector('#ph tbody').innerHTML=rows.slice(0,120).map(x=>`<tr><td>${x.p}</td><td class=kv>${x.e}</td><td class=kv>${x.o}</td></tr>`).join('')}
document.getElementById('q').oninput=rph;
document.querySelectorAll('#ph th').forEach(th=>th.onclick=()=>{let k=th.dataset.k;if(k==sk)sd*=-1;else{sk=k;sd=(k=='p')?1:-1}rph()});
rph();
document.getElementById('cl').innerHTML=D.clusters.map((c,i)=>`<div class=card><div class=cl><b>C${c.cluster} — ${c.size} entities</b><div class=terms>${c.shared.join(' · ')}</div><div class=mem>${c.mem.join(', ')}</div><div class=note>placeholder mix: ${Object.entries(c.placeholder_mix).map(([k,v])=>k+':'+v).join('  ')}</div></div></div>`).join('');
document.querySelector('#ne tbody').innerHTML=D.newents.map(r=>`<tr><td><b>${r[0]}</b></td><td><a href="https://${r[1]}" target=_blank>${r[1]}</a></td><td>${r[2]}</td><td class=q>${r[3]}</td></tr>`).join('');
</script></body></html>"""
html=html.replace("__DATA__",DATA)
out=ROOT/"site"/"self_description_terms_atlas.html"
out.write_text(html,encoding="utf-8")
print("wrote",out,f"({len(html):,} bytes)")
