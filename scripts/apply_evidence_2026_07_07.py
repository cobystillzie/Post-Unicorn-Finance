# Apply the 2026-07-07 evidence-hardening edits salvaged from the completed
# evidence-hardening workflow (impro re-fetch, Siena/White Whale first-party
# re-source, lighter-capital band fill, d2/gorilla flag-strengthen).
# Rewrites data/evidence/atlas.csv in place and appends to manual_changes_2026-07-07.log.
import csv
import os

REPO = r'C:\Users\cobys\projects\post-unicorn-finance'
CSV = os.path.join(REPO, 'data', 'evidence', 'atlas.csv')
LOG = os.path.join(REPO, 'data', 'evidence', 'manual_changes_2026-07-07.log')
TODAY = '2026-07-07'

IMPRO_QUOTE = ("We amplify the outcome by believing early, supporting with integrity, while "
               "providing with innovative growth strategies that save cashburn as well as "
               "preserve the ownership in the founders' hands.")
IMPRO_FLAG = (
    "OWNER-DIRECTED SMV / in_disguise (Ethan in-disguise vouch, 2026-06-06, alongside Startup Ignition). "
    "Live page fetched 2026-07-07 via Exa (site 403s normal fetch; Playwright bridge unavailable): reads as "
    "emerging-markets (Africa/LATAM/SEA) pre-seed-to-Series A impact VC screening for 'category definer or "
    "global scalability' with team bios citing 'scaling startups to unicorn status' - NO post-unicorn / "
    "sub-unicorn / anti-power-law signal. The exit_quote shown is the firm's real M&A/ownership-preservation "
    "line and does NOT support SMV. Classification kept per owner directive; confidence=low; "
    "CONFLICT FLAGGED FOR OWNER REVIEW.")

SIENA_QUOTE = ("Exit potential within 3-5 years. We expect to see a clear path to the final liquidity "
               "event either as M&A or IPO.")
SIENA_FLAG = ("secondary_fund_review: RE-SOURCED FIRST-PARTY 2026-07-07 - exact 3-5y final-exit horizon now "
              "verified on the firm's own /vision page (previously rested on a GP interview).")

WW_QUOTE = "Navigate towards IPO-ready companies with clear exit timelines within 36 months."
WW_FLAG = ("secondary_fund_review: RE-SOURCED FIRST-PARTY 2026-07-07 - the <=36-month exit timeline is now "
           "verified on the firm's own /secondaries-funds page ('Exit Visibility' card). The 18-month lower "
           "bound of the 1.5-3y range remains sourced only to the Inc42 article.")

LIGHTER_NOTE = ("first-party FAQ: \"you pay a fixed percentage of topline revenue until the total repayment "
                "cap is reached. The repayment cap varies between 1.3-1.5X the funded amount\"; RBF terms "
                "typically 3y, up to 4y. Band filled 2026-07-07 (asset_class still Under Review).")
LIGHTER_FLAG_APPEND = (" | 2026-07-07 band fill: liquidity_band=SMV, horizon 3-4y from first-party FAQ "
                       "(revenue-based repayment, 1.3-1.5x cap); asset_class ruling still pending.")

D2_FLAG_APPEND = (" | 2026-07-07 band research (Sifted launch article, third-party): D2's 'Hero' instrument "
                  "is revenue-based financing - ~5% of revenue for 5y if the founder opts out of raising - "
                  "with explicit sub-unicorn framing ('half the portfolio makes 1-2x... we don't need the "
                  "next Google'). This points to an SMV-style band, which CONFLICTS with the committed "
                  "asset_class=Nimble; band left Unknown pending owner reconciliation of class vs band.")

GORILLA_FLAG_APPEND = (" | 2026-07-07 band research (firm-authored ArcticStartup article, 'By Gorilla "
                       "Capital'): designs for sub-unicorn exits ('median exit ~EUR15M... build a cap table "
                       "that works even if the exit lands at EUR15M') AND explicitly rejects engineered exit "
                       "timing ('not one that needs to sell in two years or die trying') - i.e. SMV-style, "
                       "NOT Nimble's <=6y engineered liquidity. Points to SMV band, CONFLICTS with "
                       "asset_class=Nimble; band left Unknown pending owner reconciliation.")

# entity_id -> {field: new_value}; key '__append_audit_flag__' appends to existing audit_flag
EDITS = {
    'impro-ventures': {
        'asset_class': 'SMV',
        'tier': 'in_disguise',
        'confidence': 'low',
        'exit_quote': IMPRO_QUOTE,
        'audit_flag': IMPRO_FLAG,
        'liquidity_evidence_url': 'https://impro.ventures/',
        'liquidity_evidence_note': 'firm site homepage, fetched via Exa 2026-07-07 (site 403s normal fetch)',
    },
    'siena-secondary-fund': {
        'exit_quote': SIENA_QUOTE,
        'confidence': 'high',
        'audit_flag': SIENA_FLAG,
        'liquidity_evidence_url': 'https://siena.ee/vision',
        'liquidity_evidence_note': 'first-party (firm site /vision)',
    },
    'white-whale-secondaries-fund': {
        'exit_quote': WW_QUOTE,
        'audit_flag': WW_FLAG,
        'liquidity_evidence_url': 'https://www.whitewhale.in/secondaries-funds',
        'liquidity_evidence_note': 'first-party (firm site /secondaries-funds); 36mo upper bound firm-stated, 18mo lower bound from Inc42',
    },
    'lighter-capital': {
        'liquidity_band': 'SMV',
        'horizon_years': '3-4',
        'liquidity_evidence_url': 'https://www.lightercapital.com/faq',
        'liquidity_evidence_note': LIGHTER_NOTE,
        '__append_audit_flag__': LIGHTER_FLAG_APPEND,
    },
    'd2-fund': {
        '__append_audit_flag__': D2_FLAG_APPEND,
    },
    'gorilla-capital': {
        '__append_audit_flag__': GORILLA_FLAG_APPEND,
    },
}

with open(CSV, encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

log_lines = [f'# manual_changes {TODAY} - evidence hardening (Ethan feedback item B + D)', '']
changed = 0
for r in rows:
    eid = r['entity_id']
    if eid not in EDITS:
        continue
    changed += 1
    for field, val in EDITS[eid].items():
        if field == '__append_audit_flag__':
            r['audit_flag'] = r['audit_flag'] + val
            log_lines.append(f'{eid} :: audit_flag APPEND :: {val.strip()[:120]}...')
        else:
            old = r.get(field, '')
            r[field] = val
            log_lines.append(f'{eid} :: {field} :: {old!r} -> {val!r}')
    log_lines.append('')

with open(CSV, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

with open(LOG, 'a', encoding='utf-8') as f:
    f.write('\n'.join(log_lines) + '\n')

print(f'Applied edits to {changed} rows. Log -> {LOG}')
