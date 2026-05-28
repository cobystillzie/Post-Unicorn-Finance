"""Phase 4d — Round 3 curated injection from 8 fresh WebSearches."""
from __future__ import annotations

import csv
import hashlib
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "data" / "evidence"
INTAKE_PATH = EVIDENCE / "entity_intake_queue.csv"
SOURCE_PATH = EVIDENCE / "source_registry.csv"
ENTITIES_PATH = EVIDENCE / "industry_entities.csv"

FIRMS = [
    # Micro PE (Patient Capital / Portfolio Capital)
    ("Chenmark", "https://chenmark.com/", "Patient Capital", "micro PE holding company", "Portland ME micro-PE acquiring small businesses with $1M-3M cash flow."),
    ("Atlasview Equity", "https://www.atlasviewequity.com/", "Patient Capital", "micro PE acquirer", "$1M-$5M annual cash flow target; B2B sticky customer base."),
    ("OneOutdoor Holdings", "https://www.oneoutdoor.com/", "Portfolio Capital", "outdoor recreation holdco", "Acquires outdoor recreation businesses with $1M+ EBITDA."),
    ("Thrasio", "https://www.thrasio.com/", "Portfolio Capital", "Amazon FBA / e-commerce roll-up", "Acquires Amazon FBA brands as e-commerce roll-up platform."),
    ("Evermore", "https://www.evermoreequity.com/", "Patient Capital", "micro PE / EBITDA acquirer", "Acquires $4M-$50M revenue businesses with 10+ years operating history."),

    # Impact Capital (Sovereign / Patient)
    ("Calvert Impact Capital", "https://www.calvertimpactcapital.org/", "Sovereign Capital", "impact bond fund", "Patient capital through loans, equity, guarantees for climate + inequality."),
    ("MacArthur Foundation", "https://www.macfound.org/", "Patient Capital", "impact-investing foundation", "Flexible patient risk-tolerant impact investments in funds + projects."),
    ("Better Ventures", "https://www.better.vc/", "Sovereign Capital", "mission-driven impact fund", "Catalyzes mission-driven entrepreneurship aligned to UN SDGs."),
    ("Aligned Climate Capital", "https://www.alignedclimatecapital.com/", "Sovereign Capital", "climate impact investor", "Strategic impact-driven climate investments."),
    ("Lowercarbon Capital", "https://www.lowercarbon.com/", "Sovereign Capital", "climate technology fund", "Backs companies meaningfully reducing CO2 / capturing carbon."),
    ("Blue Earth Capital", "https://www.blueearthcap.com/", "Sovereign Capital", "global impact fund", "Impact secondaries + private markets across climate, financial inclusion, healthcare."),

    # B Corp / Mission-Lock investors (Patient Capital / Steward)
    ("TIFF Investment Management", "https://www.tiff.org/", "Patient Capital", "endowment impact manager", "B Corp certified endowment-focused investment manager."),
    ("Funds For Good", "https://www.fundsforgood.eu/", "Patient Capital", "Belgian impact fund", "Belgian B Corp impact-investing platform."),
    ("Mission Driven Finance", "https://www.missiondrivenfinance.com/", "Patient Capital", "community impact lender", "B Corp impact investing firm financing under-resourced entrepreneurs."),
    ("The Builders Fund", "https://www.thebuildersfund.com/", "Patient Capital", "mission-aligned growth equity", "B Corp growth equity targeting mission-aligned consumer + business services."),

    # Private credit / Direct lending (SMV / Instrument)
    ("Golub Capital", "https://www.golubcapital.com/", "SMV", "middle-market direct lender", "Major US middle-market direct lender; non-dilutive financing for sponsor-backed deals."),
    ("Blue Owl Capital", "https://www.blueowl.com/", "Portfolio Capital", "alternative asset manager", "Direct lending + GP stakes + real estate; permanent capital structures."),

    # Sovereign / Public capital
    ("Sovereign Tech Fund", "https://www.sovereign.tech/", "Sovereign Capital", "German public open-source fund", "German Federal investment in open-source critical digital infrastructure."),
    ("HUMAIN", "https://humain.ai/", "Sovereign Capital", "Saudi AI sovereign", "Saudi PIF-owned AI infrastructure company with $100B+ planned investment."),

    # Faith / values investors (Patient Capital / Steward)
    ("CapShift", "https://capshift.com/", "Patient Capital", "values-driven investment platform", "Donor-advised + foundation impact investing platform."),
    ("The GIIN", "https://thegiin.org/", "Sovereign Capital", "Global Impact Investing Network", "Network organization for global impact investors + faith-based investing repository."),
    ("Faith Driven Investor", "https://faithdriveninvestor.org/", "Patient Capital", "faith-based investor community", "Community + repository for Christian-values investing."),
    ("Amana Mutual Funds", "https://www.amanafunds.com/", "Patient Capital", "Islamic mutual fund manager", "Shariah-compliant mutual fund family; values-based exclusions."),

    # Additional notable mentions
    ("Peter Lohmann", "https://www.peterlohmann.com/", "Patient Capital", "mini-Berkshires commentator + operator", "Operator-commentator on the mini-Berkshire / micro-PE model."),
    ("Permanent Capital (peer)", "https://www.perpetual-capital.com/", "Patient Capital", "permanent capital vehicle", "Long-hold investment vehicle (verify URL on first fetch)."),
]


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def make_id(prefix: str, *parts: str) -> str:
    h = hashlib.sha1("|".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{h}"


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (name or "").lower())


def domain(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().lstrip("www.").split(":")[0]
    except ValueError:
        return ""


def main() -> int:
    with INTAKE_PATH.open(encoding="utf-8") as f:
        ir = csv.DictReader(f)
        intake_fields, intake_rows = ir.fieldnames, list(ir)
    with SOURCE_PATH.open(encoding="utf-8") as f:
        sr = csv.DictReader(f)
        s_fields, s_rows = sr.fieldnames, list(sr)
    with ENTITIES_PATH.open(encoding="utf-8") as f:
        e_rows = list(csv.DictReader(f))

    existing_keys = {(normalize_name(r.get("name", "")), domain(r.get("website", ""))) for r in intake_rows + e_rows}
    existing_names = {normalize_name(r.get("name", "")) for r in intake_rows + e_rows}
    existing_source_urls = {r["source_url"] for r in s_rows}
    existing_lead_ids = {r.get("lead_id", "") for r in intake_rows}

    new_count = 0
    today = now_iso()[:10]
    for name, website, tc, et, notes in FIRMS:
        n = normalize_name(name)
        d = domain(website)
        if n in existing_names or (n, d) in existing_keys:
            print(f"  skip: {name}")
            continue
        lead_id = make_id("intake-curated3", n, d)
        if lead_id in existing_lead_ids:
            continue
        intake_rows.append({
            "lead_id": lead_id, "name": name, "lead_type": "manual_curation",
            "website": website, "source_urls": website,
            "discovered_from": "manual:claude_curation_round3_2026-05-28",
            "target_asset_class": tc, "target_entity_type": et,
            "active_status": "active", "source_tier": "public_web", "priority": "high",
            "evidence_status": "needs_verification", "review_status": "queued",
            "created_at": today,
            "notes": f"Curated round 3 on 2026-05-28 from 8 fresh WebSearches. {notes}",
        })
        existing_names.add(n)
        existing_keys.add((n, d))
        existing_lead_ids.add(lead_id)
        if website not in existing_source_urls:
            s_rows.append({
                "source_url": website, "source_name": f"{name} official site",
                "source_type": "official_site", "source_quality": "primary",
                "license_or_access": "public web",
                "notes": f"Curated round 3 by claude session 2026-05-28.",
                "last_checked": today,
            })
            existing_source_urls.add(website)
        new_count += 1
        print(f"  + {name}")

    with INTAKE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=intake_fields); w.writeheader(); w.writerows(intake_rows)
    with SOURCE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=s_fields); w.writeheader(); w.writerows(s_rows)
    print(f"Injected {new_count} round-3 firms.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
