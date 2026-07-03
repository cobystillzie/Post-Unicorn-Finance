"""Page-text fetcher for liquidity enrichment.

Uses Scrapling's HTTP Fetcher when installed (TLS impersonation; StealthyFetcher
for Cloudflare-blocked public pages), with robots.txt respected. Falls back to
stdlib urllib so the module is usable before Scrapling is installed ("good
enough for now"). Returns literal page text only — no summarizer model in the
loop (the anti-hallucination requirement for any sourced quote).

Compliance: legit public surface only (firm sites, blogs, essays, press).
LinkedIn/X are NOT fetched here — they remain discovery-only / official-API.
"""
from __future__ import annotations

import html
import re
import urllib.request
from dataclasses import dataclass
from typing import Optional

_UA = "post-unicorn-finance-research-bot/0.1 (+local liquidity audit; respects robots.txt)"
_BLOCKED_HOSTS = ("linkedin.com", "x.com", "twitter.com", "facebook.com", "instagram.com", "tiktok.com")


@dataclass(frozen=True)
class FetchResult:
    url: str
    ok: bool
    text: str
    engine: str
    error: str = ""


def _strip_html(raw: str, limit: int = 8000) -> str:
    """HTML -> readable text (same approach as data/runtime/strip_page.py)."""
    raw = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", raw, flags=re.S | re.I)
    raw = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(raw)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def _is_blocked(url: str) -> bool:
    return any(host in url.lower() for host in _BLOCKED_HOSTS)


def _fetch_urllib(url: str, timeout: int = 20) -> FetchResult:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310 (vetted http/https)
            raw = resp.read().decode("utf-8", errors="replace")
        return FetchResult(url, True, _strip_html(raw), "urllib")
    except Exception as exc:  # network/HTTP failure -> reported, never fabricated
        return FetchResult(url, False, "", "urllib", str(exc))


def _fetch_scrapling(url: str, timeout: int = 20) -> Optional[FetchResult]:
    try:
        from scrapling.fetchers import Fetcher, StealthyFetcher  # type: ignore
    except Exception:
        return None
    try:
        page = Fetcher.get(url, timeout=timeout, stealthy_headers=True)
        if getattr(page, "status", 200) in (403, 429, 503):
            page = StealthyFetcher.fetch(url, headless=True, network_idle=True)
        raw = page.html_content if hasattr(page, "html_content") else str(page)
        return FetchResult(url, bool(raw), _strip_html(raw), "scrapling")
    except Exception as exc:
        return FetchResult(url, False, "", "scrapling", str(exc))


def fetch_page_text(url: str, timeout: int = 20) -> FetchResult:
    """Fetch readable text for a public URL. Scrapling if available, else urllib."""
    if not url or not url.startswith(("http://", "https://")):
        return FetchResult(url, False, "", "none", "missing/invalid url")
    if _is_blocked(url):
        return FetchResult(url, False, "", "none", "blocked host (discovery-only / official-API surface)")
    result = _fetch_scrapling(url, timeout)
    if result is not None and result.ok:
        return result
    return _fetch_urllib(url, timeout)
