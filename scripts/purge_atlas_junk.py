"""Phase 5a — Atlas cleanup: purge article-title/non-allocator junk + demote mega-PE.

Reversible: every removed/demoted row is logged to
data/evidence/junk_purge_log_2026-05-28.csv with a `reason` column.
"""
from __future__ import annotations
import csv
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / "data" / "evidence"
ENTITIES_PATH = EV / "industry_entities.csv"
INTAKE_PATH = EV / "entity_intake_queue.csv"
LOG_PATH = EV / "junk_purge_log_2026-05-28.csv"

# ----- entity_ids to DELETE from industry_entities.csv (obvious non-allocators) -----
DELETE_FROM_ENTITIES = {
    # article-title rows (not firms)
    "ai-startup-investment-roundups-2026",
    "b2b-software-company-buyers",
    "ifi-patient-capital-manifesto",
    "indie-hacker-success-stories-database",
    "investments",
    "roll-up-strategy-2026",
    "saas-valuation-multiples-2026",
    "search-fund-resources",
    "solo-founder-ai-tools",
    "the-quiet-rise-of-profitable-indie-hackers-in-2026",
    "vibe-coding-for-solo-founders-and-indie-hackers",
    "what-is-a-venture-studio-the-venture-studio-model-explained",
    "7-actionable-bootstrapped-saas-success-stories-playbooks-for-2025",
    "software-valuation-multiples",
    "explore-our-saas-m-a-deal-database",
    "the-fundless-sponsor-explained",
    "what-is-royalty-financing",
    "2025-plumbing-industry-report",
    "cloud-solutions-for-broadcast-ctv-and-fast",
    "sell-your-micro-saas",
    "learn-ai-for-entrepreneurs",
    "startup-studio-vs-venture-builder",
    "welcome-to-pathstone",
    "independent-sponsor-model",
    "local-government-software",
    "danantara-sovereign-ai-fund-launching",
    # generic terms / button text / acronyms
    "eta",
    "view-portfolio",
    "founder-programs",
    "b2b-bnpl",
    "funded",
    # tech corps misclassified as capital allocators
    "ibm",
    "salesforce",
    "motorola-solutions",
    "hawk-infinity-software",
    # SaaS products / blogs
    "trustmrr",
    "baremetrics",
    "bootstrappers",
    "saasplaybook",
    # individual commentators
    "peter-lohmann",
}

# ----- entity_ids to DEMOTE from entities → queue (mega-PE; reversible Ethan call) -----
DEMOTE_TO_QUEUE = {
    "bain-capital": "mega-pe-scope-review",
    "vista-equity-partners": "mega-pe-scope-review",
    "francisco-partners": "mega-pe-scope-review",
    "keensight-capital": "mega-pe-scope-review",
    "blue-owl-capital": "mega-pe-scope-review",
    "golub-capital": "mega-pe-scope-review",
}

# ----- lead_ids to DELETE from entity_intake_queue.csv -----
# Strategy: name-pattern + known specific junk. Includes article titles,
# generic page headings, sec.gov, whitehouse.gov pages, podcasts, etc.
DELETE_FROM_QUEUE_NAMES = {
    "ai startup investment roundups 2026",
    "patient capital",  # generic acumen page
    "buy & sell profitable online businesses",
    "local government software",
    "what is a venture studio? the venture studio model explained",
    "search fund resources",
    "vibe coding for solo founders and indie hackers",
    "solo founder ai tools",
    "ai saas acquisition firm from ibm veterans",
    "software valuation multiples",
    "saas valuation multiples 2026",
    "the quiet rise of profitable indie hackers in 2026",
    "indie hacker success stories database",
    "b2b bnpl",
    "startup capital with zero dilution",
    "salesforce",
    "servicenow",
    "hawk infinity software",
    "ibm",
    "motorola solutions",
    "trustmrr",
    "hacker news",
    "roll-up strategy 2026",
    "investments",
    "what is an independent sponsor? 2026 guide to fundless sponsors in m&a",
    "7 actionable bootstrapped saas success stories & playbooks for 2025",
    "founder programs",
    "fellowship",
    "the calm company fund investment thesis",
    "wefunder,  ...",
    "startup financing",
    "explore our saas m&a deal database",
    "saas m&a transaction services",
    "eta",  # just acronym, not the real firm "ETA Equity"
    "learn ai for entrepreneurs",
    "what is employee ownership? a guide for business owners",
    "youth entrepreneurship programming",
    "who we are",
    "acquisition criteria",
    "startup studio vs venture builder",
    "steward ownership",
    "founder fellowship",
    "2025 plumbing industry report",
    "funded!",
    "what is royalty financing?",
    "the fundless sponsor explained",
    "sec.gov",
    "bootstrapped saas the complete founder's playbook",
    "independent sponsor model",
    "the independent sponsor model or fundless sponsor model",
    "vroom ventures",
    "product hunt",
    "startup for the rest of us",
    "satya ghani",
    "private equity rollup strategy explained",
    "private equity roll up strategy explained",
    "allegro",
    "allegrow",
    "the venture studio model",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_csv_rows(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv_rows(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def append_to_log(log_rows: list[dict]) -> None:
    """Write log file with the union of all keys as header."""
    if not log_rows:
        return
    # Union of all keys, stable order: standard log fields first then row fields
    log_fields = ["log_op", "log_reason", "log_timestamp", "log_source_csv"]
    seen = set(log_fields)
    for r in log_rows:
        for k in r.keys():
            if k not in seen:
                log_fields.append(k)
                seen.add(k)
    file_exists = LOG_PATH.exists()
    with LOG_PATH.open("a", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=log_fields, extrasaction="ignore")
        if not file_exists:
            w.writeheader()
        for r in log_rows:
            w.writerow(r)


def main() -> int:
    timestamp = now_iso()
    log_rows: list[dict] = []

    # --- Step 1: process industry_entities.csv ---
    ent_fields, ent_rows = read_csv_rows(ENTITIES_PATH)
    keep_entities: list[dict] = []
    demoted_to_queue: list[dict] = []
    delete_count = 0
    demote_count = 0
    for row in ent_rows:
        eid = row.get("entity_id", "").strip()
        if eid in DELETE_FROM_ENTITIES:
            log_rows.append({
                **row,
                "log_op": "delete_from_entities",
                "log_reason": "obvious non-allocator (article title / tech corp / SaaS product / generic term)",
                "log_timestamp": timestamp,
                "log_source_csv": "industry_entities.csv",
            })
            delete_count += 1
            continue
        if eid in DEMOTE_TO_QUEUE:
            log_rows.append({
                **row,
                "log_op": "demote_to_queue",
                "log_reason": DEMOTE_TO_QUEUE[eid],
                "log_timestamp": timestamp,
                "log_source_csv": "industry_entities.csv",
            })
            demoted_to_queue.append(row)
            demote_count += 1
            continue
        keep_entities.append(row)

    # --- Step 2: process entity_intake_queue.csv ---
    intake_fields, intake_rows = read_csv_rows(INTAKE_PATH)
    keep_intake: list[dict] = []
    queue_delete_count = 0
    for row in intake_rows:
        name_lc = row.get("name", "").strip().lower()
        if name_lc in DELETE_FROM_QUEUE_NAMES:
            log_rows.append({
                **row,
                "log_op": "delete_from_queue",
                "log_reason": "article title / generic term / podcast / personal name (not capital allocator)",
                "log_timestamp": timestamp,
                "log_source_csv": "entity_intake_queue.csv",
            })
            queue_delete_count += 1
            continue
        keep_intake.append(row)

    # --- Step 3: append demoted entities into the queue with mega-pe tag ---
    # Map entity row → intake row (minimum fields to preserve identity)
    today = timestamp[:10]
    for ent in demoted_to_queue:
        name = ent.get("name", "")
        website = ent.get("website", "")
        # Build a deterministic lead_id
        import hashlib
        nslug = ent.get("entity_id", "").replace("-", "")[:20] or "demoted"
        lead_id = f"intake-demoted-{hashlib.sha1((name + website).encode()).hexdigest()[:10]}"
        intake_row = {field: "" for field in intake_fields}
        intake_row.update({
            "lead_id": lead_id,
            "name": name,
            "lead_type": "manual_curation",
            "website": website,
            "source_urls": website,
            "discovered_from": "manual:demote_from_entities_2026-05-28",
            "target_asset_class": "Patient Capital",  # placeholder; Ethan to reclassify
            "target_entity_type": "mega-pe-scope-review",
            "active_status": "active",
            "source_tier": "public_web",
            "priority": "high",
            "evidence_status": "needs_verification",
            "review_status": "needs_review",
            "created_at": today,
            "notes": f"Demoted from industry_entities on 2026-05-28 for Ethan scope review (mega-PE: in or out of post-unicorn atlas?). Original entity_id={ent.get('entity_id','')} primary_asset_class={ent.get('primary_asset_class','')}.",
        })
        keep_intake.append(intake_row)

    # --- Step 4: write outputs ---
    write_csv_rows(ENTITIES_PATH, ent_fields, keep_entities)
    write_csv_rows(INTAKE_PATH, intake_fields, keep_intake)
    append_to_log(log_rows)

    # --- Step 5: report ---
    print(f"=== Atlas Junk Purge -- {timestamp} ===")
    print(f"industry_entities.csv: {len(ent_rows)} -> {len(keep_entities)}")
    print(f"  deleted (junk):     {delete_count}")
    print(f"  demoted (mega-PE):  {demote_count}")
    print(f"entity_intake_queue.csv: {len(intake_rows)} -> {len(keep_intake)}")
    print(f"  deleted (junk):     {queue_delete_count}")
    print(f"  added (demotions):  {demote_count}")
    print(f"Audit log: {LOG_PATH.relative_to(ROOT)} ({len(log_rows)} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
