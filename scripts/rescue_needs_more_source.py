"""
Rescue stalled `needs_more_source` leads by expanding their source_urls to
include common informational sub-pages, then re-running fetch + promote.

Many capital firms have generic homepages but rich /about, /thesis,
/our-approach, or /portfolio pages that DO contain the asset-class keywords
the promotion gate requires.

Strategy:
 1. For each lead with review_status='needs_more_source', generate sub-page
    URL candidates by appending standard paths to the lead's homepage.
 2. Append those URLs to the lead's `source_urls` (semicolon-separated).
 3. Reset review_status to 'queued' so the next promotion pass re-evaluates.
 4. The next `fetch-sources` + `promote-intake` will fetch and try to promote.

Run:
  python scripts/rescue_needs_more_source.py
  python scripts/research_agents.py fetch-sources --limit 300
  python scripts/research_agents.py promote-intake --limit 100
"""
from __future__ import annotations

import csv
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
INTAKE_PATH = ROOT / "data" / "evidence" / "entity_intake_queue.csv"
SOURCE_PATH = ROOT / "data" / "evidence" / "source_registry.csv"

# Paths that tend to contain investment-thesis language
SUB_PATHS = [
    "/about",
    "/about-us",
    "/approach",
    "/our-approach",
    "/thesis",
    "/investment-thesis",
    "/philosophy",
    "/strategy",
    "/our-strategy",
    "/what-we-do",
    "/how-we-invest",
    "/our-companies",
    "/portfolio",
    "/companies",
    "/investments",
    "/team",
    "/why-us",
    "/process",
]


def base_url(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return ""
    return f"{parsed.scheme}://{parsed.netloc}"


def main() -> int:
    with INTAKE_PATH.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fields = reader.fieldnames
        rows = list(reader)
    with SOURCE_PATH.open(encoding="utf-8") as f:
        s_reader = csv.DictReader(f)
        s_fields = s_reader.fieldnames
        s_rows = list(s_reader)
    existing_source_urls = {r["source_url"] for r in s_rows}

    rescued = 0
    new_source_rows: list[dict[str, str]] = []
    for row in rows:
        if row.get("review_status") != "needs_more_source":
            continue
        homepage = row.get("website", "").strip()
        base = base_url(homepage)
        if not base:
            continue
        existing_urls = {u.strip() for u in (row.get("source_urls") or "").split(";") if u.strip()}
        added = []
        for sub in SUB_PATHS:
            candidate = base + sub
            if candidate in existing_urls:
                continue
            added.append(candidate)
            if candidate not in existing_source_urls:
                new_source_rows.append({
                    "source_url": candidate,
                    "source_name": f"{row['name']} {sub} page",
                    "source_type": "sub_page_rescue",
                    "source_quality": "unknown",
                    "license_or_access": "public web",
                    "notes": f"Rescue-fetch candidate for {row['name']} stalled at needs_more_source.",
                    "last_checked": row.get("created_at") or "",
                })
                existing_source_urls.add(candidate)
        if added:
            row["source_urls"] = ";".join(sorted({*existing_urls, *added}))
            row["review_status"] = "queued"  # let the next pass re-evaluate
            row["notes"] = (row.get("notes") or "") + f" | Rescue: appended {len(added)} sub-page URLs and requeued."
            rescued += 1

    with INTAKE_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    if new_source_rows:
        s_rows.extend(new_source_rows)
        with SOURCE_PATH.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=s_fields)
            w.writeheader()
            w.writerows(s_rows)
    print(f"Rescued {rescued} leads; appended {len(new_source_rows)} new sub-page URLs to source_registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
