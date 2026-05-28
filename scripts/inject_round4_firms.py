"""Phase 4f — Round 4 curated injection from 4 fresh WebSearches."""
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
    # Founder-friendly SaaS acquirers
    ("Curious", "https://www.curious.fund/", "Patient Capital", "permanent equity SaaS acquirer", "Founded by Andrew Dumont; buy-and-hold software acquirer thinking in decades."),
    ("Noosa Labs", "https://www.noosalabs.com/", "Portfolio Capital", "small SaaS acquirer", "Acquires profitable SaaS at $200K-800K ARR; operator-led ownership."),
    ("itrinity", "https://www.itrinity.com/", "Portfolio Capital", "European SaaS acquirer", "Slovak SaaS holding company; acquired UptimeRobot, EmailListVerify, others."),
    ("Wildfront", "https://wildfront.co/", "Portfolio Capital", "bootstrapped SaaS acquirer", "Acquires profitable bootstrapped SaaS with $1k-$10k MRR."),

    # Search funds / SMB acquisition
    ("Shareholder Ventures", "https://smb.fund/", "Search/ETA", "search fund / SBA co-investor", "$250k-$750k checks behind acquisition entrepreneurs buying $3-12M SMBs with SBA loans."),
    ("Aspect Investors", "https://www.aspectinvestors.com/", "Search/ETA", "search fund investor", "Dallas-based PE specializing in search funds; entrepreneur-CEO collaboration."),
    ("ETA Equity", "https://etaequity.com/", "Search/ETA", "ETA private equity firm", "Dallas TX PE for ETA; invested in 70+ search funds over 15 years."),
    ("SMB Investor Network", "https://www.smbinvestornetwork.com/", "Search/ETA", "SMB co-investment platform", "Co-investment platform for search-fund accredited investors with $10K minimums."),

    # Venture studios
    ("Atomic", "https://atomic.vc/", "Portfolio Capital", "consumer venture studio", "San Francisco venture studio focused on consumer; built Hims, OpenStore, others."),
    ("Pioneer Square Labs", "https://www.psl.com/", "Portfolio Capital", "B2B SaaS venture studio", "Seattle B2B SaaS venture studio with structured build cycles."),
    ("Founders Factory", "https://foundersfactory.com/", "Portfolio Capital", "global venture studio", "UK/global venture studio + accelerator; multi-region."),
    ("Hexa", "https://www.hexa.studio/", "Portfolio Capital", "European B2B SaaS studio", "Paris-based venture studio (formerly eFounders); B2B SaaS + AI focus."),
    ("Science Inc", "https://science-inc.com/", "Portfolio Capital", "consumer venture studio", "LA-based consumer-focused venture studio."),
    ("Nobody Studios", "https://nobodystudios.com/", "Portfolio Capital", "high-volume venture studio", "Targeting incubation of 100 novel companies within 5 years."),

    # European bootstrapped / indie
    ("Point Nine", "https://www.pointninecap.com/", "SMV", "European B2B SaaS angel/seed", "Berlin-based B2B SaaS + marketplace investor (Zendesk, ChartMogul, Geckoboard)."),
    ("Frontline Ventures", "https://www.frontline.vc/", "SMV", "European B2B helping US expansion", "Dublin/London focused on European B2B SaaS expanding to US."),
    ("Qubit Capital", "https://qubit.capital/", "SMV", "alternative startup capital advisor", "Advisor + capital provider profiling RBF/PE/family-office options."),

    # SMV growth equity / non-dilutive
    ("Atempo", "https://www.atempo.fund/", "SMV", "European RBF / hybrid", "European later-stage RBF/hybrid bootstrapped SaaS capital."),
    ("Decathlon Capital Partners", "https://www.decathloncapital.com/", "SMV", "revenue-based financing", "US-based RBF for steady-revenue businesses; senior debt structure."),
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
        lead_id = make_id("intake-curated4", n, d)
        if lead_id in existing_lead_ids:
            continue
        intake_rows.append({
            "lead_id": lead_id, "name": name, "lead_type": "manual_curation",
            "website": website, "source_urls": website,
            "discovered_from": "manual:claude_curation_round4_2026-05-28",
            "target_asset_class": tc, "target_entity_type": et,
            "active_status": "active", "source_tier": "public_web", "priority": "high",
            "evidence_status": "needs_verification", "review_status": "queued",
            "created_at": today,
            "notes": f"Curated round 4 on 2026-05-28. {notes}",
        })
        existing_names.add(n)
        existing_keys.add((n, d))
        existing_lead_ids.add(lead_id)
        if website not in existing_source_urls:
            s_rows.append({
                "source_url": website, "source_name": f"{name} official site",
                "source_type": "official_site", "source_quality": "primary",
                "license_or_access": "public web",
                "notes": f"Curated round 4 by claude session 2026-05-28.",
                "last_checked": today,
            })
            existing_source_urls.add(website)
        new_count += 1
        print(f"  + {name}")

    with INTAKE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=intake_fields); w.writeheader(); w.writerows(intake_rows)
    with SOURCE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=s_fields); w.writeheader(); w.writerows(s_rows)
    print(f"Injected {new_count} round-4 firms.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
