"""Phase 4i — Round 7 injection: permanent capital holdcos + healthcare specialty roll-ups."""
from __future__ import annotations
import csv, hashlib, re, sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
EV = ROOT / "data" / "evidence"
INTAKE_PATH = EV / "entity_intake_queue.csv"
SOURCE_PATH = EV / "source_registry.csv"
ENTITIES_PATH = EV / "industry_entities.csv"

FIRMS = [
    # Permanent capital holdcos
    ("AH Equity Investments", "https://www.ah-equity.com/", "Patient Capital", "permanent capital holdco", "Panama-based permanent capital vehicle; intends to never sell."),
    ("Perpetuo Capital", "https://perpetuocapital.com/", "Patient Capital", "permanent capital balance-sheet acquirer", "Balance-sheet permanent capital; $2-10M EBITDA majority change-of-control LBO with continuing management."),
    ("Snell Ventures", "https://www.snellventures.com/", "Patient Capital", "faith-focused family office", "Nashville-based family office acquiring manufacturing/industrial for next-generation preservation."),
    ("Hummock Capital", "https://www.hummockcapital.com/", "Patient Capital", "family-owned operating holding company", "Family-owned holdco actively managing NA manufacturing + tech as owner-operators."),
    ("The Courtney Group", "https://www.courtneygroup.com/", "Patient Capital", "flexible long-hold operator", "$1M-$200M equity flexibility; can own businesses for 20+ years."),
    # Healthcare specialty roll-ups (Portfolio Capital)
    ("Pacific Dental Services", "https://www.pacificdentalservices.com/", "Portfolio Capital", "national dental services platform", "Major US dental services organization; serial acquirer of practices."),
    ("Specialty Dental Brands", "https://www.specialtydentalbrands.com/", "Portfolio Capital", "specialty dental roll-up", "Largest US specialty-only dental DSO consolidator; premium 10x-13x EBITDA multiples."),
    ("Allied OMS", "https://www.alliedoms.com/", "Portfolio Capital", "oral/maxillofacial roll-up", "30+ offices in 12 states; specialty oral/maxillofacial surgery roll-up."),
    ("Beacon Oral Specialists", "https://www.beaconoralspecialists.com/", "Portfolio Capital", "oral surgery roll-up", "106 locations in 12 states; oral surgery specialty platform."),
    ("Epic4 Specialty Partners", "https://www.epic4partners.com/", "Portfolio Capital", "specialty dental partnership", "61 practices; specialty dental partnership platform."),
    ("Heartland Dental", "https://www.heartland.com/", "Portfolio Capital", "national dental support organization", "Largest US dental services organization; ~2,500+ offices; KKR + OTPP-backed serial acquirer."),
    ("MB2 Dental", "https://www.mb2dental.com/", "Portfolio Capital", "doctor-owned dental partnership", "Doctor-owned dental partnership model; mid-market specialty roll-up."),
    ("Mortenson Dental Partners", "https://www.mortensondental.com/", "Portfolio Capital", "dental support organization", "Audax + Genstar-backed dental services organization."),
]


def now_iso(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def make_id(prefix, *parts): return f"{prefix}-{hashlib.sha1('|'.join(parts).encode()).hexdigest()[:12]}"
def norm(name): return re.sub(r"[^a-z0-9]+", "", (name or "").lower())
def dom(url):
    try: return urlparse(url).netloc.lower().lstrip("www.").split(":")[0]
    except ValueError: return ""


def main() -> int:
    with INTAKE_PATH.open(encoding="utf-8") as f:
        ir = csv.DictReader(f); intake_fields, intake_rows = ir.fieldnames, list(ir)
    with SOURCE_PATH.open(encoding="utf-8") as f:
        sr = csv.DictReader(f); s_fields, s_rows = sr.fieldnames, list(sr)
    with ENTITIES_PATH.open(encoding="utf-8") as f:
        e_rows = list(csv.DictReader(f))
    existing_keys = {(norm(r.get("name","")), dom(r.get("website",""))) for r in intake_rows + e_rows}
    existing_names = {norm(r.get("name","")) for r in intake_rows + e_rows}
    existing_source_urls = {r["source_url"] for r in s_rows}
    new_count, today = 0, now_iso()[:10]
    for name, website, tc, et, notes in FIRMS:
        n, d = norm(name), dom(website)
        if n in existing_names or (n, d) in existing_keys:
            print(f"  skip: {name}"); continue
        intake_rows.append({
            "lead_id": make_id("intake-curated7", n, d), "name": name, "lead_type": "manual_curation",
            "website": website, "source_urls": website,
            "discovered_from": "manual:claude_curation_round7_2026-05-28",
            "target_asset_class": tc, "target_entity_type": et,
            "active_status": "active", "source_tier": "public_web", "priority": "high",
            "evidence_status": "needs_verification", "review_status": "queued",
            "created_at": today, "notes": f"Curated round 7 on 2026-05-28. {notes}",
        })
        existing_names.add(n); existing_keys.add((n, d))
        if website not in existing_source_urls:
            s_rows.append({
                "source_url": website, "source_name": f"{name} official site",
                "source_type": "official_site", "source_quality": "primary",
                "license_or_access": "public web",
                "notes": "Curated round 7 by claude session 2026-05-28.", "last_checked": today,
            })
            existing_source_urls.add(website)
        new_count += 1; print(f"  + {name}")
    with INTAKE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=intake_fields); w.writeheader(); w.writerows(intake_rows)
    with SOURCE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=s_fields); w.writeheader(); w.writerows(s_rows)
    print(f"Injected {new_count} round-7 firms.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
