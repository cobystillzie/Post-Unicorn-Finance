"""
Phase 4 — Extract firm names from article-style aggregator pages.

The previous DDG discovery hits a yield ceiling because most queries return firm
HOMEPAGES (one firm per page). Article-style aggregators ("List of search fund
investors", "60+ firms that buy SaaS", etc.) list 20-100 firms in a single page.
Crawling these gives much higher per-fetch yield.

Strategy:
 1. Curated list of high-signal article URLs (verified via WebSearch).
 2. For each: fetch HTML, extract <a> tags + heading text.
 3. Match heading/bold patterns that look like firm names:
    - Pascal-case 2-4 words at start of line / inside H2/H3
    - Followed by descriptive prose ("X is a firm that...", "X invests in...")
 4. Pair extracted name with an anchor href if one exists for it on the page.
 5. Dedupe against existing atlas + intake queue.
 6. Append to entity_intake_queue.csv with appropriate target_asset_class.

Run:
  python scripts/extract_firms_from_articles.py
  python scripts/atlas_sqlite.py build   # sync CSV -> SQLite
  python scripts/research_agents.py fetch-sources --limit 500
  python scripts/research_agents.py promote-intake --limit 300
"""
from __future__ import annotations

import csv
import hashlib
import random
import re
import sys
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "data" / "evidence"
INTAKE_PATH = EVIDENCE / "entity_intake_queue.csv"
SOURCE_PATH = EVIDENCE / "source_registry.csv"
ENTITIES_PATH = EVIDENCE / "industry_entities.csv"

USER_AGENT = "post-unicorn-finance-article-crawler/0.1 (+local evidence discovery)"

# Each entry: (slug, url, target_asset_class, notes)
ARTICLES = [
    # Search funds
    ("leland_top_search_funds", "https://www.joinleland.com/library/a/list-of-search-funds", "Search/ETA", "Leland comprehensive search-fund list"),
    ("leland_search_fund_investors", "https://www.joinleland.com/library/a/search-fund-investors", "Search/ETA", "Top 20 search-fund investors"),
    ("leland_search_fund_accelerators", "https://www.joinleland.com/library/a/search-fund-accelerators", "Search/ETA", "Top search-fund accelerators"),
    ("onrec_search_fund_db", "https://www.onrec.com/news/database-top-search-fund-investors", "Search/ETA", "Database of top search-fund investors $1M-5M EBITDA"),
    ("nextgen_eta_resources", "https://nextgengp.com/resources/", "Search/ETA", "NextGen GP ETA & search fund resource library"),
    # Permanent equity / holdcos / serial acquirers
    ("theygotacquired_saas", "https://theygotacquired.com/resources/firms-that-buy-saas/", "Portfolio Capital", "60+ firms that buy SaaS"),
    ("quartr_serial_acquirers", "https://quartr.com/insights/company-research/our-list-of-100-eminent-serial-acquirers", "Portfolio Capital", "100 eminent serial acquirers"),
    ("acquirers_list", "https://www.acquirers.com/serial-acquirer-list", "Portfolio Capital", "Serial acquirer list"),
    ("softwareequity_top_buyers", "https://softwareequity.com/top-strategic-buyers", "Portfolio Capital", "Top strategic software buyers"),
    ("rollupeurope_aggregators", "https://rollupeurope.com/p/how-30-software-aggregators-live-and-breathe-insights-from-our-2nd-software-serial-acquirer-summit", "Portfolio Capital", "30+ European software aggregators"),
    # SaaS PE / SMV
    ("dakota_saas_pe", "https://www.dakota.com/resources/blog/top-10-private-equity-firms-investing-in-saas", "SMV", "Top 10 PE firms investing in SaaS"),
    ("softwareequity_software_pe", "https://softwareequity.com/blog/top-software-private-equity-firms", "SMV", "Top software PE firms"),
    ("prospectrock_micro_pe", "https://prospectrockpartners.com/the-rise-of-micro-private-equity/", "SMV", "Micro PE landscape"),
    # Indie / bootstrap / micro
    ("indiehackers_alt_funding", "https://www.indiehackers.com/article/the-alternative-funding-options-for-saas-startups-cheat-sheet-c770f5991e", "LMV", "Alternative funding options cheat sheet"),
    ("alignify_indie_hackers", "https://alignify.co/insights/indie-hackers", "LMV", "Indie hacker bootstrapped success stories 2026"),
    ("firsto_indie_alternatives", "https://firsto.co/blog/indie-hackers-alternatives-2026", "LMV", "Indie hacker community alternatives"),
]

# Words that look like firm names but aren't (filter list)
NOISE_TOKENS = {
    "list", "top", "best", "review", "guide", "introduction", "overview",
    "summary", "conclusion", "what", "why", "how", "when", "where", "who",
    "the", "a", "an", "is", "are", "was", "were", "this", "that", "these", "those",
    "key", "main", "primary", "secondary", "first", "second", "third", "next",
    "click", "read", "more", "learn", "see", "view", "find", "search",
    "subscribe", "share", "follow", "contact", "about", "home", "blog", "news",
    "article", "post", "page", "section", "chapter", "appendix", "footer", "header",
    "menu", "navigation", "sidebar", "comments", "reply", "edit", "delete",
    "login", "signup", "register", "account", "profile", "settings", "logout",
    "image", "photo", "video", "audio", "media", "download", "upload", "file",
    "table", "figure", "chart", "graph", "diagram", "illustration",
    "year", "month", "week", "day", "hour", "minute", "second",
    "january", "february", "march", "april", "may", "june", "july",
    "august", "september", "october", "november", "december",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "summary", "conclusion", "introduction",
}

# Stop words / generic blog vocabulary that's never a firm
GENERIC_PHRASES = {
    "private equity", "venture capital", "investment fund", "growth equity",
    "asset management", "portfolio company", "operating company", "small business",
    "limited partner", "general partner", "managing director", "managing partner",
    "search fund", "search funds", "permanent equity", "patient capital",
    "holding company", "holding companies", "venture studio", "venture studios",
    "private company", "private companies", "small business", "small businesses",
    "sponsorship", "sponsorship", "membership", "education", "training",
    "what is", "what are", "what does", "how to", "why use", "when to",
    "table of contents", "frequently asked questions", "read more",
    "leave a comment", "post navigation", "related posts", "you may also like",
}


# --- Utilities ----------------------------------------------------------------

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


class ArticleParser(HTMLParser):
    """Extract:
       1. Headings (h1/h2/h3/h4) with their text content - candidate firm names
       2. Bold/strong text - candidate firm names
       3. Anchor tags - to pair names with URLs
    """
    HEADING_TAGS = {"h1", "h2", "h3", "h4"}
    EMPHASIS_TAGS = {"b", "strong"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.candidates: list[tuple[str, str]] = []  # (text, type)
        self.anchors: list[tuple[str, str]] = []  # (href, text)
        self._stack: list[str] = []
        self._buffer: list[str] = []
        self._current_href: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self.HEADING_TAGS or tag in self.EMPHASIS_TAGS:
            if not self._stack:
                self._buffer = []
            self._stack.append(tag)
        elif tag == "a":
            href = dict(attrs).get("href") or ""
            self._current_href = href
            if not self._stack:
                self._buffer = []

    def handle_endtag(self, tag: str) -> None:
        if tag in self.HEADING_TAGS or tag in self.EMPHASIS_TAGS:
            if self._stack and self._stack[-1] == tag:
                self._stack.pop()
                if not self._stack:
                    text = " ".join("".join(self._buffer).split()).strip()
                    if text and 2 <= len(text) <= 100:
                        self.candidates.append((text, tag))
                    self._buffer = []
        elif tag == "a" and self._current_href is not None:
            text = " ".join("".join(self._buffer).split()).strip() if not self._stack else ""
            self.anchors.append((self._current_href, text))
            self._current_href = None
            if not self._stack:
                self._buffer = []

    def handle_data(self, data: str) -> None:
        if self._stack or self._current_href is not None:
            self._buffer.append(data)


def looks_like_firm_name(text: str) -> bool:
    """Heuristics to decide if a heading-text candidate looks like a firm name."""
    s = text.strip()
    if len(s) < 3 or len(s) > 60:
        return False
    lower = s.lower()
    # filter out obvious headings
    if any(g in lower for g in GENERIC_PHRASES):
        return False
    # filter sentences (have punctuation in middle)
    if re.search(r"[.!?].+", s):
        return False
    # filter "What is" / "How to" style
    if re.match(r"^(what|how|why|when|where|who|the|a |an |is |are |these)\b", lower):
        return False
    # require at least one capitalized word
    words = [w for w in re.split(r"\s+", s) if w]
    if not words:
        return False
    if not any(w[0].isupper() for w in words):
        return False
    # token-level noise filter
    if all(w.lower() in NOISE_TOKENS for w in words):
        return False
    # has digits but not as a model name suggests stats/year (skip)
    if re.match(r"^\d+", s) or re.match(r"^[Tt]op\s+\d+", s):
        return False
    return True


def fetch_html(url: str, timeout: int = 25) -> tuple[str | None, str | None]:
    try:
        req = Request(url, headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.5",
        })
        with urlopen(req, timeout=timeout) as response:
            body = response.read(3_000_000)
            charset = response.headers.get_content_charset() or "utf-8"
            return body.decode(charset, errors="replace"), None
    except HTTPError as exc:
        return None, f"http_{exc.code}"
    except (URLError, TimeoutError, OSError) as exc:
        return None, f"network_{type(exc).__name__}"


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


# --- Main ---------------------------------------------------------------------

def crawl() -> int:
    intake_fields, intake_rows = read_csv_rows(INTAKE_PATH)
    source_fields, source_rows = read_csv_rows(SOURCE_PATH)
    _, entity_rows = read_csv_rows(ENTITIES_PATH)

    if not intake_fields or not source_fields:
        print("ERROR: missing intake/source CSVs", file=sys.stderr)
        return 1

    existing_keys: set[tuple[str, str]] = set()
    existing_names: set[str] = set()
    for r in intake_rows + entity_rows:
        n = normalize_name(r.get("name", ""))
        existing_keys.add((n, domain(r.get("website", ""))))
        existing_names.add(n)
    existing_source_urls = {r["source_url"] for r in source_rows}
    existing_lead_ids = {r.get("lead_id", "") for r in intake_rows}

    new_count = 0
    today = now_iso()[:10]

    for slug, url, target_class, notes in ARTICLES:
        print(f"[{slug}] fetching {url}", flush=True)
        if new_count > 0 or slug != ARTICLES[0][0]:
            time.sleep(2 + random.uniform(0, 2))
        html, err = fetch_html(url)
        if err or not html:
            print(f"  [{slug}] skipped: {err}")
            continue
        parser = ArticleParser()
        try:
            parser.feed(html)
        except Exception as exc:  # noqa: BLE001
            print(f"  [{slug}] parse error: {exc}")
            continue

        # Build name -> best URL map from anchors
        name_to_url: dict[str, str] = {}
        src_dom = domain(url)
        for href, text in parser.anchors:
            absolute = urljoin(url, href)
            p = urlparse(absolute)
            if p.scheme not in ("http", "https"):
                continue
            host = p.netloc.lower().lstrip("www.").split(":")[0]
            if not host or host == src_dom or host.endswith("." + src_dom):
                continue
            if any(host == b or host.endswith("." + b) for b in {
                "linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com",
                "youtube.com", "youtu.be", "medium.com", "substack.com", "github.com",
                "crunchbase.com", "pitchbook.com", "wikipedia.org",
                "joinleland.com",
            }):
                continue
            normalized = normalize_name(text)
            if normalized and 2 <= len(text) <= 60 and normalized not in name_to_url:
                # only short paths (entity homepages)
                segments = [s for s in p.path.strip("/").split("/") if s]
                if len(segments) <= 1:
                    name_to_url[normalized] = f"{p.scheme}://{p.netloc}/"

        # Candidate firm names from headings
        added_for_dir = 0
        seen_in_article: set[str] = set()
        for text, _kind in parser.candidates:
            if not looks_like_firm_name(text):
                continue
            normalized = normalize_name(text)
            if normalized in seen_in_article:
                continue
            seen_in_article.add(normalized)
            if normalized in existing_names:
                continue
            # find a URL for this name
            firm_url = name_to_url.get(normalized, "")
            if not firm_url:
                # No URL found - skip; we won't add a firm we can't fetch
                continue
            dom = domain(firm_url)
            key = (normalized, dom)
            if key in existing_keys:
                continue
            lead_id = make_id("intake-art", slug, dom)
            if lead_id in existing_lead_ids:
                continue
            new_row = {
                "lead_id": lead_id,
                "name": text,
                "lead_type": "article_extraction",
                "website": firm_url,
                "source_urls": f"{firm_url};{url}",
                "discovered_from": f"article:{slug}",
                "target_asset_class": target_class,
                "target_entity_type": f"article-listed {target_class} candidate",
                "active_status": "unknown",
                "source_tier": "medium",
                "priority": "medium",
                "evidence_status": "needs_verification",
                "review_status": "queued",
                "created_at": today,
                "notes": f"Extracted from heading on {url} ({notes}). Verify own-site self-description before promotion.",
            }
            intake_rows.append(new_row)
            existing_keys.add(key)
            existing_names.add(normalized)
            existing_lead_ids.add(lead_id)
            if firm_url not in existing_source_urls:
                source_rows.append({
                    "source_url": firm_url,
                    "source_name": f"{text} site (article-extracted)",
                    "source_type": "article_extraction",
                    "source_quality": "unknown",
                    "license_or_access": "public web",
                    "notes": f"Discovered by article-crawler on {today} from {url}. Verify before promotion.",
                    "last_checked": today,
                })
                existing_source_urls.add(firm_url)
            new_count += 1
            added_for_dir += 1
        print(f"  [{slug}] +{added_for_dir} new firm candidates")

    if new_count:
        write_csv_rows(INTAKE_PATH, intake_fields, intake_rows)
        write_csv_rows(SOURCE_PATH, source_fields, source_rows)
    print(f"Total new firm candidates: {new_count}")
    return 0


if __name__ == "__main__":
    sys.exit(crawl())
