"""
Queue Audit 2026-06-01 -- pre-screen 789 non-promoted leads before next promotion run.

Findings:
  28 confirmed purge candidates (11 UVC + 17 ECOSYSTEM non-allocators)
  761 clean leads -> queued (ready for inject_and_promote)
  1 double-promoted lead already in atlas

Purge criteria (name/entity_type only -- no page content available):
  UVC hard list: confirmed unicorn-return-seeking VC firms
  ECOSYSTEM: equity-free grants/fellowships, angel networks/syndicates, communities

Adversarial review notes:
  Accel-KKR: mid-market tech PE (NOT UVC) -- kept as Portfolio Capital candidate
  FJ Labs: marketplace-focused seed, borderline -- kept for gate
  J-Ventures: "capitalist kibbutz" -- kept for gate
  OneOutdoor Holdings: outdoor recreation holdco -- kept as Portfolio Capital candidate
  Neo: selective founder residency (no capital deployed) -> PURGE ECOSYSTEM
  Atomico Angels: European angel collective (not a fund) -> PURGE ECOSYSTEM

Run from project root:
    python scripts/queue_audit_2026-06-01.py
"""

import csv, re
from pathlib import Path
from urllib.parse import urlparse

EVIDENCE  = Path("data/evidence")
QUEUE_CSV = EVIDENCE / "entity_intake_queue.csv"
LOG       = EVIDENCE / "manual_changes_2026-06-01.log"
AUDIT_LOG = EVIDENCE / "queue_audit_2026-06-01.csv"
TODAY     = "2026-06-01"


def norm(n):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", (n or "").lower())).strip()


def domain_of(url):
    try:
        d = urlparse((url or "").strip().lower()).netloc.replace("www.", "")
        return d.split(":")[0].strip("/")
    except Exception:
        return ""


def read_csv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path, rows, fieldnames=None):
    if not rows:
        return
    fns = fieldnames or list(rows[0].keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fns, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def append_log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")


# Confirmed UVC (unicorn-return-seeking VC firms)
PURGE_UVC = {norm(n) for n in [
    "Thoma Bravo", "GTCR", "Battery Ventures", "8VC", "Hack VC",
    "Founders Fund Seed", "Founders Fund", "Compound VC",
    "Eniac Ventures", "Gradient Ventures", "1kx",
]}

# Confirmed non-allocators (fellowships, grants, angel syndicates, communities)
PURGE_ECOSYSTEM = {norm(n) for n in [
    # Fellowship / grants / equity-free
    "On Deck", "Graham & Walker", "Founder Fellowship", "Da Vinci Fellowship",
    "Echoing Green", "Black Ambition", "Tory Burch Foundation", "Arch Grants",
    "AI Risk Mitigation Fund", "Neo",
    # Angel networks / syndicates
    "AngelHQ", "TRICAPITAL Angels", "Halo Business Angel Network (HBAN)",
    "Equity Gap", "Angel Ventures", "Highland Venture Capital", "Atomico Angels",
]}


def run_audit():
    atlas_rows = read_csv(EVIDENCE / "industry_entities.csv")
    atlas_names = {norm(r.get("name", "") or r.get("legal_name", "")) for r in atlas_rows}
    atlas_domains = {domain_of(r.get("website", "")) for r in atlas_rows if r.get("website", "")}

    rows = read_csv(QUEUE_CSV)
    fieldnames = list(rows[0].keys())

    audit_log = []
    updated_rows = []
    counts = {
        "unchanged_promoted": 0,
        "promoted_duplicate": 0,
        "rejected_uvc": 0,
        "rejected_ecosystem": 0,
        "queued": 0,
    }

    for row in rows:
        status = row.get("review_status", "")
        name   = row.get("name", "")
        nn     = norm(name)
        d      = domain_of(row.get("website", ""))

        if status == "promoted":
            counts["unchanged_promoted"] += 1
            updated_rows.append(row)
            continue

        if (nn in atlas_names) or (d and d in atlas_domains):
            row = dict(row)
            row["review_status"] = "promoted_duplicate"
            row["notes"] = (row.get("notes", "") + " | [audit-2026-06-01] already in atlas").strip()
            counts["promoted_duplicate"] += 1
            audit_log.append({"lead_id": row.get("lead_id", ""), "name": name,
                               "action": "promoted_duplicate", "reason": "already in atlas"})
            updated_rows.append(row)
            continue

        if nn in PURGE_UVC:
            row = dict(row)
            row["review_status"] = "rejected"
            row["notes"] = (row.get("notes", "") + " | [audit-2026-06-01] PURGE_UVC").strip()
            counts["rejected_uvc"] += 1
            audit_log.append({"lead_id": row.get("lead_id", ""), "name": name,
                               "action": "rejected", "reason": "UVC -- unicorn-return-seeking VC"})
            updated_rows.append(row)
            continue

        if nn in PURGE_ECOSYSTEM:
            row = dict(row)
            row["review_status"] = "rejected"
            row["notes"] = (row.get("notes", "") + " | [audit-2026-06-01] PURGE_ECOSYSTEM").strip()
            counts["rejected_ecosystem"] += 1
            audit_log.append({"lead_id": row.get("lead_id", ""), "name": name,
                               "action": "rejected", "reason": "ECOSYSTEM -- non-allocator"})
            updated_rows.append(row)
            continue

        row = dict(row)
        row["review_status"] = "queued"
        row["notes"] = (row.get("notes", "") +
                        " | [audit-2026-06-01] pre-screen cleared, ready for promote").strip()
        counts["queued"] += 1
        updated_rows.append(row)

    write_csv(QUEUE_CSV, updated_rows, fieldnames)

    if audit_log:
        write_csv(AUDIT_LOG, audit_log, ["lead_id", "name", "action", "reason"])

    append_log(f"\n[{TODAY}] QUEUE AUDIT RUN")
    for k, v in counts.items():
        append_log(f"  {k}: {v}")

    return counts, audit_log


if __name__ == "__main__":
    counts, audit_log = run_audit()

    total = sum(counts.values())
    print("=== QUEUE AUDIT 2026-06-01 COMPLETE ===\n")
    print(f"  Total queue rows:      {total}")
    print(f"  Unchanged (promoted):  {counts['unchanged_promoted']}")
    print(f"  Promoted duplicates:   {counts['promoted_duplicate']}")
    print(f"  Rejected (UVC):        {counts['rejected_uvc']}")
    print(f"  Rejected (ecosystem):  {counts['rejected_ecosystem']}")
    print(f"  Queued (clean):        {counts['queued']}")
    print()
    rejected = [e for e in audit_log if e["action"] == "rejected"]
    print(f"Rejected ({len(rejected)}):")
    for e in rejected:
        print(f"  {e['name']:<44} {e['reason']}")
    print()
    print(f"Audit log:   {AUDIT_LOG}")
    print()
    print("Priority order for next inject_and_promote run:")
    print("  1. Portfolio Capital  (need +93,  have 157 queued)")
    print("  2. LMV               (need +39,  have ~250 queued after purge)")
    print("  3. SMV               (need  +8,  have 115 queued)")
    print("  4. Sovereign Capital (at target, 68 queued for replacement)")
    print("  5. Patient Capital   (OVER target -- do NOT add more)")
    print("\nDone.")
