"""Liquidity-horizon classifier — pure, deterministic, config-driven.

Encodes the user's 2026-06-09 ruling (see the design spec). Qualitative signal
is primary; stated year/$ numbers refine it; axis conflicts return needs_review
rather than guessing. No I/O, no globals beyond the frozen default config.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Signal(str, Enum):
    """Qualitative liquidity signal — what language can reliably produce."""

    FAST = "fast"
    MEDIUM = "medium"
    SLOW = "slow"
    NONE = "none"                 # no exit by design
    BUILD = "build_from_within"   # studio: company creation is the activity
    UNKNOWN = "unknown"


class Band(str, Enum):
    NIMBLE = "Nimble"
    SMV = "SMV"
    UNICORN = "Unicorn"           # excluded baseline
    PERMANENT = "Permanent"
    STUDIO = "Studio"
    NEEDS_REVIEW = "needs_review"
    UNKNOWN = "Unknown"


@dataclass(frozen=True)
class BandConfig:
    """Cutoffs, in one place — expected to change once Ethan signs off."""

    nimble_max_years: float = 6.0                                   # < this -> Nimble
    smv_years: tuple[float, float] = (6.0, 9.0)                     # inclusive SMV speed band
    smv_exit_usd: tuple[float, float] = (50_000_000.0, 500_000_000.0)
    unicorn_min_years: float = 10.0                                 # >= this -> Unicorn (excluded)


DEFAULT_CONFIG = BandConfig()


@dataclass(frozen=True)
class ClassifyResult:
    band: Band
    needs_review: bool
    rationale: str


def _numeric_band(
    horizon: Optional[float], exit_usd: Optional[float], cfg: BandConfig
) -> tuple[Optional[Band], bool, str]:
    """Band implied by stated numbers, or (None, ...) when no horizon is stated."""
    if horizon is None:
        return None, False, ""
    if horizon >= cfg.unicorn_min_years:
        return Band.UNICORN, False, f"horizon {horizon}yr >= {cfg.unicorn_min_years} (unicorn baseline)"
    if horizon < cfg.nimble_max_years:
        return Band.NIMBLE, False, f"horizon {horizon}yr < {cfg.nimble_max_years} (fast)"
    lo, hi = cfg.smv_years
    if lo <= horizon <= hi:
        elo, ehi = cfg.smv_exit_usd
        if exit_usd is None:
            return Band.SMV, True, f"horizon {horizon}yr in SMV band but exit size unknown (size co-defines SMV)"
        if exit_usd < elo:
            if horizon == cfg.nimble_max_years:  # the crossing point -> tie-break on size
                return Band.NIMBLE, False, (
                    f"horizon {horizon}yr at crossing + exit ${exit_usd:,.0f} < ${elo:,.0f} -> Nimble (tie-breaker)"
                )
            return Band.NEEDS_REVIEW, True, (
                f"horizon {horizon}yr (medium speed) but exit ${exit_usd:,.0f} < ${elo:,.0f} (small) -> conflict"
            )
        if exit_usd > ehi:
            return Band.NEEDS_REVIEW, True, f"horizon {horizon}yr but exit ${exit_usd:,.0f} > ${ehi:,.0f} (too large)"
        return Band.SMV, False, f"horizon {horizon}yr + exit ${exit_usd:,.0f} in SMV range"
    return Band.NEEDS_REVIEW, True, f"horizon {horizon}yr falls in the {hi}-{cfg.unicorn_min_years} gap"


_SIGNAL_BAND = {
    Signal.FAST: Band.NIMBLE,
    Signal.MEDIUM: Band.SMV,
    Signal.SLOW: Band.UNICORN,
}


def classify(
    signal: Signal = Signal.UNKNOWN,
    horizon_years: Optional[float] = None,
    exit_size_usd: Optional[float] = None,
    config: BandConfig = DEFAULT_CONFIG,
) -> ClassifyResult:
    """Assign a liquidity band. Qualitative-primary, numeric-refined, conflict-safe."""
    cfg = config

    # Structural signals win outright (Permanent wins the tie, per taxonomy rule #2).
    if signal is Signal.NONE:
        contradicted = horizon_years is not None and horizon_years < cfg.unicorn_min_years
        note = "no-exit signal -> Permanent"
        if contradicted:
            note += f" (but a {horizon_years}yr horizon was also stated -> review)"
        return ClassifyResult(Band.PERMANENT, contradicted, note)
    if signal is Signal.BUILD:
        return ClassifyResult(Band.STUDIO, False, "build-from-within signal -> Studio")

    num_band, num_review, num_note = _numeric_band(horizon_years, exit_size_usd, cfg)
    sig_band = _SIGNAL_BAND.get(signal)  # None for UNKNOWN

    # medium signal alone can't confirm SMV (exit size co-defines it)
    if signal is Signal.MEDIUM and num_band is None:
        return ClassifyResult(Band.SMV, True, "medium signal -> SMV but no stated exit size to confirm $50-500M")

    if sig_band is not None and num_band is not None:
        if sig_band is num_band:
            return ClassifyResult(num_band, num_review, f"signal + numbers agree: {num_note}")
        if num_band is Band.NEEDS_REVIEW:
            return ClassifyResult(Band.NEEDS_REVIEW, True, num_note)
        return ClassifyResult(
            Band.NEEDS_REVIEW, True, f"conflict: signal '{signal.value}'->{sig_band.value} vs {num_note}"
        )

    if num_band is not None:
        return ClassifyResult(num_band, num_review, num_note)
    if sig_band is not None:
        return ClassifyResult(sig_band, False, f"signal '{signal.value}' -> {sig_band.value}")

    return ClassifyResult(Band.UNKNOWN, True, "no liquidity signal or stated horizon found")
