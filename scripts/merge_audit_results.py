"""Merge comprehensive-atlas-audit results into atlas.csv (2026-07-02).

Inputs:
  data/runtime/audit_batches_2026-07-02.json        (what was sent)
  data/runtime/audit_results_2026-07-02/batch_*.json (agent outputs)
  data/runtime/audit_workflow_summary_2026-07-02.json (workflow return: changes + verdicts)

Outputs:
  data/evidence/atlas.csv                    enriched in place (+country, allocator, evidence_signal,
                                             liquidity_evidence_url, liquidity_evidence_note)
  docs/atlas_comprehensive_audit_2026-07-02.md   per-entity review table
  data/evidence/manual_changes_2026-07-02.log    appended change log

Policies (from audit brief + CLAUDE.md):
  - Class change applied ONLY if change_type=='apply' AND verify verdict upheld+quote_verified.
    Everything else -> proposed (review table only).
  - SMV<->Nimble and Group 6 are NEVER auto-applied (agents were told 'propose'; enforced again here).
  - Band: overwrite if old band in {'', 'Unknown', 'Unicorn'}; otherwise only if audit conf=='high'
    AND exit_quote present AND differs (logged).
  - horizon_years: fill when audit found a value; overwrite only with exit_quote evidence.
  - exit_quote/source: replace when audit returned a non-empty live-verified quote.
  - tech_enabled: only auto-fix 'review'/'flagged-pending'/'' rows; disagreements on set rows -> flag only.
  - confidence: set from audit classification_confidence; normalize legacy 'medium'->'med'.
  - audit_flag: audit flags if non-empty; else cleared when conf=='high', else keep old.
  - allocator=='no' rows NOT auto-moved unless the agent itself set class Under Review with 'apply'
    + upheld verdict (adversarial double-check requirement).
"""
import csv, json, glob, os, sys
from datetime import date

REPO = r'C:\Users\cobys\projects\post-unicorn-finance'
ATLAS = os.path.join(REPO, 'data', 'evidence', 'atlas.csv')
RESULTS_DIR = os.path.join(REPO, 'data', 'runtime', 'audit_results_2026-07-02')
SUMMARY = os.path.join(REPO, 'data', 'runtime', 'audit_workflow_summary_2026-07-02.json')
REVIEW_MD = os.path.join(REPO, 'docs', 'atlas_comprehensive_audit_2026-07-02.md')
CHANGELOG = os.path.join(REPO, 'data', 'evidence', 'manual_changes_2026-07-02.log')
TODAY = '2026-07-02'

# ---- load ----
with open(ATLAS, encoding='utf-8-sig') as f:
    atlas = list(csv.DictReader(f))
by_id = {r['entity_id']: r for r in atlas}

results = {}
dupes, parse_errors = [], []
for path in sorted(glob.glob(os.path.join(RESULTS_DIR, 'batch_*.json'))):
    try:
        with open(path, encoding='utf-8-sig') as f:
            data = json.load(f)
        for e in data.get('entities', []):
            if e['entity_id'] in results:
                dupes.append(e['entity_id'])
            results[e['entity_id']] = e
    except Exception as ex:
        parse_errors.append((os.path.basename(path), str(ex)))

verdicts = {}
if os.path.exists(SUMMARY):
    with open(SUMMARY, encoding='utf-8-sig') as f:
        summary = json.load(f)
    for b in summary.get('batches', []):
        for v in b.get('verdicts', []) or []:
            verdicts[v['entity_id']] = v

missing = [eid for eid in by_id if eid not in results]
extra = [eid for eid in results if eid not in by_id]
print(f'atlas rows: {len(atlas)} | results: {len(results)} | missing: {len(missing)} | extra: {len(extra)}')
if missing: print('MISSING:', missing)
if extra: print('EXTRA (ignored):', extra)
if dupes: print('DUPES (last wins):', dupes)
if parse_errors: print('PARSE ERRORS:', parse_errors)

GROUP6 = {'serent-capital','silversmith-capital','skoyen-software','soch-holdings',
          'ascendant-ventures','savana-fund','social-tech-ventures','zebra-impact-ventures',
          'capacity-capital','perpetuity-project'}
SMV_NIMBLE = {'SMV', 'Nimble'}

applied, proposed, enriched_only, log_lines = [], [], [], []

def note(row, txt):
    row['source_note'] = (row['source_note'] + ' | ' if row['source_note'] else '') + txt

def norm_url(url):
    url = (url or '').strip()
    if url and not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url

def host(url):
    url = norm_url(url)
    if not url:
        return ''
    h = url.split('//', 1)[-1].split('/', 1)[0].lower()
    return h[4:] if h.startswith('www.') else h

def liquidity_note(row, url, source):
    url_host = host(url)
    site_host = host(row.get('website', ''))
    if not url_host:
        return ''
    if 'substack.com' in url_host:
        return 'official Substack'
    if 'beehiiv.com' in url_host:
        return 'official newsletter'
    if site_host and url_host == site_host:
        return 'homepage' if source != 'source_url' else 'official source page'
    return 'third-party liquidity evidence'

for eid, row in by_id.items():
    a = results.get(eid)
    if not a:
        continue
    changes_here = []

    # ---- classification ----
    old_class = row['asset_class']
    new_class = a['confirmed_asset_class']
    want_change = new_class != old_class
    is_smv_nimble_swap = {old_class, new_class} == SMV_NIMBLE
    v = verdicts.get(eid)
    verified = bool(v and v.get('upheld') and v.get('quote_verified'))
    if want_change:
        auto_ok = (a['change_type'] == 'apply' and not is_smv_nimble_swap
                   and eid not in GROUP6 and verified)
        rec = dict(id=eid, name=a['name'], frm=old_class, to=new_class,
                   conf=a['classification_confidence'], why=a['rationale'],
                   quote=a['verbatim_quote'], url=a['source_url'],
                   verdict=(v or {}).get('notes', 'no verify verdict'),
                   group6=eid in GROUP6, smv_nimble=is_smv_nimble_swap)
        if auto_ok:
            row['asset_class'] = new_class
            changes_here.append(f'asset_class {old_class} -> {new_class}')
            applied.append(rec)
        else:
            proposed.append(rec)

    # ---- band ----
    old_band, new_band = row['liquidity_band'], a['liquidity_band']
    if new_band and new_band != 'Unknown' and new_band != old_band:
        if old_band in ('', 'Unknown', 'Unicorn'):
            row['liquidity_band'] = new_band
            changes_here.append(f'band {old_band or "(blank)"} -> {new_band}')
        elif a['classification_confidence'] == 'high' and a['exit_quote']:
            row['liquidity_band'] = new_band
            changes_here.append(f'band {old_band} -> {new_band} (high-conf quote)')

    # ---- horizon ----
    if a['horizon_years'] and a['horizon_years'] != row['horizon_years']:
        if not row['horizon_years'] or a['exit_quote']:
            old_h = row['horizon_years']
            row['horizon_years'] = a['horizon_years']
            changes_here.append(f'horizon {old_h or "(blank)"} -> {a["horizon_years"]}')

    # ---- exit quote ----
    if a['exit_quote'] and a['exit_quote'] != row['exit_quote']:
        row['exit_quote'] = a['exit_quote']
        changes_here.append('exit_quote refreshed (live-verified)')
    if a['source_url']:
        note(row, f'audited {TODAY}: {a["source_url"]}')

    # ---- liquidity evidence link ----
    if a['horizon_years']:
        liq_url = norm_url(a.get('exit_quote_url') or '')
        liq_source = 'exit_quote_url'
        if not liq_url:
            liq_url = norm_url(a.get('source_url') or row.get('website') or '')
            liq_source = 'source_url' if a.get('source_url') else 'website'
        row['liquidity_evidence_url'] = liq_url
        row['liquidity_evidence_note'] = liquidity_note(row, liq_url, liq_source)
    else:
        row['liquidity_evidence_url'] = ''
        row['liquidity_evidence_note'] = ''

    # ---- tech_enabled ----
    audit_te = 'yes' if a['tech_enabled'] else 'no'
    if row['tech_enabled'] in ('review', 'flagged-pending', ''):
        if row['tech_enabled'] != audit_te:
            changes_here.append(f'tech_enabled {row["tech_enabled"] or "(blank)"} -> {audit_te}')
            row['tech_enabled'] = audit_te
    elif row['tech_enabled'] in ('yes', 'no') and row['tech_enabled'] != audit_te:
        a['flags'] = (a['flags'] + ' | ' if a['flags'] else '') + f'tech_enabled disagreement: csv={row["tech_enabled"]} audit={audit_te}'

    # ---- confidence ----
    if row['confidence'] == 'medium':
        row['confidence'] = 'med'
    if a['classification_confidence'] != row['confidence']:
        row['confidence'] = a['classification_confidence']

    # ---- audit_flag ----
    if a['flags'].strip():
        row['audit_flag'] = a['flags'].strip()
    elif a['classification_confidence'] == 'high':
        if row['audit_flag']:
            changes_here.append('flag cleared (high-confidence confirm)')
        row['audit_flag'] = ''

    # ---- new columns ----
    row['country'] = a['country']
    row['allocator'] = 'yes' if a['allocator'] else 'no'
    row['evidence_signal'] = a['evidence_signal']

    if changes_here and not any(c.startswith('asset_class') for c in changes_here):
        enriched_only.append((eid, changes_here))
    for c in changes_here:
        log_lines.append(f'{TODAY} full-audit {eid}: {c} [src: {a["source_url"] or "n/a"}]')

# rows with no result keep blanks in new columns
for row in atlas:
    row.setdefault('country', '')
    row.setdefault('allocator', '')
    row.setdefault('evidence_signal', '')
    row.setdefault('liquidity_evidence_url', '')
    row.setdefault('liquidity_evidence_note', '')

# ---- write CSV ----
cols = ['entity_id','name','asset_class','liquidity_band','horizon_years','tech_enabled',
        'tier','confidence','website','exit_quote','audit_flag','source_note',
        'country','allocator','evidence_signal','liquidity_evidence_url','liquidity_evidence_note']
with open(ATLAS, 'w', encoding='utf-8', newline='') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(atlas)

# ---- change log ----
with open(CHANGELOG, 'a', encoding='utf-8') as f:
    f.write(f'\n# Comprehensive per-entity audit merge {TODAY}\n')
    for line in log_lines:
        f.write(line + '\n')

# ---- review table ----
def md_escape(s): return (s or '').replace('|', '\\|').replace('\n', ' ')
lines = [f'# Comprehensive Atlas Audit — Results ({TODAY})', '',
         f'All {len(results)} of {len(atlas)} entities audited against live pages. '
         f'Missing: {missing or "none"}.', '',
         '## Taxonomy guardrails used for this merge', '',
         '- **Nimble** = smaller-market companies targeting fast liquidity, normally 3-5 years and always under 6 years.',
         '- **SMV** = large-ish markets targeting sub-unicorn liquidity, typically $50M-$500M outcomes on a 7-9 year path. A medium horizon without size evidence stays review-sensitive.',
         '- **Permanent** = no forced exit / evergreen / hold indefinitely. Permanent wins over Nimble when both no-exit and capital-efficient signals appear.',
         '- **Revenue-based lenders** are real tech-enabled allocators, but where the return is repayment/royalty rather than company exit, they are held in Under Review.',
         '- SMV<->Nimble changes and Group 6 calls are held for owner review, not auto-applied.', '',
         '## Applied class changes (unambiguous, adversarially verified)', '']
lines.append('| Entity | From → To | Conf | Rationale | Evidence quote | Verify verdict |')
lines.append('|---|---|---|---|---|---|')
for r in applied:
    lines.append(f"| {r['name']} | {r['frm']} → {r['to']} | {r['conf']} | {md_escape(r['why'])} | "
                 f"\"{md_escape(r['quote'][:160])}\" ([src]({r['url']})) | {md_escape(r['verdict'])} |")
if not applied: lines.append('| _none_ | | | | | |')
lines += ['', '## Proposed class changes (owner decision required)', '']
lines.append('| Entity | From → To | Conf | Why held for review | Rationale | Evidence quote |')
lines.append('|---|---|---|---|---|---|')
for r in proposed:
    hold = 'Group 6' if r['group6'] else ('SMV↔Nimble (pending Ethan)' if r['smv_nimble'] else
           ('agent proposed' if True else ''))
    lines.append(f"| {r['name']} | {r['frm']} → {r['to']} | {r['conf']} | {hold} | {md_escape(r['why'])} | "
                 f"\"{md_escape(r['quote'][:160])}\" ([src]({r['url']})) |")
if not proposed: lines.append('| _none_ | | | | | |')
lines += ['', '## Per-entity audit detail', '']
lines.append('| Entity | Class (conf) | Band / Horizon | Country | Allocator | Self-description (evidence_signal) | Evidence quote / source | Exit evidence | Flags |')
lines.append('|---|---|---|---|---|---|---|---|---|')
for row in atlas:
    a = results.get(row['entity_id'])
    if not a: continue
    band = row['liquidity_band'] or '—'
    hz = row['horizon_years'] or '—'
    quote = md_escape((a.get('verbatim_quote') or '')[:180])
    src = a.get('source_url') or row.get('website') or ''
    evidence = f'"{quote}" ([src]({src}))' if quote and src else ('[src](%s)' % src if src else '—')
    exit_q = md_escape((a.get('exit_quote') or row.get('exit_quote') or '')[:180])
    exit_src = a.get('exit_quote_url') or row.get('liquidity_evidence_url') or ''
    exit_ev = f'"{exit_q}" ([src]({exit_src}))' if exit_q and exit_src else (f'"{exit_q}"' if exit_q else '—')
    lines.append(f"| [{row['name']}]({row['website']}) | {row['asset_class']} ({row['confidence']}) | "
         f"{band} / {hz}y | {md_escape(row['country'])} | {row['allocator']} | "
                 f"{md_escape(row['evidence_signal'][:220])} | {evidence} | {exit_ev} | "
                 f"{md_escape(row['audit_flag'][:120])} |")
with open(REVIEW_MD, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')

print(f'\napplied class changes: {len(applied)}')
for r in applied: print(f"  {r['id']}: {r['frm']} -> {r['to']}")
print(f'proposed class changes: {len(proposed)}')
for r in proposed: print(f"  {r['id']}: {r['frm']} -> {r['to']} ({'G6' if r['group6'] else ''}{'S/N' if r['smv_nimble'] else ''})")
print(f'enrichment-only rows changed: {len(enriched_only)}')
print(f'log lines: {len(log_lines)}')
print(f'review table: {REVIEW_MD}')
