"""Inject curated firms -> verify through the SAME gate -> promote -> identity-audit.

Usage:  python scripts/inject_and_promote.py <firms.json> <round_tag>

firms.json: {"firms":[{"name","website","asset_class","entity_type","evidence_quote"?}]}

Pipeline per run (CSV is authority; DB is cache):
  1. dedupe vs existing entities+queue, append new leads to entity_intake_queue.csv + source_registry.csv
  2. import_csvs(reset=False) so the DB matches the CSVs (preserves source_pages fetch cache)
  3. fetch-sources -> extract-claims -> promote-intake  (the existing, unchanged gate)
  4. identity audit: every entity promoted this run must have a DISTINCTIVE (non-generic, non-vocabulary)
     name token present in its fetched homepage text; failures are demoted to review_status=needs_review
     and removed from industry_entities.csv. This closes the any-token identity hole without touching the gate.
"""
from __future__ import annotations
import csv, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import research_agents as ra
from atlas_sqlite import import_csvs, open_db

EV = ROOT / "data" / "evidence"
INTAKE = EV / "entity_intake_queue.csv"
SOURCES = EV / "source_registry.csv"
ENTITIES = EV / "industry_entities.csv"
CLAIMS = EV / "entity_claims.csv"

# Build the vocabulary set (asset-class keywords) so identity tokens exclude generic vocab words.
VOCAB = set()
for _kws in ra.CLASS_KEYWORDS.values():
    for _k in _kws:
        for _t in re.findall(r"[a-z0-9]+", _k.lower()):
            if len(_t) >= 3:
                VOCAB.add(_t)


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read(path):
    with path.open(encoding="utf-8") as f:
        r = csv.DictReader(f)
        return r.fieldnames, list(r)


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def distinctive_tokens(name):
    return [t for t in ra.significant_tokens(name) if t not in VOCAB]


def inject(firms, round_tag):
    intake_fields, intake_rows = read(INTAKE)
    src_fields, src_rows = read(SOURCES)
    _, ent_rows = read(ENTITIES)

    existing_names = {ra.normalize_name(r.get("name", "")) for r in intake_rows + ent_rows}
    existing_keys = {(ra.normalize_name(r.get("name", "")), ra.domain(r.get("website", ""))) for r in intake_rows + ent_rows}
    existing_src = {r["source_url"] for r in src_rows}
    today = now_iso()[:10]
    added = 0
    for fm in firms:
        name, website = fm.get("name", "").strip(), fm.get("website", "").strip()
        ac, et = fm.get("asset_class", "").strip(), fm.get("entity_type", "").strip()
        if not name or not website or ac not in ra.AUTO_PROMOTION_ASSET_CLASSES:
            continue
        n, d = ra.normalize_name(name), ra.domain(website)
        if n in existing_names or (n, d) in existing_keys:
            continue
        quote = (fm.get("evidence_quote", "") or "").replace("\n", " ").strip()
        intake_rows.append({
            "lead_id": ra.make_id(f"intake-{round_tag}", n, d), "name": name,
            "lead_type": "manual_curation", "website": website, "source_urls": website,
            "discovered_from": f"manual:claude_curation_{round_tag}_{today}",
            "target_asset_class": ac, "target_entity_type": et, "active_status": "active",
            "source_tier": "public_web", "priority": "high", "evidence_status": "needs_verification",
            "review_status": "queued", "created_at": today,
            "notes": f"Curated {round_tag} on {today}. Homepage quote: {quote[:200]}",
        })
        existing_names.add(n); existing_keys.add((n, d))
        if website not in existing_src:
            src_rows.append({
                "source_url": website, "source_name": f"{name} official site",
                "source_type": "official_site", "source_quality": "primary",
                "license_or_access": "public web",
                "notes": f"Curated {round_tag} by claude session.", "last_checked": today,
            })
            existing_src.add(website)
        added += 1
    write(INTAKE, intake_fields, intake_rows)
    write(SOURCES, src_fields, src_rows)
    return added


MIN_PAGE_CHARS = 400  # below this the homepage is JS-only/thin -> cannot verify, so do NOT demote


def identity_audit(new_names_norm):
    """Audit ONLY entities promoted in the current round (new_names_norm = set of normalized names).

    Demote an entity to needs_review ONLY when its homepage was fetched with substantial text AND
    none of its distinctive (non-generic, non-vocabulary) name tokens appear in that text. Thin/JS-only
    or unfetched pages are left in place (unverifiable != fabricated) so we never retroactively nuke
    real firms. This is an anti-hallucination guard for fresh AI-sourced leads, not a global purge.
    """
    if not new_names_norm:
        return []
    ent_fields, ent_rows = read(ENTITIES)
    intake_fields, intake_rows = read(INTAKE)
    with open_db(ra.DEFAULT_DB) as c:
        by_dom = {}
        for row in c.execute("SELECT source_url,title,raw_text FROM source_pages WHERE fetch_status='ok'"):
            txt = (row["title"] or "") + " " + (row["raw_text"] or "")
            by_dom.setdefault(ra.domain(row["source_url"]), txt)
    demoted, keep = [], []
    for e in ent_rows:
        nn = ra.normalize_name(e.get("name", ""))
        if nn not in new_names_norm:
            keep.append(e)
            continue
        dtok = distinctive_tokens(e.get("name", ""))
        txt = by_dom.get(ra.domain(e.get("website", "")), "")
        # cannot verify thin/missing pages -> keep (do not demote)
        if not dtok or len(txt.strip()) < MIN_PAGE_CHARS:
            keep.append(e)
            continue
        if any(t in txt.lower() for t in dtok):
            keep.append(e)
        else:
            demoted.append(e["name"])
    if demoted:
        write(ENTITIES, ent_fields, keep)
        kept_ids = {e["entity_id"] for e in keep}
        # sweep claims for demoted entities so we never leave FK-breaking orphan claims
        cl_fields, cl_rows = read(CLAIMS)
        cl_keep = [c for c in cl_rows if not c.get("entity_id") or c["entity_id"] in kept_ids]
        if len(cl_keep) != len(cl_rows):
            write(CLAIMS, cl_fields, cl_keep)
        dset = {ra.normalize_name(n) for n in demoted}
        for r in intake_rows:
            if ra.normalize_name(r.get("name", "")) in dset:
                r["review_status"] = "needs_review"
                r["notes"] = (r.get("notes", "") + " | identity-audit: distinctive name token absent from a substantial homepage; needs human check").strip()
        write(INTAKE, intake_fields, intake_rows)
    return demoted


def main():
    firms_path = Path(sys.argv[1])
    round_tag = sys.argv[2] if len(sys.argv) > 2 else "roundX"
    data = json.loads(firms_path.read_text(encoding="utf-8"))
    firms = data.get("firms", data) if isinstance(data, dict) else data

    def count_entities():
        with ENTITIES.open(encoding="utf-8") as f:
            return sum(1 for _ in f) - 1

    def entity_names():
        with ENTITIES.open(encoding="utf-8") as f:
            return {ra.normalize_name(r["name"]) for r in csv.DictReader(f)}

    before = count_entities()
    before_names = entity_names()
    added = inject(firms, round_tag)
    print(f"[{round_tag}] candidates={len(firms)} injected_new={added} (entities before={before})")

    # Clear FK-bearing derived/cache tables before a cache-preserving re-import. Across rounds these
    # accumulate references to entity/claim rows that get re-imported, which trips
    # "FOREIGN KEY constraint failed" on commit. source_pages (the fetch cache, no FK to CSV tables)
    # and agent_runs are preserved so we never re-fetch.
    with open_db(ra.DEFAULT_DB) as _c:
        for _t in ("intake_promotion_reviews", "review_feedback", "claim_reviews",
                   "classification_suggestions", "discovery_candidates", "evolution_proposals"):
            try:
                _c.execute(f"DELETE FROM {_t}")
            except Exception:
                pass
        _c.commit()
    import_csvs(ra.DEFAULT_DB, reset=False)
    ra.source_fetch_agent(ra.DEFAULT_DB, verified_only=False, limit=max(400, added * 3))
    ra.claim_extraction_agent(ra.DEFAULT_DB, limit=1000)
    ra.promote_intake_agent(ra.DEFAULT_DB, limit=1000)

    after_promote = count_entities()
    new_names = entity_names() - before_names
    demoted = identity_audit(new_names)
    after = count_entities()
    print(f"[{round_tag}] promoted={after_promote - before} demoted_by_identity_audit={len(demoted)} -> net_new={after - before}")
    if demoted:
        print("  demoted:", ", ".join(demoted))
    print(f"[{round_tag}] TOTAL ENTITIES NOW = {after}")


if __name__ == "__main__":
    sys.exit(main())
