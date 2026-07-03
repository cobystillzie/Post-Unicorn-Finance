"""Deterministic liquidity-signal extractor.

Reads a block of text (a firm's stored self_id_quote + notes, or scraped page
text) and returns the strongest liquidity Signal, the verbatim phrase + window
that triggered it (anti-hallucination: always a literal substring of the input),
and any explicitly-stated horizon (years) or exit size ($). No LLM in the loop.

Negation/contrast aware: firms frequently DEFINE themselves by rejecting a
timeline ("Unlike PE who flip in 3-5 years, we hold forever"). A FAST/SLOW/MEDIUM
phrase — or a stated number — sitting just after a negation/contrast cue is the
firm *rejecting* that horizon, not claiming it, so it is suppressed rather than
mislabeled. (Found via the 2026-06-09 validation run: Tiny/Silversmith/etc.)

The lexicon is v1 and deliberately tunable.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from liquidity.bands import Signal

# Precedence: NONE (no-exit) > BUILD (studio) > FAST > SLOW > MEDIUM.
# A no-exit claim is the strongest structural statement and must beat an
# incidental "don't chase unicorns" on the same page. Ambiguous "no-pressure"
# phrases ("no forced exit", "no exit mandate") were REMOVED from NONE — they are
# used by Nimble/patient funds too and were over-flipping rows to Permanent.
_LEXICON: list[tuple[Signal, tuple[str, ...]]] = [
    (Signal.NONE, (
        "no intention of selling", "never sold", "never sell", "won't sell", "will not sell",
        "do not sell", "not for sale", "permanent capital", "permanent equity", "permanently hold",
        "hold forever", "indefinite hold", "hold in perpetuity", "in perpetuity", "evergreen",
        "no exit", "no fund life", "buy and hold", "buy-and-hold", "steward owner", "steward-owner",
        "steward ownership", "not built to flip", "don't flip", "do not flip", "won't flip",
        "operate the businesses we own", "long-term owner", "long term owner",
    )),
    (Signal.BUILD, (
        "venture studio", "venture builder", "studio model", "we build companies", "build and own",
        "company builder", "we create companies", "company creation", "build from scratch",
        "builder of companies", "we incubate and own", "co-create companies", "start and own",
        "build, own, and operate", "we build, own",
    )),
    (Signal.FAST, (
        "quick liquidity", "fast liquidity", "rapid liquidity", "early liquidity", "quick exit",
        "fast exit", "quick return", "fast return", "short hold", "quick realization",
        "speed of liquidity", "don't chase unicorns", "do not chase unicorns", "rather than unicorns",
        "hunt camels", "camel", "3-5 year", "3–5 year", "3 to 5 year", "2-4 year", "sub-5",
        "under 5 year", "rapid scaling", "non-dilutive", "revenue-based", "revenue based",
    )),
    (Signal.SLOW, (
        "power law", "power-law", "unicorn outcomes", "10x fund", "venture-scale returns",
        "blitzscale", "blitzscaling", "fund-returner", "outlier returns", "moonshot", "decacorn",
        "7-10 year", "7–10 year", "long j-curve", "10-year horizon", "10 year horizon",
    )),
    (Signal.MEDIUM, (
        "sub-unicorn", "mid-market exit", "strategic acquisition", "growth equity", "majority recap",
        "control buyout", "liquidity for shareholders", "5-7 year", "5–7 year", "6-8 year",
        "lower middle market", "lower-middle-market", "mid-market", "minority growth",
    )),
]

_YEAR_RANGE = re.compile(r"(\d{1,2})\s*(?:-|–|to)\s*(\d{1,2})\s*[- ]?year", re.I)
_YEAR_SINGLE = re.compile(r"(\d{1,2})\s*[- ]?year", re.I)
_MONEY = re.compile(r"\$\s?(\d+(?:\.\d+)?)\s*(billion|bn|b|million|mm|m)\b", re.I)

# Cues that mean the firm is contrasting AGAINST the following timeline/outcome.
_NEGATION_CUES = (
    "unlike", "rather than", "instead of", "as opposed to", "not ", "n't", "never",
    "no ", "avoid", "reject", "versus", "vs ", "vs.", "away from", "don't", "do not",
    "private equity", "traditional pe", "traditional vc", "traditional private equity",
)

# Signals that describe a timeline/outcome the firm may be rejecting in contrast.
_NEGATABLE = (Signal.FAST, Signal.SLOW, Signal.MEDIUM)


@dataclass(frozen=True)
class SignalMatch:
    signal: Signal
    matched_phrase: str
    quote: str                       # literal window around the match (evidence)
    horizon_years: Optional[float]
    exit_size_usd: Optional[float]
    confidence: str                  # high | med | low


def _is_negated(text_low: str, idx: int, lookback: int = 50) -> bool:
    pre = text_low[max(0, idx - lookback):idx]
    return any(cue in pre for cue in _NEGATION_CUES)


def _window(text: str, idx: int, span: int = 70) -> str:
    start = max(0, idx - span)
    end = min(len(text), idx + span)
    return text[start:end].strip()


def _first_unnegated(pattern: "re.Pattern[str]", text_low: str):
    for m in pattern.finditer(text_low):
        if not _is_negated(text_low, m.start()):
            return m
    return None


def _find_phrase_unnegated(text_low: str, phrase: str, suppress_negated: bool) -> int:
    """Index of first phrase occurrence; if suppress_negated, skip negated ones."""
    start = 0
    while True:
        j = text_low.find(phrase, start)
        if j == -1:
            return -1
        if suppress_negated and _is_negated(text_low, j):
            start = j + 1
            continue
        return j


def _find_horizon(text_low: str) -> Optional[float]:
    m = _first_unnegated(_YEAR_RANGE, text_low)
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2.0
    m = _first_unnegated(_YEAR_SINGLE, text_low)
    if m:
        val = float(m.group(1))
        if 1 <= val <= 20:           # ignore stray numbers like a stray "2024 year"
            return val
    return None


# A $ figure counts as an EXIT size only when exit-language is nearby. Otherwise
# it is almost always AUM / fund size / ARR (validation 2026-06-09: Pemba "$2b
# funds" and Invictus "$10M+ ARR" were being mis-read as exit proceeds).
_EXIT_CONTEXT = ("exit", "acquir", "sold for", "sale of", "sells for", "bought for",
                 "acquisition", "liquidity event", "proceeds", "realiz", "realis",
                 "m&a", "takeover", "exit value", "exit at", "exit around", "exits around")


def _find_exit_usd(text_low: str) -> Optional[float]:
    for m in _MONEY.finditer(text_low):
        if _is_negated(text_low, m.start()):
            continue
        ctx = text_low[max(0, m.start() - 60):m.end() + 30]
        if any(w in ctx for w in _EXIT_CONTEXT):
            amount = float(m.group(1))
            unit = m.group(2).lower()
            mult = 1_000_000_000.0 if unit in ("billion", "bn", "b") else 1_000_000.0
            return amount * mult
    return None


_CONFIDENCE = {Signal.NONE: "high", Signal.BUILD: "high", Signal.FAST: "med",
               Signal.SLOW: "med", Signal.MEDIUM: "low"}


def extract_signal(text: str) -> SignalMatch:
    """Return the strongest non-negated liquidity signal found in ``text``."""
    if not text or not text.strip():
        return SignalMatch(Signal.UNKNOWN, "", "", None, None, "low")
    low = text.lower()
    horizon = _find_horizon(low)
    exit_usd = _find_exit_usd(low)

    for signal, phrases in _LEXICON:
        suppress = signal in _NEGATABLE
        for phrase in phrases:
            idx = _find_phrase_unnegated(low, phrase, suppress)
            if idx != -1:
                return SignalMatch(
                    signal=signal,
                    matched_phrase=phrase,
                    quote=_window(text, idx),
                    horizon_years=horizon,
                    exit_size_usd=exit_usd,
                    confidence=_CONFIDENCE.get(signal, "low"),
                )

    # No lexicon hit, but a non-negated stated horizon still classifies numerically.
    if horizon is not None:
        m = _first_unnegated(_YEAR_RANGE, low) or _first_unnegated(_YEAR_SINGLE, low)
        idx = m.start() if m else 0
        return SignalMatch(Signal.UNKNOWN, "stated-horizon", _window(text, idx), horizon, exit_usd, "low")

    return SignalMatch(Signal.UNKNOWN, "", "", None, exit_usd, "low")
