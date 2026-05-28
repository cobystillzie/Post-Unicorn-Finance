"""Phase 4e — Deep-mine article-title entities for firms they describe.

The user's insight: articles in the atlas (like 'Roll-Up Strategy 2026',
'AI Startup Investment Roundups 2026', 'What Is a Venture Studio?') aren't
firms themselves - they're SOURCES that name many firms inside. We should
extract those named firms and inject them as new candidate leads, then let
the verify pipeline classify each by their own page text.

Strategy:
 1. Pull the article-shaped entities' source URLs from the atlas.
 2. Re-fetch HTML for each (cached source_pages.raw_text is text-only, no anchors).
 3. Parse HTML for two signal types:
    a. External anchor tags with concise text (probably firm names with URLs).
    b. Prose-mention patterns like 'X is a Y firm' / 'include X, Y, Z'.
 4. Resolve anchor name -> URL mapping; for prose names with no URL, skip.
 5. Inject as needs_verification intake leads with discovered_from = article-mining.
"""
from __future__ import annotations

import csv
import hashlib
import re
import sys
import time
import random
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

USER_AGENT = "post-unicorn-finance-article-deepminer/0.1"

# Articles we know about plus their guessed inferred asset class (for default
# target_asset_class when the firm's own page hasn't been classified yet).
ARTICLES = [
    ("https://aifundingtracker.com", "SMV"),
    ("https://www.mrrstory.com/stories", "LMV"),
    ("https://ctacquisitions.com/roll-up-strategy-guide-2026", "Portfolio Capital"),
    ("https://entrepreneurloop.com/solo-founder-ai-tools", "LMV"),
    ("https://upstartzen.com/quiet-rise-profitable-indie-hackers", "LMV"),
    ("https://futuresight.ventures/what-is-a-venture-studio", "Portfolio Capital"),
    ("https://saasoperations.com/bootstrapped-saas-success-stories/", "LMV"),
    ("https://windsordrake.com/saas-valuation-multiples-2026", "SMV"),
]

EXCLUDE_DOMAINS = {
    "linkedin.com", "twitter.com", "x.com", "facebook.com", "instagram.com",
    "youtube.com", "youtu.be", "medium.com", "substack.com", "github.com",
    "crunchbase.com", "pitchbook.com", "wikipedia.org", "google.com",
    "duckduckgo.com", "bing.com", "apple.com", "play.google.com",
    "techcrunch.com", "forbes.com", "bloomberg.com", "reuters.com",
    "nytimes.com", "wsj.com", "ft.com", "businesswire.com", "prnewswire.com",
    "vimeo.com", "spotify.com", "soundcloud.com", "anchor.fm",
    "mailchimp.com", "hubspot.com", "typeform.com", "calendly.com",
    "stripe.com", "amazon.com", "amazonaws.com", "googleusercontent.com",
    "cloudflare.com", "fonts.googleapis.com", "discord.com", "slack.com",
    "stackoverflow.com", "techstars.com", "ycombinator.com",
    # The article hosts themselves
    "aifundingtracker.com", "mrrstory.com", "ctacquisitions.com",
    "entrepreneurloop.com", "upstartzen.com", "futuresight.ventures",
    "saasoperations.com", "windsordrake.com",
}

GENERIC_NOISE = {
    "home", "about", "contact", "blog", "news", "services", "menu", "more",
    "newsletter", "subscribe", "login", "signup", "search", "previous", "next",
    "click here", "read more", "see all", "view portfolio", "our portfolio",
    "our team", "our companies", "our story", "the team", "the platform",
    "privacy", "terms", "cookie", "advertise", "sponsor", "press",
    "instagram", "twitter", "linkedin", "facebook", "youtube", "tiktok",
    "site map", "sitemap", "rss",
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
        return urlparse(url).netloc.lower().lstrip("www.").split(":")[0]
    except ValueError:
        return ""


class AnchorAndProseParser(HTMLParser):
    """Captures anchor (href, text) pairs and accumulates plain-text body."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[tuple[str, str]] = []
        self._in_anchor = False
        self._anchor_href = ""
        self._anchor_text: list[str] = []
        self._body_text: list[str] = []
        self._skip_depth = 0
        self._skip_tags = {"script", "style", "noscript", "nav", "footer", "header"}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in self._skip_tags:
            self._skip_depth += 1
            return
        if tag == "a" and self._skip_depth == 0:
            href = dict(attrs).get("href") or ""
            self._in_anchor = True
            self._anchor_href = href
            self._anchor_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag in self._skip_tags and self._skip_depth > 0:
            self._skip_depth -= 1
            return
        if tag == "a" and self._in_anchor:
            text = " ".join("".join(self._anchor_text).split()).strip()
            if text and self._anchor_href:
                self.anchors.append((self._anchor_href, text))
            self._in_anchor = False
            self._anchor_href = ""
            self._anchor_text = []

    def handle_data(self, data: str) -> None:
        if self._skip_depth > 0:
            return
        if self._in_anchor:
            self._anchor_text.append(data)
        self._body_text.append(data)

    @property
    def body(self) -> str:
        return " ".join("".join(self._body_text).split())


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


def is_external_company_url(href: str, source_domain: str) -> tuple[bool, str]:
    """Returns (ok, normalized_homepage_url) for an anchor candidate."""
    if not href:
        return False, ""
    parsed = urlparse(href)
    if parsed.scheme not in ("http", "https"):
        return False, ""
    host = parsed.netloc.lower().lstrip("www.").split(":")[0]
    if not host or host == source_domain:
        return False, ""
    if any(host == b or host.endswith("." + b) for b in EXCLUDE_DOMAINS):
        return False, ""
    # Article and blog-like paths get excluded
    path = parsed.path.lower()
    if re.search(r"/(blog|news|article|press|post|podcast|episode|tag|category|author)/", path):
        return False, ""
    segments = [s for s in path.strip("/").split("/") if s]
    if len(segments) > 2:
        return False, ""
    return True, f"{parsed.scheme}://{parsed.netloc}/"


def clean_anchor_name(text: str) -> str:
    s = text.strip()
    if len(s) < 3 or len(s) > 60:
        return ""
    lower = s.lower()
    if lower in GENERIC_NOISE:
        return ""
    # Strip leading/trailing arrows etc.
    s = re.sub(r"^[^\w]+|[^\w)]+$", "", s).strip()
    if not s:
        return ""
    words = s.split()
    if not any(w[0].isupper() for w in words):
        return ""
    return s


def read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def write_csv_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def slug(url: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", url.lower()).strip("_")[:48] or "article"


def main() -> int:
    intake_fields, intake_rows = read_csv_rows(INTAKE_PATH)
    source_fields, source_rows = read_csv_rows(SOURCE_PATH)
    _, entity_rows = read_csv_rows(ENTITIES_PATH)

    existing_keys = {(normalize_name(r.get("name", "")), domain(r.get("website", "")))
                     for r in intake_rows + entity_rows}
    existing_names = {normalize_name(r.get("name", "")) for r in intake_rows + entity_rows}
    existing_source_urls = {r["source_url"] for r in source_rows}
    existing_lead_ids = {r.get("lead_id", "") for r in intake_rows}

    new_count = 0
    today = now_iso()[:10]

    for idx, (url, default_class) in enumerate(ARTICLES):
        article_slug = slug(url)
        print(f"\n[{article_slug}] fetching {url}", flush=True)
        if idx > 0:
            time.sleep(2 + random.uniform(0, 2))
        html, err = fetch_html(url)
        if err or not html:
            print(f"  skipped: {err}")
            continue
        parser = AnchorAndProseParser()
        try:
            parser.feed(html)
        except Exception as exc:  # noqa: BLE001
            print(f"  parse error: {exc}")
            continue

        article_domain = domain(url)
        article_added = 0
        # Anchor-based candidates
        for href, text in parser.anchors:
            absolute = urljoin(url, href)
            ok, homepage = is_external_company_url(absolute, article_domain)
            if not ok:
                continue
            name = clean_anchor_name(text)
            if not name:
                # Use host root as name fallback
                host = domain(absolute)
                name = host.split(".")[0].replace("-", " ").title() if host else ""
                if not name or len(name) < 3:
                    continue
            n = normalize_name(name)
            d = domain(homepage)
            if n in existing_names or (n, d) in existing_keys:
                continue
            lead_id = make_id("intake-article", article_slug, d)
            if lead_id in existing_lead_ids:
                continue
            intake_rows.append({
                "lead_id": lead_id, "name": name, "lead_type": "article_extraction_v2",
                "website": homepage, "source_urls": f"{homepage};{url}",
                "discovered_from": f"article_deepmine:{article_slug}",
                "target_asset_class": default_class,
                "target_entity_type": f"article-mentioned candidate (target {default_class})",
                "active_status": "unknown", "source_tier": "public_web", "priority": "medium",
                "evidence_status": "needs_verification", "review_status": "queued",
                "created_at": today,
                "notes": f"Extracted from anchor on {url} on {today}. Anchor text: '{text[:80]}'. Verify own-site self-description before promotion.",
            })
            existing_keys.add((n, d))
            existing_names.add(n)
            existing_lead_ids.add(lead_id)
            if homepage not in existing_source_urls:
                source_rows.append({
                    "source_url": homepage, "source_name": f"{name} site (article-mined)",
                    "source_type": "article_mention", "source_quality": "unknown",
                    "license_or_access": "public web",
                    "notes": f"Mined from {url} on {today}; requires verification.",
                    "last_checked": today,
                })
                existing_source_urls.add(homepage)
            new_count += 1
            article_added += 1
        print(f"  +{article_added} new firm candidates from anchors")

    if new_count:
        write_csv_rows(INTAKE_PATH, intake_fields, intake_rows)
        write_csv_rows(SOURCE_PATH, source_fields, source_rows)
    print(f"\nTotal new candidates: {new_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
