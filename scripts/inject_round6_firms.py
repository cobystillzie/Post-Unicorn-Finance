"""Phase 4h — Round 6 injection: Asia-Pacific, LatAm, Nordic emerging managers."""
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
    # Asia-Pacific
    ("FEBE Ventures", "https://febeventures.com/", "SMV", "SE Asia B2B SaaS investor", "Southeast Asia B2B SaaS/AI/IoT/blockchain investor."),
    ("Insignia Ventures Partners", "https://insignia.vc/", "SMV", "SE Asia growth equity", "Singapore-based Southeast Asia early to growth stage investor."),
    # Nordic emerging managers
    ("Alliance Venture", "https://alliance.vc/", "SMV", "Nordic global ambition seed", "Nordic founder-friendly seed firm targeting global ambitions."),
    ("VC Lab", "https://govclab.com/", "LMV", "emerging manager accelerator", "Accelerator program for emerging VC fund managers globally."),
    ("Basepoint VC", "https://basepoint.vc/", "SMV", "Nordic-focused investor", "Nordic-focused VC ecosystem operator + investor."),
    ("Inception Fund", "https://www.inceptionfund.com/", "LMV", "Nordic AI micro fund", "EUR21M Nordic+Baltic micro-fund focused on day-zero technical founders."),
    # LatAm
    ("Kaszek Ventures", "https://kaszek.com/", "SMV", "LatAm early-stage investor", "LatAm-focused founder-friendly venture firm."),
    ("Monashees", "https://monashees.com.br/", "SMV", "Brazilian seed/early-stage", "Brazilian early-stage venture firm."),
    # Specialized / niche
    ("Underdog Inc", "https://underdog.inc/", "Portfolio Capital", "creator-economy venture studio", "Creator-economy focused operator + venture studio."),
    ("Atomico Angels", "https://www.atomico.com/angels", "LMV", "European angel collective", "Atomico's angel program for European operators."),
    ("Kima Ventures", "https://www.kimaventures.com/", "LMV", "global seed angel fund", "Xavier Niel's seed fund investing in 100+ startups per year."),
    ("Hoxton Ventures", "https://hoxtonventures.com/", "SMV", "European deep-tech seed", "London-based European deep-tech seed investor."),
]


def now_iso(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def make_id(prefix, *parts):
    return f"{prefix}-{hashlib.sha1('|'.join(parts).encode()).hexdigest()[:12]}"
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
            "lead_id": make_id("intake-curated6", n, d), "name": name, "lead_type": "manual_curation",
            "website": website, "source_urls": website,
            "discovered_from": "manual:claude_curation_round6_2026-05-28",
            "target_asset_class": tc, "target_entity_type": et,
            "active_status": "active", "source_tier": "public_web", "priority": "high",
            "evidence_status": "needs_verification", "review_status": "queued",
            "created_at": today, "notes": f"Curated round 6 on 2026-05-28. {notes}",
        })
        existing_names.add(n); existing_keys.add((n, d))
        if website not in existing_source_urls:
            s_rows.append({
                "source_url": website, "source_name": f"{name} official site",
                "source_type": "official_site", "source_quality": "primary",
                "license_or_access": "public web",
                "notes": "Curated round 6 by claude session 2026-05-28.", "last_checked": today,
            })
            existing_source_urls.add(website)
        new_count += 1; print(f"  + {name}")
    with INTAKE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=intake_fields); w.writeheader(); w.writerows(intake_rows)
    with SOURCE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=s_fields); w.writeheader(); w.writerows(s_rows)
    print(f"Injected {new_count} round-6 firms.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
