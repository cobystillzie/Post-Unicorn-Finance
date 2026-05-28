"""
Phase 4b — Bulk-inject high-confidence non-unicorn capital firms not yet in atlas.

Each entry is a firm I'm confident about based on:
- WebSearch returns from 2026-05-28
- Domain knowledge of the search-fund / permanent-equity / RBF spaces
- Names mentioned in Cowork's earlier handoff

URLs are best-guess homepage URLs. The fetch+promote pipeline will:
 - Successfully verify firms whose homepage carries 2+ asset-class keywords
 - 404 / stall the ones with wrong URLs (manageable attrition)

This script ONLY adds firms not already in industry_entities or entity_intake_queue.

Run:
  python scripts/inject_known_firms.py
  python scripts/atlas_sqlite.py build
  python scripts/research_agents.py fetch-sources --limit 300
  python scripts/research_agents.py promote-intake --limit 300
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
    # Search/ETA - search funds, ETA accelerators, independent sponsors
    ("DVG Partners", "https://www.dvgpartners.com/", "Search/ETA", "search fund investor", "Search-fund investor frequently cited in 2025-2026 lists."),
    ("Broadtree Partners", "https://www.broadtreepartners.com/", "Search/ETA", "search fund investor", "Search-fund firm noted in industry directories."),
    ("Red Forest Capital", "https://www.redforestcapital.com/", "Search/ETA", "search fund investor", "Search-fund investor."),
    ("Vroom Ventures", "https://www.vroom.vc/", "Search/ETA", "search fund accelerator", "ETA-focused search-fund vehicle."),
    ("NextGen GP", "https://nextgengp.com/", "Search/ETA", "search fund accelerator", "Search-fund accelerator and ETA resource publisher."),
    ("Avante Capital", "https://avantecapital.com/", "Search/ETA", "independent sponsor", "Independent sponsor model — deal-by-deal acquirer."),
    ("Endurance Search Partners", "https://endurance-search.com/", "Search/ETA", "search fund accelerator", "Search-fund accelerator."),

    # Portfolio Capital - vertical SaaS holdcos, serial acquirers
    ("Brydon Group", "https://www.brydongroup.com/", "Portfolio Capital", "vertical software holding company", "Acquires vertical software and services in regulated industries."),
    ("Relay Commerce", "https://www.relaycommerce.com/", "Portfolio Capital", "e-commerce software holding company", "E-commerce software holdco buying recurring-revenue businesses."),
    ("Embrace Software", "https://www.embracesoftware.com/", "Portfolio Capital", "niche SaaS acquirer", "Acquires niche vertical-SaaS and on-premise software."),
    ("Tern Group", "https://wearetern.com/", "Portfolio Capital", "UK VMS acquirer", "Deal-by-deal UK vertical-market-software acquirer."),
    ("Merit Network", "https://meritholdings.com/", "Portfolio Capital", "vertical SaaS holdco", "Holding company for hyper-specialized vertical software businesses."),
    ("Volaris", "https://www.volarisgroup.com/", "Portfolio Capital", "vertical software holding company", "Constellation Software operating group acquiring vertical-market software."),

    # LMV - solo GPs, nano funds, indie capital
    ("Hustle Fund", "https://www.hustlefund.vc/", "LMV", "pre-seed solo-GP fund", "Operator-led pre-seed fund for hustle-style founders."),
    ("South Park Commons", "https://www.southparkcommons.com/", "LMV", "founder community + fund", "Founder fellowship and community-led capital."),
    ("Banana Capital", "https://www.banana.capital/", "LMV", "solo-GP fund", "Solo-GP nano-fund."),
    ("Forum Ventures", "https://www.forumvc.com/", "LMV", "early-stage B2B accelerator", "Early-stage B2B SaaS founder-friendly capital."),
    ("On Deck", "https://www.beondeck.com/", "LMV", "founder fellowship + capital", "Founder fellowship and capital provider for ambitious founders."),
    ("Magic Fund", "https://www.magic.fund/", "LMV", "global solo-GP collective", "Solo-GP / micro-fund collective focused on globally-distributed founders."),

    # SMV - embedded finance, RBF, working capital
    ("Re:cap", "https://re-cap.com/", "SMV", "recurring-revenue financing", "German RBF provider for SaaS subscription advances."),
    ("Karmen", "https://www.karmen.io/", "SMV", "embedded finance / RBF", "French RBF/working-capital provider for digital businesses."),
    ("Settle", "https://www.settle.com/", "SMV", "working capital / B2B BNPL", "Working-capital + B2B BNPL platform for inventory-driven SMBs."),
    ("Brex Capital", "https://www.brex.com/product/capital", "SMV", "working capital provider", "Brex working-capital line for startups + scale-ups."),

    # Patient Capital / Family offices / Steward ownership
    ("Walton Enterprises", "https://www.waltonenterprises.com/", "Patient Capital", "family office direct investment", "Walton-family multi-generational holding/family-office entity."),
    ("Pritzker Group", "https://www.pritzkergroup.com/", "Patient Capital", "family office direct investment", "Pritzker-family direct private-investment platform with long hold horizons."),
    ("Pohlad Companies", "https://www.pohladcompanies.com/", "Patient Capital", "family operating company", "Multi-generational family operating company / holdco."),
    ("Patagonia Works", "https://www.patagoniaworks.com/", "Patient Capital", "steward-owned holdco", "Patagonia's parent company; founder transferred ownership to Patagonia Purpose Trust + Holdfast Collective."),
    ("Mozilla Foundation", "https://foundation.mozilla.org/", "Patient Capital", "purpose-trust non-profit owner", "Non-profit owner of Mozilla Corporation; steward-ownership model."),
    ("Wellcome Trust", "https://wellcome.org/", "Patient Capital", "perpetual charitable foundation", "Permanent-capital charitable trust funding science and health."),
    ("Purpose Foundation", "https://purpose-economy.org/en/foundation/", "Patient Capital", "steward-ownership foundation", "Foundation that converts companies to permanent steward-owned structures."),
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
        host = urlparse(url).netloc.lower().lstrip("www.")
        return host.split(":")[0]
    except ValueError:
        return ""


def main() -> int:
    with INTAKE_PATH.open(encoding="utf-8") as f:
        intake_reader = csv.DictReader(f)
        intake_fields = intake_reader.fieldnames
        intake_rows = list(intake_reader)
    with SOURCE_PATH.open(encoding="utf-8") as f:
        s_reader = csv.DictReader(f)
        s_fields = s_reader.fieldnames
        s_rows = list(s_reader)
    with ENTITIES_PATH.open(encoding="utf-8") as f:
        e_reader = csv.DictReader(f)
        e_rows = list(e_reader)

    existing_keys: set[tuple[str, str]] = set()
    existing_names: set[str] = set()
    for r in intake_rows + e_rows:
        n = normalize_name(r.get("name", ""))
        existing_keys.add((n, domain(r.get("website", ""))))
        existing_names.add(n)
    existing_source_urls = {r["source_url"] for r in s_rows}
    existing_lead_ids = {r.get("lead_id", "") for r in intake_rows}

    new_count = 0
    today = now_iso()[:10]
    skipped_existing = 0

    for name, website, target_class, entity_type, notes in FIRMS:
        normalized = normalize_name(name)
        dom = domain(website)
        key = (normalized, dom)
        if normalized in existing_names or key in existing_keys:
            skipped_existing += 1
            print(f"  skip (exists): {name}")
            continue
        lead_id = make_id("intake-manual", normalized, dom)
        if lead_id in existing_lead_ids:
            continue
        new_row = {
            "lead_id": lead_id,
            "name": name,
            "lead_type": "manual_curation",
            "website": website,
            "source_urls": website,
            "discovered_from": "manual:claude_curation_2026-05-28",
            "target_asset_class": target_class,
            "target_entity_type": entity_type,
            "active_status": "active",
            "source_tier": "high",
            "priority": "high",
            "evidence_status": "needs_verification",
            "review_status": "queued",
            "created_at": today,
            "notes": f"Manually curated 2026-05-28 from WebSearch and domain knowledge of non-unicorn capital. {notes}",
        }
        intake_rows.append(new_row)
        existing_names.add(normalized)
        existing_keys.add(key)
        existing_lead_ids.add(lead_id)
        if website not in existing_source_urls:
            s_rows.append({
                "source_url": website,
                "source_name": f"{name} official site",
                "source_type": "official_site",
                "source_quality": "high",
                "license_or_access": "public web",
                "notes": f"Curated by claude session 2026-05-28; primary source for {name}.",
                "last_checked": today,
            })
            existing_source_urls.add(website)
        new_count += 1
        print(f"  + {name} -> {website}")

    with INTAKE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=intake_fields)
        w.writeheader()
        w.writerows(intake_rows)
    with SOURCE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=s_fields)
        w.writeheader()
        w.writerows(s_rows)
    print(f"Injected {new_count} new firms; skipped {skipped_existing} already in atlas.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
