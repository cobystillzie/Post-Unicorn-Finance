import csv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; EV=ROOT/"data"/"evidence"
# ---- existing names for dedup ----
ent={r["name"].lower() for r in csv.DictReader(open(EV/"industry_entities.csv"))}
iq_path=EV/"entity_intake_queue.csv"
iq_rows=list(csv.DictReader(open(iq_path)))
iq_fields=iq_rows[0].keys() if iq_rows else None
existing={r["name"].lower() for r in iq_rows}|ent

NEW=[
 # name, website, target_asset_class, target_entity_type, evidence_status, source_urls, notes
 ("Everhold","https://www.everhold.com/","Patient Capital","permanent-equity holding company","candidate_evidence","https://www.everhold.com/","Self-described (fetched 2026-05-27): 'We buy businesses. And hold them forever... We're not a private equity firm... we use permanent capital.' Founder-led B2B, $500K-2M EBITDA, vertical SaaS/services. Permanent/steward/evergreen cluster."),
 ("Purpose Evergreen Capital","https://purpose-economy.org/en/pec/","Patient Capital","evergreen / steward-ownership fund","candidate_evidence","https://purpose-economy.org/en/pec/","Self-described (fetched 2026-05-27): 'patient, value-aligned capital... evergreen investment fund without pressure to force an exit... invest without voting rights... return rate is capped.' EUR0.5-5M, ~EUR30M raised. Steward-ownership."),
 ("HOLD.co","https://hold.co/","Patient Capital","permanent-capital holding company","needs_verification","https://hold.co/blog/permanent-capital-holding-company-strategy","Search-discovered 2026-05-27; describes a permanent-capital holding-company strategy. Verify own-site self-description before promotion."),
 ("Upliift","https://upliift.com/","Patient Capital","permanent-equity acquirer","needs_verification","https://upliift.com/2026/04/01/permanent-equity-approach/","Search-discovered 2026-05-27; permanent-equity approach. Verify own-site text."),
 ("Bending Spoons","https://bendingspoons.com/","Portfolio Capital","acquire-and-hold software operator","needs_verification","https://techcrunch.com/2025/11/25/why-hold-forever-investors-are-snapping-up-venture-capital-zombies/","Search-discovered 2026-05-27; acquires & holds tech brands (Evernote, Vimeo, Meetup), 'no plans to sell.' Verify primary source."),
 ("Fund for Employee Ownership","https://www.evgoh.com/tfeo","Search/ETA","patient-capital employee-ownership acquirer","needs_verification","https://www.evgoh.com/tfeo","Search-discovered 2026-05-27; leverages patient capital to acquire SMBs and convert to employee ownership. SMB/EO-ETA sub-lane."),
 ("Evergreen (evergreensg.com)","https://www.evergreensg.com/","Patient Capital","permanent home for businesses","needs_verification","https://www.evergreensg.com/","Search-discovered 2026-05-27; 'A Permanent Home for Businesses.' Verify own-site self-description."),
]
added=[]
n=0
for name,site,ac,et,ev,src,notes in NEW:
    if name.lower() in existing: 
        print("skip (dup):",name); continue
    n+=1
    iq_rows.append({
        "lead_id":f"intake-web-2026-05-27-{n:03d}",
        "name":name,"lead_type":"web_discovery","website":site,
        "source_urls":src,"discovered_from":"claude_web_discovery:self_description_mining",
        "target_asset_class":ac,"target_entity_type":et,"active_status":"active",
        "source_tier":"public_web","priority":"high" if ev=="candidate_evidence" else "medium",
        "evidence_status":ev,"review_status":"pending","created_at":"2026-05-27","notes":notes,
    })
    added.append(name)
with open(iq_path,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=list(iq_fields)); w.writeheader(); w.writerows(iq_rows)
print("intake rows now:",len(iq_rows),"| added:",added)

# ---- scrape targets ----
st_path=EV/"scrape_targets.csv"
st_rows=list(csv.DictReader(open(st_path))); st_fields=list(st_rows[0].keys())
NEWT=[
 {"lane":"Permanent/Steward","target_asset_class":"Patient Capital","source_family":"public_web",
  "query":"permanent equity hold forever steward ownership evergreen fund acquire profitable businesses no forced exit",
  "seed_entities_or_sources":"Everhold;Permanent Equity;Purpose Evergreen Capital;HOLD.co;Tiny",
  "source_tier":"public_web","priority":"high","expected_fields":"name;website;capital_model;hold_period;liquidity_language",
  "notes":"Emergent permanent/steward/evergreen self-identity cluster (mined 2026-05-27); cuts across Patient/Portfolio/SMV placeholders."},
 {"lane":"Instrument","target_asset_class":"SMV","source_family":"public_web",
  "query":"embedded finance working capital revenue-based financing platform merchants small business non-dilutive",
  "seed_entities_or_sources":"Shopify Capital;PayPal Working Capital;Parafin;Liberis;YouLend",
  "source_tier":"public_web","priority":"medium","expected_fields":"provider;instrument;terms_language;target_customer",
  "notes":"Embedded-finance / working-capital self-described sub-group filed under SMV; track as instrument-provider class."},
 {"lane":"Portfolio Capital","target_asset_class":"Portfolio Capital","source_family":"public_web",
  "query":"venture studio company creation company formation studio equity venture builder vertical saas",
  "seed_entities_or_sources":"High Alpha;Pioneer Square Labs;Fractal Software;Team8;Expa",
  "source_tier":"public_web","priority":"medium","expected_fields":"name;website;studio_model;sector",
  "notes":"Studio / company-creation self-identity distinct from acquirers within Portfolio Capital."},
 {"lane":"Search/ETA","target_asset_class":"Search/ETA","source_family":"public_web",
  "query":"employee ownership acquire small business patient capital convert ESOP SMB owners sell business",
  "seed_entities_or_sources":"Teamshares;Mainshares;Acquira;Fund for Employee Ownership;Common Future",
  "source_tier":"public_web","priority":"medium","expected_fields":"name;website;searcher_profile;ownership_model",
  "notes":"SMB / employee-ownership ETA sub-lane (mined 2026-05-27)."},
]
for t in NEWT: st_rows.append({k:t.get(k,"") for k in st_fields})
with open(st_path,"w",newline="",encoding="utf-8") as f:
    w=csv.DictWriter(f,fieldnames=st_fields); w.writeheader(); w.writerows(st_rows)
print("scrape_targets rows now:",len(st_rows))
