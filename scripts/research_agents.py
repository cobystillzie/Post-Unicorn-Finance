"""Local research-agent loop for the Post-Unicorn Finance atlas."""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from atlas_sqlite import DEFAULT_DB, exec_script, export_rankings, import_csvs, insert_dict, now_iso, open_db, slug, validate_database
from atlas_scoring import default_claim_confidence


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "data" / "evidence"
EXPORTS = ROOT / "data" / "exports"

KEYWORD_GROUPS = {
    "instrument_language": [
        "revenue-based",
        "revenue based",
        "revenue share",
        "shared earnings",
        "royalty",
        "capped return",
        "non-dilutive",
        "venture debt",
        "working capital",
        "milestone",
    ],
    "smv_language": [
        "bootstrapped",
        "capital efficient",
        "b2b saas",
        "profitable",
        "founder-led",
        "acquisition",
        "m&a",
        "vertical software",
        "software companies",
    ],
    "patient_capital_language": [
        "patient capital",
        "permanent capital",
        "long-term",
        "long duration",
        "no forced exit",
        "dividend",
        "hold forever",
    ],
    "search_eta_language": [
        "search fund",
        "entrepreneurship through acquisition",
        "acquire a business",
        "business acquisition",
        "operator",
    ],
    "sovereign_language": [
        "sovereign",
        "national",
        "public investment",
        "strategic investment",
        "government",
        "industrial",
    ],
    "portfolio_capital_language": [
        "holding company",
        "venture studio",
        "startup studio",
        "acquire and operate",
        "portfolio",
        "shared infrastructure",
    ],
    "lmv_language": [
        "indie",
        "solo founder",
        "micro-saas",
        "micro saas",
        "tiny team",
        "ai-native",
    ],
}

CLASS_KEYWORDS = {
    "UVC": ["venture capital", "vc firm", "pre-seed", "seed fund", "early-stage", "startups"],
    "SMV": [
        "bootstrapped",
        "capital efficient",
        "b2b saas",
        "founder-led",
        "vertical software",
        "recurring revenue",
        "revenue-based",
        "non-dilutive",
        "growth debt",
    ],
    "Patient Capital": ["patient capital", "permanent capital", "long-term", "no forced exit"],
    "Search/ETA": ["search fund", "entrepreneurship through acquisition", "business acquisition"],
    "Sovereign Capital": ["sovereign", "government", "public investment", "national"],
    "Portfolio Capital": ["holding company", "venture studio", "startup studio", "acquire and operate"],
    "LMV": ["indie", "solo founder", "micro-saas", "tiny team", "ai-native"],
}

COMMON_NAME_TOKENS = {
    "capital",
    "company",
    "fund",
    "group",
    "holdings",
    "labs",
    "partners",
    "software",
    "ventures",
}


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.title_parts: list[str] = []
        self._in_title = False
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._skip_depth:
            return
        text = html.unescape(data).strip()
        if not text:
            return
        if self._in_title:
            self.title_parts.append(text)
        self.parts.append(text)

    @property
    def text(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.parts)).strip()

    @property
    def title(self) -> str:
        return re.sub(r"\s+", " ", " ".join(self.title_parts)).strip()


def make_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()[:12]
    return f"{prefix}-{digest}"


def split_tags(value: str) -> list[str]:
    return [part.strip() for part in value.split(";") if part.strip()]


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_fieldnames(path: Path, rows: list[dict[str, str]]) -> list[str]:
    if path.exists():
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames:
                return list(reader.fieldnames)
    if rows:
        return list(rows[0].keys())
    return []


def write_csv_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str] | None = None) -> None:
    fieldnames = fieldnames or csv_fieldnames(path, rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def evidence_path(name: str) -> Path:
    return EVIDENCE / name


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def significant_tokens(value: str) -> list[str]:
    tokens = [token.lower() for token in re.findall(r"[a-zA-Z0-9]+", value)]
    filtered = [token for token in tokens if len(token) >= 3 and token not in COMMON_NAME_TOKENS]
    return filtered or [token for token in tokens if len(token) >= 3]


def source_quality_for_url(source_url: str) -> str:
    for row in read_csv_rows(evidence_path("source_registry.csv")):
        if row.get("source_url", "").strip() == source_url:
            return row.get("source_quality", "unknown") or "unknown"
    return "unknown"


def record_run(
    conn: sqlite3.Connection,
    agent_name: str,
    stage: str,
    status: str,
    started_at: str,
    input_count: int,
    output_count: int,
    notes: str,
) -> str:
    run_id = make_id("run", agent_name, stage, started_at, str(output_count))
    insert_dict(
        conn,
        "agent_runs",
        {
            "run_id": run_id,
            "agent_name": agent_name,
            "stage": stage,
            "status": status,
            "started_at": started_at,
            "completed_at": now_iso(),
            "input_count": input_count,
            "output_count": output_count,
            "notes": notes,
        },
    )
    return run_id


def ensure_db(db_path: Path) -> None:
    if not db_path.exists():
        import_csvs(db_path)
        return
    with open_db(db_path) as conn:
        exec_script(conn)
        conn.commit()


def discovery_agent(db_path: Path) -> int:
    ensure_db(db_path)
    started = now_iso()
    with open_db(db_path) as conn:
        targets = conn.execute("SELECT * FROM scrape_targets").fetchall()
        created = 0
        for target in targets:
            seeds = [part.strip() for part in target["seed_entities_or_sources"].split(";") if part.strip()]
            for seed in seeds:
                candidate_id = make_id("candidate", target["target_id"], seed)
                insert_dict(
                    conn,
                    "discovery_candidates",
                    {
                        "candidate_id": candidate_id,
                        "run_id": "pending",
                        "lane": target["lane"],
                        "target_asset_class": target["target_asset_class"],
                        "name": seed,
                        "website": "",
                        "source_url": "",
                        "source_snippet": target["query"],
                        "source_type": target["source_family"],
                        "evidence_status": "candidate_evidence",
                        "confidence_score": 40,
                        "created_at": now_iso(),
                        "notes": "Seed candidate from scrape_targets.csv; requires source discovery before atlas insertion.",
                    },
                )
                created += 1
            conn.execute(
                """
                UPDATE query_performance
                SET results_found = ?, candidates_added = ?, last_run_at = ?
                WHERE target_id = ?
                """,
                (len(seeds), len(seeds), now_iso(), target["target_id"]),
            )
        intake_rows = conn.execute(
            "SELECT * FROM entity_intake_queue WHERE review_status IN ('queued', 'needs_more_source')"
        ).fetchall()
        for lead in intake_rows:
            candidate_id = make_id("candidate", "entity-intake", lead["lead_id"])
            insert_dict(
                conn,
                "discovery_candidates",
                {
                    "candidate_id": candidate_id,
                    "run_id": "pending",
                    "lane": "Entity Intake",
                    "target_asset_class": lead["target_asset_class"],
                    "name": lead["name"],
                    "website": lead["website"],
                    "source_url": lead["website"],
                    "source_snippet": lead["notes"],
                    "source_type": lead["lead_type"],
                    "evidence_status": lead["evidence_status"],
                    "confidence_score": 25,
                    "created_at": now_iso(),
                    "notes": "User-discovered intake lead. Keep out of industry_entities.csv until source text supports a specific atlas claim.",
                },
            )
            created += 1
        run_id = record_run(
            conn,
            "discovery_agent",
            "discovery",
            "ok",
            started,
            len(targets) + len(intake_rows),
            created,
            "Generated seed candidates from scrape targets and queued entity-intake leads.",
        )
        conn.execute("UPDATE discovery_candidates SET run_id = ? WHERE run_id = 'pending'", (run_id,))
        conn.commit()
    print(f"Discovery agent created/updated {created} candidate leads")
    return 0


def fetch_url(source_url: str, timeout: int = 20) -> dict[str, object]:
    request = Request(
        source_url,
        headers={
            "User-Agent": "post-unicorn-finance-research-bot/0.1 (+local evidence verification)",
            "Accept": "text/html,application/xhtml+xml,text/plain;q=0.9,*/*;q=0.5",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(1_500_000)
            content_type = response.headers.get("content-type", "")
            charset = response.headers.get_content_charset() or "utf-8"
            decoded = body.decode(charset, errors="replace")
            extractor = TextExtractor()
            if "html" in content_type.lower() or "<html" in decoded[:500].lower():
                extractor.feed(decoded)
                text = extractor.text
                title = extractor.title
            else:
                text = re.sub(r"\s+", " ", decoded).strip()
                title = ""
            status_code = getattr(response, "status", 200)
            return {
                "status_code": int(status_code),
                "fetch_status": "ok",
                "content_type": content_type,
                "title": title[:500],
                "raw_text": text[:250_000],
                "error": "",
            }
    except HTTPError as exc:
        return {
            "status_code": int(exc.code),
            "fetch_status": "http_error",
            "content_type": "",
            "title": "",
            "raw_text": "",
            "error": str(exc),
        }
    except (URLError, TimeoutError, OSError) as exc:
        return {
            "status_code": 0,
            "fetch_status": "error",
            "content_type": "",
            "title": "",
            "raw_text": "",
            "error": str(exc),
        }


def source_urls_to_fetch(conn: sqlite3.Connection, verified_only: bool, limit: int) -> list[str]:
    fetched_ok = {
        row["source_url"]
        for row in conn.execute(
            """
            SELECT source_url
            FROM source_pages
            WHERE fetch_status = 'ok' AND LENGTH(TRIM(raw_text)) > 0
            """
        )
    }
    candidates: list[tuple[int, str]] = []

    def add(priority: int, value: str) -> None:
        url = value.strip()
        if not url or not is_url(url) or url in fetched_ok:
            return
        candidates.append((priority, url))

    if verified_only:
        query = """
            SELECT DISTINCT source_url FROM entity_claims
            WHERE evidence_status = 'verified_fact'
            ORDER BY source_url
        """
        for row in conn.execute(query):
            add(0, row["source_url"])
    else:
        for row in conn.execute(
            """
            SELECT DISTINCT source_url FROM entity_claims
            WHERE evidence_status = 'verified_fact'
            ORDER BY source_url
            """
        ):
            add(0, row["source_url"])
        for row in conn.execute(
            """
            SELECT website, source_urls
            FROM entity_intake_queue
            WHERE review_status IN ('queued', 'needs_more_source')
            ORDER BY priority, name
            """
        ):
            add(1, row["website"])
            for url in split_tags(row["source_urls"]):
                add(1, url)
        for row in conn.execute("SELECT DISTINCT source_url FROM entity_claims ORDER BY source_url"):
            add(2, row["source_url"])
        for row in conn.execute("SELECT DISTINCT website FROM industry_entities ORDER BY website"):
            add(3, row["website"])

    urls = []
    seen: set[str] = set()
    for _priority, url in sorted(candidates, key=lambda item: (item[0], item[1])):
        if url in seen:
            continue
        seen.add(url)
        urls.append(url)
    if limit:
        return urls[:limit]
    return urls


def source_fetch_agent(db_path: Path, verified_only: bool, limit: int) -> int:
    ensure_db(db_path)
    started = now_iso()
    with open_db(db_path) as conn:
        urls = source_urls_to_fetch(conn, verified_only=verified_only, limit=limit)
        fetched = 0
        for url in urls:
            result = fetch_url(url)
            text = str(result["raw_text"])
            page_id = make_id("page", url)
            insert_dict(
                conn,
                "source_pages",
                {
                    "page_id": page_id,
                    "source_url": url,
                    "fetched_at": now_iso(),
                    "status_code": int(result["status_code"]),
                    "fetch_status": result["fetch_status"],
                    "content_type": result["content_type"],
                    "title": result["title"],
                    "raw_text": text,
                    "text_hash": hashlib.sha256(text.encode("utf-8")).hexdigest() if text else "",
                    "error": result["error"],
                },
            )
            fetched += 1
        record_run(conn, "source_fetch_agent", "fetch_sources", "ok", started, len(urls), fetched, f"verified_only={verified_only}; limit={limit}")
        conn.commit()
    print(f"Source fetch agent fetched {fetched} URLs")
    return 0


def split_sentences(text: str) -> list[str]:
    rough = re.split(r"(?<=[.!?])\s+", text)
    return [sentence.strip() for sentence in rough if 40 <= len(sentence.strip()) <= 500]


def find_keyword_snippets(text: str) -> dict[str, str]:
    sentences = split_sentences(text)
    found: dict[str, str] = {}
    lower_cache = [(sentence, sentence.lower()) for sentence in sentences]
    for claim_type, keywords in KEYWORD_GROUPS.items():
        for sentence, lower in lower_cache:
            if any(keyword in lower for keyword in keywords):
                found[claim_type] = sentence
                break
    return found


def claim_extraction_agent(db_path: Path, limit: int) -> int:
    ensure_db(db_path)
    started = now_iso()
    with open_db(db_path) as conn:
        pages = conn.execute(
            """
            SELECT * FROM source_pages
            WHERE fetch_status = 'ok' AND LENGTH(TRIM(raw_text)) > 0
            ORDER BY fetched_at DESC
            """
        ).fetchall()
        if limit:
            pages = pages[:limit]
        claims_added = 0
        for page in pages:
            matches = conn.execute(
                """
                SELECT DISTINCT e.*
                FROM industry_entities e
                LEFT JOIN entity_claims c ON c.entity_id = e.entity_id
                WHERE e.website = ? OR c.source_url = ?
                """,
                (page["source_url"], page["source_url"]),
            ).fetchall()
            snippets = find_keyword_snippets(page["raw_text"])
            for entity in matches:
                for claim_type, snippet in snippets.items():
                    claim_id = make_id("claim", entity["entity_id"], claim_type, snippet)
                    exists = conn.execute("SELECT 1 FROM entity_claims WHERE claim_id = ?", (claim_id,)).fetchone()
                    if exists:
                        continue
                    claim_text = f"Source text for {entity['name']} contains {claim_type.replace('_', ' ')} evidence."
                    insert_dict(
                        conn,
                        "entity_claims",
                        {
                            "claim_id": claim_id,
                            "entity_id": entity["entity_id"],
                            "entity_name": entity["name"],
                            "claim_type": claim_type,
                            "claim": claim_text,
                            "source_url": page["source_url"],
                            "source_type": "fetched_source_page",
                            "source_quality": "primary",
                            "source_tier": "public_web",
                            "evidence_status": "verified_fact",
                            "last_verified_at": now_iso()[:10],
                            "notes": "Agent-extracted source-text observation. Human review still required before paper use.",
                            "claim_confidence": 82,
                            "source_page_id": page["page_id"],
                            "source_text_snippet": snippet,
                            "paper_ready": 0,
                        },
                    )
                    claims_added += 1
        record_run(conn, "claim_extraction_agent", "extract_claims", "ok", started, len(pages), claims_added, "Generated atomic source-text observation claims.")
        conn.commit()
    print(f"Claim extraction agent added {claims_added} claims")
    return 0


def classification_agent(db_path: Path) -> int:
    ensure_db(db_path)
    started = now_iso()
    with open_db(db_path) as conn:
        entities = conn.execute("SELECT * FROM industry_entities").fetchall()
        suggestions = 0
        for entity in entities:
            text_rows = conn.execute(
                """
                SELECT source_text_snippet
                FROM entity_claims
                WHERE entity_id = ? AND LENGTH(TRIM(source_text_snippet)) > 0
                """,
                (entity["entity_id"],),
            ).fetchall()
            joined = " ".join(row["source_text_snippet"].lower() for row in text_rows)
            if not joined:
                continue
            class_scores: dict[str, int] = {}
            for asset_class, keywords in CLASS_KEYWORDS.items():
                class_scores[asset_class] = sum(1 for keyword in keywords if keyword in joined)
            best_class, best_score = max(class_scores.items(), key=lambda item: item[1])
            if best_score == 0:
                continue
            suggested_fit = min(100, max(45, int(entity["fit_score"]) + best_score * 2))
            suggestion_id = make_id("suggestion", entity["entity_id"], best_class, str(best_score))
            insert_dict(
                conn,
                "classification_suggestions",
                {
                    "suggestion_id": suggestion_id,
                    "run_id": "pending",
                    "entity_id": entity["entity_id"],
                    "suggested_primary_asset_class": best_class,
                    "suggested_secondary_asset_classes": entity["secondary_asset_classes"],
                    "suggested_instrument_types": entity["instrument_types"],
                    "suggested_fit_score": suggested_fit,
                    "rationale": f"Fetched source text matched {best_score} keyword(s) for {best_class}. Current primary class is {entity['primary_asset_class']}.",
                    "confidence_score": min(90, 50 + best_score * 10),
                    "status": "proposed",
                    "created_at": now_iso(),
                },
            )
            suggestions += 1
        run_id = record_run(conn, "classification_agent", "classify", "ok", started, len(entities), suggestions, "Created non-destructive classification suggestions.")
        conn.execute("UPDATE classification_suggestions SET run_id = ? WHERE run_id = 'pending'", (run_id,))
        conn.commit()
    print(f"Classification agent created/updated {suggestions} suggestions")
    return 0


def domain(value: str) -> str:
    parsed = urlparse(value)
    host = parsed.netloc.lower().removeprefix("www.")
    return host


def dedupe_agent(db_path: Path) -> int:
    ensure_db(db_path)
    started = now_iso()
    with open_db(db_path) as conn:
        rows = [dict(row) for row in conn.execute("SELECT entity_id, name, website FROM industry_entities")]
        flagged = 0
        for left_index, left in enumerate(rows):
            for right in rows[left_index + 1 :]:
                same_name = slug(left["name"]) == slug(right["name"])
                same_domain = domain(left["website"]) and domain(left["website"]) == domain(right["website"])
                if not (same_name or same_domain):
                    continue
                target_id = "|".join(sorted([left["entity_id"], right["entity_id"]]))
                feedback_id = make_id("feedback", "duplicate", target_id)
                rationale = f"Possible duplicate detected by {'name' if same_name else 'domain'} match: {left['name']} / {right['name']}."
                insert_dict(
                    conn,
                    "review_feedback",
                    {
                        "feedback_id": feedback_id,
                        "target_type": "entity_pair",
                        "target_id": target_id,
                        "label": "duplicate",
                        "reviewer": "dedupe_agent",
                        "rationale": rationale,
                        "created_at": now_iso(),
                        "applied_to_learning": 0,
                    },
                )
                flagged += 1
        record_run(conn, "dedupe_agent", "dedupe", "ok", started, len(rows), flagged, "Flagged possible duplicate entity pairs for human review.")
        conn.commit()
    print(f"Dedupe agent flagged {flagged} possible duplicates")
    return 0


def candidate_source_pages(conn: sqlite3.Connection, lead: sqlite3.Row | dict[str, str]) -> list[sqlite3.Row]:
    urls = [str(lead["website"]).strip()]
    urls.extend(split_tags(str(lead["source_urls"])))
    unique_urls = []
    seen: set[str] = set()
    for url in urls:
        if not is_url(url) or url in seen:
            continue
        seen.add(url)
        unique_urls.append(url)
    if not unique_urls:
        return []
    placeholders = ", ".join("?" for _ in unique_urls)
    return conn.execute(
        f"""
        SELECT *
        FROM source_pages
        WHERE fetch_status = 'ok'
          AND LENGTH(TRIM(raw_text)) > 0
          AND source_url IN ({placeholders})
        ORDER BY
          CASE WHEN source_url = ? THEN 0 ELSE 1 END,
          fetched_at DESC
        """,
        [*unique_urls, str(lead["website"]).strip()],
    ).fetchall()


def duplicate_intake_reason(lead: dict[str, str], entity_rows: list[dict[str, str]]) -> str:
    lead_name = normalize_name(lead["name"])
    lead_domain = domain(lead["website"])
    for row in entity_rows:
        if normalize_name(row["name"]) == lead_name:
            return f"duplicate entity name: {row['name']}"
        if lead_domain and domain(row["website"]) == lead_domain:
            return f"duplicate entity domain: {row['website']}"
    return ""


def class_scores(text: str) -> dict[str, int]:
    lower = text.lower()
    return {
        asset_class: sum(1 for keyword in keywords if keyword in lower)
        for asset_class, keywords in CLASS_KEYWORDS.items()
    }


def infer_intake_asset_class(lead: dict[str, str], text: str) -> tuple[str, int, str]:
    target = lead["target_asset_class"]
    if target == "Instrument":
        return "", 0, "Instrument is a financing mechanism, not a primary entity asset class"
    scores = class_scores(text)
    if target in CLASS_KEYWORDS and scores.get(target, 0) > 0:
        return target, scores[target], f"target class {target} matched source text"
    if target not in {"", "All", "Unknown Candidate"} and target not in CLASS_KEYWORDS:
        return target, 1, f"target class {target} retained from intake queue"
    non_uvc_scores = {asset: score for asset, score in scores.items() if asset != "UVC"}
    best_class, best_score = max(non_uvc_scores.items(), key=lambda item: item[1])
    if best_score >= 2:
        return best_class, best_score, f"inferred {best_class} from {best_score} source-text keyword matches"
    if target == "UVC" and scores.get("UVC", 0) > 0:
        return "UVC", scores["UVC"], "target class UVC matched source text"
    return "", 0, "no sufficiently specific non-unicorn asset-class fit found"


def source_supports_intake(lead: dict[str, str], page: sqlite3.Row) -> tuple[bool, dict[str, object], str, str]:
    text = f"{page['title']} {page['raw_text']}"
    lower = text.lower()
    name_tokens = significant_tokens(lead["name"])
    role_tokens = significant_tokens(lead["target_entity_type"])
    name_supported = any(token in lower for token in name_tokens)
    role_supported = any(token in lower for token in role_tokens)
    website_domain = domain(lead["website"])
    page_domain = domain(page["source_url"])
    website_supported = bool(website_domain and (website_domain == page_domain or website_domain in lower))
    asset_class, asset_score, asset_reason = infer_intake_asset_class(lead, text)
    snippets = find_keyword_snippets(text)
    source_snippet = next(iter(snippets.values()), "")
    if not source_snippet:
        for sentence in split_sentences(text):
            sentence_lower = sentence.lower()
            if any(token in sentence_lower for token in name_tokens + role_tokens):
                source_snippet = sentence
                break
    checks = {
        "name_supported": name_supported,
        "website_supported": website_supported,
        "role_supported": role_supported,
        "asset_class": asset_class,
        "asset_score": asset_score,
        "asset_reason": asset_reason,
        "source_url": page["source_url"],
    }
    if not name_supported:
        return False, checks, "", "source text does not directly support the entity name"
    if not website_supported:
        return False, checks, "", "source text or URL does not support the entity website/domain"
    if not role_supported:
        return False, checks, "", "source text does not directly support the entity role"
    if not asset_class:
        return False, checks, "", asset_reason
    if not source_snippet:
        return False, checks, "", "no usable source snippet found"
    return True, checks, source_snippet, ""


def unique_entity_id(name: str, existing_ids: set[str]) -> str:
    base = slug(name)
    candidate = base
    suffix = 2
    while candidate in existing_ids:
        candidate = f"{base}-{suffix}"
        suffix += 1
    return candidate


def update_intake_rows(updates: dict[str, dict[str, str]]) -> None:
    path = evidence_path("entity_intake_queue.csv")
    rows = read_csv_rows(path)
    fieldnames = csv_fieldnames(path, rows)
    for row in rows:
        update = updates.get(row["lead_id"])
        if update:
            row.update(update)
    write_csv_rows(path, rows, fieldnames)


def ensure_source_registry_rows(source_urls: list[str], lead_name: str) -> None:
    path = evidence_path("source_registry.csv")
    rows = read_csv_rows(path)
    fieldnames = csv_fieldnames(path, rows)
    existing_urls = {row["source_url"] for row in rows}
    for url in source_urls:
        if not is_url(url) or url in existing_urls:
            continue
        rows.append(
            {
                "source_url": url,
                "source_name": f"{lead_name} intake source",
                "source_type": "intake_source",
                "source_quality": "unknown",
                "license_or_access": "public web",
                "notes": "Added by intake promotion agent; review source quality before paper use.",
                "last_checked": now_iso()[:10],
            }
        )
        existing_urls.add(url)
    write_csv_rows(path, rows, fieldnames)


def build_promoted_rows(
    lead: dict[str, str],
    page: sqlite3.Row,
    source_snippet: str,
    asset_class: str,
    existing_ids: set[str],
) -> tuple[dict[str, str], dict[str, str]]:
    if asset_class == "Instrument":
        raise ValueError("Instrument cannot be promoted as a primary entity asset class")
    entity_id = unique_entity_id(lead["name"], existing_ids)
    secondary = "Unknown Candidate" if asset_class != "Unknown Candidate" else "UVC"
    entity_row = {
        "entity_id": entity_id,
        "name": lead["name"],
        "primary_asset_class": asset_class,
        "secondary_asset_classes": secondary,
        "entity_type": lead["target_entity_type"],
        "website": lead["website"],
        "active_status": lead["active_status"],
        "source_tier": lead["source_tier"],
        "geography": "Unknown",
        "sector_focus": "Unknown",
        "capital_model": "Unknown",
        "instrument_types": "unknown",
        "target_company_profile": lead["target_entity_type"],
        "non_unicorn_thesis": "candidate supports industry mapping outside or adjacent to classic unicorn VC",
        "ecosystem_role": lead["target_entity_type"],
        "fit_score": "62",
        "evidence_status": "candidate_evidence",
        "last_verified_at": now_iso()[:10],
        "notes": "Promoted from entity_intake_queue by intake verification agent; human review required before paper use.",
    }
    claim_row = {
        "claim_id": f"claim-{entity_id}-intake-001",
        "entity_id": entity_id,
        "entity_name": lead["name"],
        "claim_type": "intake_promotion",
        "claim": f"{lead['name']} is a candidate {asset_class} industry entity based on fetched source text describing its role as {lead['target_entity_type']}.",
        "source_url": page["source_url"],
        "source_type": "fetched_source_page",
        "source_quality": source_quality_for_url(page["source_url"]),
        "source_tier": lead["source_tier"],
        "evidence_status": "candidate_evidence",
        "last_verified_at": now_iso()[:10],
        "notes": f"Source snippet retained in intake_promotion_reviews; not paper-ready. Snippet: {source_snippet[:180]}",
    }
    return entity_row, claim_row


def write_promotion_review(
    conn: sqlite3.Connection,
    lead: dict[str, str],
    run_id: str,
    status: str,
    source_url: str = "",
    source_page_id: str = "",
    source_snippet: str = "",
    checks: dict[str, object] | None = None,
    rejection_reason: str = "",
    entity_row: dict[str, str] | None = None,
    claim_row: dict[str, str] | None = None,
) -> None:
    entity_id = entity_row["entity_id"] if entity_row else ""
    asset_class = entity_row["primary_asset_class"] if entity_row else ""
    review_id = make_id("promotion", lead["lead_id"], status, source_url, entity_id)
    insert_dict(
        conn,
        "intake_promotion_reviews",
        {
            "review_id": review_id,
            "lead_id": lead["lead_id"],
            "run_id": run_id,
            "status": status,
            "name": lead["name"],
            "proposed_entity_id": entity_id,
            "proposed_primary_asset_class": asset_class,
            "proposed_entity_row": json.dumps(entity_row or {}, sort_keys=True),
            "proposed_claim_row": json.dumps(claim_row or {}, sort_keys=True),
            "source_url": source_url,
            "source_page_id": source_page_id,
            "source_snippet": source_snippet,
            "checks": json.dumps(checks or {}, sort_keys=True),
            "rejection_reason": rejection_reason,
            "created_at": now_iso(),
        },
    )


def intake_promotion_agent(db_path: Path, limit: int, promote: bool) -> int:
    ensure_db(db_path)
    started = now_iso()
    promoted = 0
    reviewed = 0
    csv_entity_rows = read_csv_rows(evidence_path("industry_entities.csv"))
    csv_claim_rows = read_csv_rows(evidence_path("entity_claims.csv"))
    intake_rows = read_csv_rows(evidence_path("entity_intake_queue.csv"))
    entity_fieldnames = csv_fieldnames(evidence_path("industry_entities.csv"), csv_entity_rows)
    claim_fieldnames = csv_fieldnames(evidence_path("entity_claims.csv"), csv_claim_rows)
    existing_ids = {row["entity_id"] for row in csv_entity_rows}
    eligible = [row for row in intake_rows if row["review_status"] in {"queued", "needs_more_source"}]
    if limit:
        eligible = eligible[:limit]

    with open_db(db_path) as conn:
        exec_script(conn)
        run_id = record_run(
            conn,
            "intake_promotion_agent",
            "promote_intake" if promote else "verify_intake",
            "ok",
            started,
            len(eligible),
            0,
            "Started intake verification.",
        )
        for row in intake_rows:
            insert_dict(conn, "entity_intake_queue", row)
        intake_updates: dict[str, dict[str, str]] = {}
        for lead in eligible:
            reviewed += 1
            duplicate_reason = duplicate_intake_reason(lead, csv_entity_rows)
            if duplicate_reason:
                write_promotion_review(conn, lead, run_id, "duplicate", rejection_reason=duplicate_reason)
                if promote:
                    intake_updates[lead["lead_id"]] = {
                        "review_status": "duplicate",
                        "notes": f"{lead['notes']} Intake promotion agent marked duplicate: {duplicate_reason}",
                    }
                continue

            pages = candidate_source_pages(conn, lead)
            if not pages:
                reason = "no fetched direct source text available for intake lead"
                write_promotion_review(conn, lead, run_id, "needs_more_source", rejection_reason=reason)
                if promote:
                    intake_updates[lead["lead_id"]] = {
                        "review_status": "needs_more_source",
                        "evidence_status": "needs_verification",
                        "notes": f"{lead['notes']} Intake promotion agent needs more source text: {reason}",
                    }
                continue

            accepted: tuple[sqlite3.Row, dict[str, object], str, str] | None = None
            last_page: sqlite3.Row | None = None
            last_reason = ""
            last_checks: dict[str, object] = {}
            for page in pages:
                passed, checks, snippet, reason = source_supports_intake(lead, page)
                last_page = page
                if passed:
                    accepted = (page, checks, snippet, str(checks["asset_class"]))
                    break
                last_reason = reason
                last_checks = checks
            if not accepted:
                write_promotion_review(
                    conn,
                    lead,
                    run_id,
                    "needs_more_source",
                    source_url=last_page["source_url"] if last_page else "",
                    source_page_id=last_page["page_id"] if last_page else "",
                    checks=last_checks,
                    rejection_reason=last_reason,
                )
                if promote:
                    intake_updates[lead["lead_id"]] = {
                        "review_status": "needs_more_source",
                        "evidence_status": "needs_verification",
                        "notes": f"{lead['notes']} Intake promotion agent needs more source support: {last_reason}",
                    }
                continue

            page, checks, source_snippet, asset_class = accepted
            entity_row, claim_row = build_promoted_rows(lead, page, source_snippet, asset_class, existing_ids)
            write_promotion_review(
                conn,
                lead,
                run_id,
                "ready_for_promotion" if not promote else "promoted",
                source_url=page["source_url"],
                source_page_id=page["page_id"],
                source_snippet=source_snippet,
                checks=checks,
                entity_row=entity_row,
                claim_row=claim_row,
            )
            if not promote:
                continue

            csv_entity_rows.append(entity_row)
            csv_claim_rows.append(claim_row)
            existing_ids.add(entity_row["entity_id"])
            ensure_source_registry_rows([lead["website"], *split_tags(lead["source_urls"]), page["source_url"]], lead["name"])
            sqlite_entity = dict(entity_row)
            sqlite_entity["fit_score"] = int(sqlite_entity["fit_score"])
            insert_dict(conn, "industry_entities", sqlite_entity)
            sqlite_claim = dict(claim_row)
            sqlite_claim["claim_confidence"] = default_claim_confidence(sqlite_claim["evidence_status"])
            sqlite_claim["source_page_id"] = page["page_id"]
            sqlite_claim["source_text_snippet"] = source_snippet
            sqlite_claim["paper_ready"] = 0
            insert_dict(conn, "entity_claims", sqlite_claim)
            for source_row in read_csv_rows(evidence_path("source_registry.csv")):
                insert_dict(conn, "source_registry", source_row)
            intake_updates[lead["lead_id"]] = {
                "review_status": "promoted",
                "evidence_status": "candidate_evidence",
                "notes": f"{lead['notes']} Promoted as {asset_class} candidate from {page['source_url']}. Human review required before paper use.",
            }
            promoted += 1

        if promote:
            write_csv_rows(evidence_path("industry_entities.csv"), csv_entity_rows, entity_fieldnames)
            write_csv_rows(evidence_path("entity_claims.csv"), csv_claim_rows, claim_fieldnames)
            update_intake_rows(intake_updates)
            for lead_id, update in intake_updates.items():
                conn.execute(
                    """
                    UPDATE entity_intake_queue
                    SET review_status = ?,
                        evidence_status = COALESCE(NULLIF(?, ''), evidence_status),
                        notes = ?
                    WHERE lead_id = ?
                    """,
                    (
                        update.get("review_status", ""),
                        update.get("evidence_status", ""),
                        update.get("notes", ""),
                        lead_id,
                    ),
                )
        conn.execute(
            """
            UPDATE agent_runs
            SET output_count = ?, notes = ?
            WHERE run_id = ?
            """,
            (promoted if promote else reviewed, f"Reviewed {reviewed} intake leads; promoted {promoted}.", run_id),
        )
        conn.commit()

    verb = "promoted" if promote else "reviewed"
    print(f"Intake promotion agent {verb} {promoted if promote else reviewed} leads")
    return 0


def verify_intake_agent(db_path: Path, limit: int) -> int:
    return intake_promotion_agent(db_path, limit=limit, promote=False)


def promote_intake_agent(db_path: Path, limit: int) -> int:
    return intake_promotion_agent(db_path, limit=limit, promote=True)


def promotion_loop(db_path: Path, limit: int) -> int:
    status = promote_intake_agent(db_path, limit=limit)
    export_rankings(db_path, 0)
    validation_status = validate(db_path, strict=True)
    return status or validation_status


def evolution_agent(db_path: Path) -> int:
    ensure_db(db_path)
    started = now_iso()
    proposals: list[dict[str, object]] = []
    with open_db(db_path) as conn:
        class_counts = {row["primary_asset_class"]: row["count"] for row in conn.execute("SELECT primary_asset_class, COUNT(*) AS count FROM industry_entities GROUP BY primary_asset_class")}
        total_entities = sum(class_counts.values())
        smv_count = class_counts.get("SMV", 0)
        lmv_count = class_counts.get("LMV", 0)
        fetched_failures = conn.execute("SELECT COUNT(*) FROM source_pages WHERE fetch_status != 'ok'").fetchone()[0]
        unreviewed_verified = conn.execute("SELECT COUNT(*) FROM entity_claims WHERE evidence_status = 'verified_fact' AND paper_ready = 0").fetchone()[0]

        checks = [
            ("coverage", "SMV", smv_count < 75, f"SMV has {smv_count} entities; target is 75 before paper draft.", "Prioritize SMV scrape targets and growth-equity/software-acquirer lanes."),
            ("coverage", "All", total_entities < 250, f"Atlas has {total_entities} entities; target is 250 for next wave.", "Run broad scrape lanes after SMV-specific expansion."),
            ("coverage", "LMV", lmv_count < 25, f"LMV has {lmv_count} entities; target is 25 for a credible emerging-category view.", "Add indie/AI-native micro venture sources and communities."),
            ("verification", "source_pages", fetched_failures > 0, f"{fetched_failures} fetched source pages failed.", "Retry failed URLs later and look for alternate official or press sources."),
            ("review", "entity_claims", unreviewed_verified > 0, f"{unreviewed_verified} verified source-text observations are not paper-ready.", "Queue top-ranked verified observations for human review before paper use."),
        ]
        for proposal_type, target, condition, rationale, recommendation in checks:
            if not condition:
                continue
            proposal_id = make_id("proposal", proposal_type, target, rationale)
            row = {
                "proposal_id": proposal_id,
                "run_id": "pending",
                "proposal_type": proposal_type,
                "target": target,
                "recommendation": recommendation,
                "rationale": rationale,
                "status": "proposed",
                "created_at": now_iso(),
            }
            insert_dict(conn, "evolution_proposals", row)
            proposals.append(row)
        run_id = record_run(conn, "evolution_agent", "evolve", "ok", started, 5, len(proposals), "Generated non-mutating improvement proposals from coverage and verification metrics.")
        conn.execute("UPDATE evolution_proposals SET run_id = ? WHERE run_id = 'pending'", (run_id,))
        conn.commit()

    EXPORTS.mkdir(parents=True, exist_ok=True)
    report = [
        "# Research Agent Evolution Report",
        "",
        f"Generated: {now_iso()}",
        "",
        "## Proposed Improvements",
    ]
    if proposals:
        for proposal in proposals:
            report.append(f"- **{proposal['target']}**: {proposal['recommendation']} Rationale: {proposal['rationale']}")
    else:
        report.append("- No evolution proposals generated.")
    (EXPORTS / "evolution_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"Evolution agent wrote {len(proposals)} proposals")
    return 0


def add_feedback(
    db_path: Path,
    target_type: str,
    target_id: str,
    label: str,
    rationale: str,
    reviewer: str,
    direct_evidence: str,
) -> int:
    ensure_db(db_path)
    allowed = {"accepted", "rejected", "needs_more_source", "wrong_bucket", "duplicate", "too_broad", "paper_ready"}
    if label not in allowed:
        print(f"Invalid feedback label: {label}", file=sys.stderr)
        return 1
    with open_db(db_path) as conn:
        feedback_id = make_id("feedback", target_type, target_id, label, rationale)
        insert_dict(
            conn,
            "review_feedback",
            {
                "feedback_id": feedback_id,
                "target_type": target_type,
                "target_id": target_id,
                "label": label,
                "reviewer": reviewer,
                "rationale": rationale,
                "created_at": now_iso(),
                "applied_to_learning": 0,
            },
        )
        if target_type == "claim":
            review_id = make_id("review", target_id, label, direct_evidence)
            insert_dict(
                conn,
                "claim_reviews",
                {
                    "review_id": review_id,
                    "claim_id": target_id,
                    "review_status": label,
                    "reviewer": reviewer,
                    "direct_evidence": direct_evidence,
                    "rationale": rationale,
                    "created_at": now_iso(),
                    "paper_ready": 1 if label == "paper_ready" else 0,
                },
            )
            if label == "paper_ready":
                conn.execute("UPDATE entity_claims SET paper_ready = 1 WHERE claim_id = ?", (target_id,))
        conn.commit()
    print(f"Recorded feedback {label} for {target_type}:{target_id}")
    return 0


def validate(db_path: Path, strict: bool) -> int:
    errors = validate_database(db_path, strict_verified_sources=strict, exact_csv_counts=False)
    if errors:
        print("Research-agent SQLite validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Research-agent SQLite validation passed")
    return 0


def write_run_report(db_path: Path, mode: str, fetch_limit: int, verified_only: bool, status: int) -> None:
    EXPORTS.mkdir(parents=True, exist_ok=True)
    with open_db(db_path) as conn:
        counts = {
            table: conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            for table in [
                "industry_entities",
                "entity_claims",
                "entity_intake_queue",
                "discovery_candidates",
                "source_pages",
                "classification_suggestions",
                "intake_promotion_reviews",
                "review_feedback",
                "claim_reviews",
                "evolution_proposals",
            ]
        }
        latest_runs = conn.execute(
            """
            SELECT agent_name, stage, status, input_count, output_count, completed_at, notes
            FROM agent_runs
            ORDER BY completed_at DESC
            LIMIT 8
            """
        ).fetchall()
        paper_ready_count = conn.execute("SELECT COUNT(*) FROM entity_claims WHERE paper_ready = 1").fetchone()[0]

    lines = [
        "# Research Agent Run Report",
        "",
        f"Generated: {now_iso()}",
        f"Mode: {mode}",
        f"Fetch limit: {fetch_limit}",
        f"Verified only: {verified_only}",
        f"Validation status: {'passed' if status == 0 else 'failed'}",
        f"Paper-ready claims: {paper_ready_count}",
        "",
        "## Counts",
    ]
    for table, count in counts.items():
        lines.append(f"- {table}: {count}")
    lines.extend(["", "## Latest Agent Runs"])
    for run in latest_runs:
        lines.append(
            f"- {run['completed_at']} {run['agent_name']}:{run['stage']} "
            f"{run['status']} input={run['input_count']} output={run['output_count']} - {run['notes']}"
        )
    (EXPORTS / "research_agent_run_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_loop(db_path: Path, fetch_limit: int, verified_only: bool, reset_from_csv: bool = False, mode: str = "run-loop") -> int:
    if reset_from_csv:
        import_csvs(db_path)
    else:
        ensure_db(db_path)
    discovery_agent(db_path)
    source_fetch_agent(db_path, verified_only=verified_only, limit=fetch_limit)
    claim_extraction_agent(db_path, limit=fetch_limit)
    classification_agent(db_path)
    dedupe_agent(db_path)
    evolution_agent(db_path)
    export_rankings(db_path, 0)
    status = validate(db_path, strict=True)
    write_run_report(db_path, mode=mode, fetch_limit=fetch_limit, verified_only=verified_only, status=status)
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(DEFAULT_DB))
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("discover")

    fetch = sub.add_parser("fetch-sources")
    fetch.add_argument("--verified-only", action="store_true")
    fetch.add_argument("--limit", type=int, default=10)

    extract = sub.add_parser("extract-claims")
    extract.add_argument("--limit", type=int, default=10)

    sub.add_parser("classify")
    sub.add_parser("dedupe")
    sub.add_parser("evolve")

    verify_intake = sub.add_parser("verify-intake")
    verify_intake.add_argument("--limit", type=int, default=10)

    promote_intake = sub.add_parser("promote-intake")
    promote_intake.add_argument("--limit", type=int, default=10)

    promotion = sub.add_parser("promotion-loop")
    promotion.add_argument("--limit", type=int, default=10)

    feedback = sub.add_parser("feedback")
    feedback.add_argument("--target-type", required=True)
    feedback.add_argument("--target-id", required=True)
    feedback.add_argument("--label", required=True)
    feedback.add_argument("--rationale", required=True)
    feedback.add_argument("--reviewer", default="human")
    feedback.add_argument("--direct-evidence", default="")

    validate_cmd = sub.add_parser("validate")
    validate_cmd.add_argument("--strict", action="store_true")

    loop = sub.add_parser("run-loop")
    loop.add_argument("--fetch-limit", type=int, default=10)
    loop.add_argument("--verified-only", action="store_true")
    loop.add_argument("--reset-from-csv", action="store_true")

    hourly = sub.add_parser("hourly-loop")
    hourly.add_argument("--fetch-limit", type=int, default=5)
    hourly.add_argument("--verified-only", action="store_true")

    args = parser.parse_args()
    db_path = Path(args.db)

    if args.command == "discover":
        return discovery_agent(db_path)
    if args.command == "fetch-sources":
        return source_fetch_agent(db_path, verified_only=args.verified_only, limit=args.limit)
    if args.command == "extract-claims":
        return claim_extraction_agent(db_path, limit=args.limit)
    if args.command == "classify":
        return classification_agent(db_path)
    if args.command == "dedupe":
        return dedupe_agent(db_path)
    if args.command == "evolve":
        return evolution_agent(db_path)
    if args.command == "verify-intake":
        return verify_intake_agent(db_path, limit=args.limit)
    if args.command == "promote-intake":
        return promote_intake_agent(db_path, limit=args.limit)
    if args.command == "promotion-loop":
        return promotion_loop(db_path, limit=args.limit)
    if args.command == "feedback":
        return add_feedback(db_path, args.target_type, args.target_id, args.label, args.rationale, args.reviewer, args.direct_evidence)
    if args.command == "validate":
        return validate(db_path, strict=args.strict)
    if args.command == "run-loop":
        return run_loop(db_path, fetch_limit=args.fetch_limit, verified_only=args.verified_only, reset_from_csv=args.reset_from_csv)
    if args.command == "hourly-loop":
        return run_loop(db_path, fetch_limit=args.fetch_limit, verified_only=args.verified_only, reset_from_csv=False, mode="hourly-loop")
    return 1


if __name__ == "__main__":
    sys.exit(main())
