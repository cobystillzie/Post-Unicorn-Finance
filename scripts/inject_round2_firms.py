"""Phase 4c — Second batch of curated firm injections from WebSearch round 2.

Sources: family-office direct-investment articles, steward-ownership directories,
European software holdco maps, RBF provider lists. All firms have public web
presence and fit non-unicorn capital criteria.
"""
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

# (name, website, target_asset_class, entity_type, notes)
FIRMS = [
    # Family-office direct-investment / patient capital
    ("Carlson Private Capital Partners", "https://www.carlsonprivatecapital.com/", "Patient Capital", "family direct investing firm", "Provides flexible, patient capital to founder-owned profitable industry-leading businesses across North America."),
    ("Walton Family Holdings", "https://www.waltonfamilyholdings.com/", "Patient Capital", "family office direct investment", "Walton-family direct investment vehicle for patient long-hold private capital."),

    # Steward-owned companies (operating companies that exemplify permanent/steward capital model)
    ("Carl Zeiss Foundation", "https://www.carl-zeiss-stiftung.de/", "Patient Capital", "perpetual purpose foundation", "Sole owner of Zeiss optics; steward-ownership archetype operating since 1889."),
    ("Robert Bosch Stiftung", "https://www.bosch-stiftung.de/", "Patient Capital", "perpetual charitable foundation", "Majority owner of Robert Bosch GmbH; classic German Stiftung steward-ownership model."),
    ("Elobau", "https://www.elobau.com/", "Patient Capital", "steward-owned operating company", "German sensor manufacturer transferred to steward-ownership via Purpose Foundation framework."),
    ("Mahle", "https://www.mahle.com/", "Patient Capital", "steward-owned automotive supplier", "Foundation-owned global automotive supplier."),
    ("John Lewis Partnership", "https://www.johnlewispartnership.co.uk/", "Patient Capital", "employee-owned trust", "UK employee-owned retailer; steward-ownership exemplar."),
    ("Novo Nordisk Foundation", "https://novonordiskfonden.dk/", "Patient Capital", "perpetual charitable foundation", "Controlling owner of Novo Nordisk; long-horizon foundation capital."),
    ("Organically Grown Company", "https://www.organicallygrown.com/", "Patient Capital", "purpose trust operating company", "US purpose trust ownership; Pacific NW organic produce distributor with no individual owners."),

    # European software holdcos
    ("MEDIQON Group", "https://www.mediqon.de/", "Portfolio Capital", "German VMS holding company", "Long-hold German vertical-market-software acquirer; €100M deployed across 26+ acquisitions."),
    ("Asseco Group", "https://www.asseco.com/", "Portfolio Capital", "European software federation", "Federation of software companies operating in 60+ countries with ~$4B in revenues."),
    ("Rebel Capital", "https://www.rebelcapital.io/", "Portfolio Capital", "permanent-equity software holdco", "AI-first SaaS HoldCo seeking permanent-equity LP capital; $100M revenue goal by 2030."),
    ("FLEX Capital", "https://www.flex.capital/", "Portfolio Capital", "German software roll-up investor", "Deep-dive analyst and serial software roll-up backer; European focus."),
    ("Lumine Group", "https://www.luminegroup.com/", "Portfolio Capital", "vertical software acquirer", "Constellation Software spinoff acquiring vertical-market communications/media software."),
    ("Perpetual Investors", "https://www.perpetualinvestors.com/", "Patient Capital", "permanent capital vehicle", "Long-hold investment vehicle for permanent-capital deployment."),

    # Additional non-unicorn capital
    ("Saas-Capital", "https://www.saas-capital.com/", "SMV", "SaaS debt growth financing", "Debt-based growth financing for SaaS companies as alternative to VC."),
    ("Upstart Network", "https://www.upstart.com/", "SMV", "alternative AI lender", "AI-driven non-dilutive lending platform."),
    ("Float Finance", "https://www.floatfinance.com/", "SMV", "non-dilutive capital", "RBF / non-dilutive capital for SaaS founders."),

    # Search/ETA + holdco crossover
    ("ClearlyAcquired", "https://www.clearlyacquired.com/", "Search/ETA", "search-fund resource + marketplace", "Search-fund deal marketplace and resource library."),
    ("Aventis Advisors", "https://www.aventis-advisors.com/", "Portfolio Capital", "M&A advisory + analyst", "Software M&A advisory tracking European software PE landscape."),
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
        lead_id = make_id("intake-curated2", n, d)
        if lead_id in existing_lead_ids:
            continue
        intake_rows.append({
            "lead_id": lead_id, "name": name, "lead_type": "manual_curation",
            "website": website, "source_urls": website,
            "discovered_from": "manual:claude_curation_round2_2026-05-28",
            "target_asset_class": tc, "target_entity_type": et,
            "active_status": "active", "source_tier": "high", "priority": "high",
            "evidence_status": "needs_verification", "review_status": "queued",
            "created_at": today,
            "notes": f"Curated round 2 on 2026-05-28 from WebSearch firm-list articles. {notes}",
        })
        existing_names.add(n)
        existing_keys.add((n, d))
        existing_lead_ids.add(lead_id)
        if website not in existing_source_urls:
            s_rows.append({
                "source_url": website, "source_name": f"{name} official site",
                "source_type": "official_site", "source_quality": "high",
                "license_or_access": "public web",
                "notes": f"Curated round 2 by claude session 2026-05-28.",
                "last_checked": today,
            })
            existing_source_urls.add(website)
        new_count += 1
        print(f"  + {name}")

    with INTAKE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=intake_fields); w.writeheader(); w.writerows(intake_rows)
    with SOURCE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=s_fields); w.writeheader(); w.writerows(s_rows)
    print(f"Injected {new_count} round-2 firms.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
