"""Phase 4g — Round 5 injection: vertical SaaS holdcos, micro acquirers, fellowships."""
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
    # Vertical SaaS holdcos
    ("Dura Software", "https://durasoftware.com/", "Portfolio Capital", "vertical SaaS holdco", "Constellation-style serial acquirer of vertical software."),
    # Micro / SaaS acquisition funds
    ("Southport Ventures", "https://www.southportventures.com/", "Portfolio Capital", "B2B SaaS acquisition fund", "Acquires profitable B2B SaaS; founded by Nicholas Evans + Trevor Ewen 2021."),
    # Pre-seed / founder fellowships (LMV)
    ("Graham & Walker", "https://grahamwalker.com/", "LMV", "founder community + accelerator", "Founder community + accelerator with grants and resources."),
    ("Freed Fellowship", "https://www.freedfellowship.com/", "LMV", "monthly micro-grant fellowship", "Monthly $500 grants for US business owners; no equity."),
    ("Halcyon Incubator", "https://halcyonincubator.org/", "Sovereign Capital", "social entrepreneur fellowship", "Global Climate Fellowship for climate founders; residencies DC + LA."),
    ("Neo", "https://neo.com/", "LMV", "selective founder residency", "Residency replacing Neo Accelerator; $750K SAFE + $450K compute per cohort."),
    ("MassChallenge", "https://masschallenge.org/", "LMV", "equity-free accelerator", "Global equity-free accelerator network."),
    ("CodeLaunch", "https://codelaunch.com/", "LMV", "regional pre-seed accelerator", "Regional pre-seed accelerator with mentorship + capital."),
    ("Theanna", "https://theanna.io/", "LMV", "equity-free accelerator platform", "Equity-free accelerator alternative platform."),
    ("Michigan Founders Fund", "https://michiganfoundersfund.org/", "LMV", "regional pre-accelerator", "Michigan free 7-week no-equity accelerator with operating grants."),
    ("HF0", "https://hf0.com/", "LMV", "founder residency + capital", "SF founder residency offering up to $1M SAFE for 5% equity."),
    # Additional non-unicorn capital
    ("Pioneer.app", "https://pioneer.app/", "LMV", "global founder tournament", "Global tournament + community-led founder funding."),
    ("Sky9 Capital", "https://www.sky9capital.com/", "LMV", "China-focused pre-seed", "China pre-seed investor with founder-friendly terms."),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def make_id(prefix, *parts):
    h = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{h}"

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
    new_count = 0
    today = now_iso()[:10]
    for name, website, tc, et, notes in FIRMS:
        n, d = norm(name), dom(website)
        if n in existing_names or (n, d) in existing_keys:
            print(f"  skip: {name}"); continue
        lead_id = make_id("intake-curated5", n, d)
        intake_rows.append({
            "lead_id": lead_id, "name": name, "lead_type": "manual_curation",
            "website": website, "source_urls": website,
            "discovered_from": "manual:claude_curation_round5_2026-05-28",
            "target_asset_class": tc, "target_entity_type": et,
            "active_status": "active", "source_tier": "public_web", "priority": "high",
            "evidence_status": "needs_verification", "review_status": "queued",
            "created_at": today,
            "notes": f"Curated round 5 on 2026-05-28. {notes}",
        })
        existing_names.add(n); existing_keys.add((n, d))
        if website not in existing_source_urls:
            s_rows.append({
                "source_url": website, "source_name": f"{name} official site",
                "source_type": "official_site", "source_quality": "primary",
                "license_or_access": "public web",
                "notes": "Curated round 5 by claude session 2026-05-28.", "last_checked": today,
            })
            existing_source_urls.add(website)
        new_count += 1
        print(f"  + {name}")
    with INTAKE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=intake_fields); w.writeheader(); w.writerows(intake_rows)
    with SOURCE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=s_fields); w.writeheader(); w.writerows(s_rows)
    print(f"Injected {new_count} round-5 firms.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
