"""Table-driven tests for the liquidity-horizon classifier (the band spine).

Encodes the user's 2026-06-09 ruling exactly:
  - Nimble  < 6yr
  - SMV     6-9yr AND $50M-500M exit
  - Unicorn >= 10yr (excluded baseline)
  - Permanent = no exit ; Studio = exit N/A (build from within)
  - Tie-breaker: at the ~6yr crossing point, a sub-$50M exit -> Nimble.
  - Axis conflict -> needs_review (never a silent guess).
"""
from __future__ import annotations

from liquidity.bands import Band, BandConfig, Signal, classify


# ---- qualitative signal only (no numbers) -------------------------------

def test_signal_none_is_permanent() -> None:
    assert classify(signal=Signal.NONE).band is Band.PERMANENT


def test_signal_build_is_studio() -> None:
    assert classify(signal=Signal.BUILD).band is Band.STUDIO


def test_signal_fast_is_nimble() -> None:
    assert classify(signal=Signal.FAST).band is Band.NIMBLE


def test_signal_medium_is_smv_but_needs_review_without_size() -> None:
    result = classify(signal=Signal.MEDIUM)
    assert result.band is Band.SMV
    assert result.needs_review is True


def test_signal_slow_is_unicorn() -> None:
    assert classify(signal=Signal.SLOW).band is Band.UNICORN


def test_signal_unknown_is_unknown_and_review() -> None:
    result = classify(signal=Signal.UNKNOWN)
    assert result.band is Band.UNKNOWN
    assert result.needs_review is True


# ---- numeric horizon drives when signal is unknown ----------------------

def test_horizon_4yr_is_nimble() -> None:
    assert classify(signal=Signal.UNKNOWN, horizon_years=4).band is Band.NIMBLE


def test_horizon_12yr_is_unicorn() -> None:
    assert classify(signal=Signal.UNKNOWN, horizon_years=12).band is Band.UNICORN


def test_horizon_7yr_with_venture_exit_is_smv() -> None:
    result = classify(signal=Signal.UNKNOWN, horizon_years=7, exit_size_usd=100_000_000)
    assert result.band is Band.SMV
    assert result.needs_review is False


def test_horizon_9to10_gap_is_needs_review() -> None:
    assert classify(signal=Signal.UNKNOWN, horizon_years=9.5).needs_review is True


# ---- the tie-breaker (user's exact example) -----------------------------

def test_6yr_under_50m_is_nimble_tiebreaker() -> None:
    result = classify(signal=Signal.UNKNOWN, horizon_years=6, exit_size_usd=20_000_000)
    assert result.band is Band.NIMBLE


def test_6yr_venture_exit_is_smv() -> None:
    assert classify(signal=Signal.UNKNOWN, horizon_years=6, exit_size_usd=120_000_000).band is Band.SMV


def test_7yr_under_50m_is_conflict_needs_review() -> None:
    assert classify(signal=Signal.UNKNOWN, horizon_years=7, exit_size_usd=20_000_000).needs_review is True


def test_6to9_exit_over_500m_is_needs_review() -> None:
    assert classify(signal=Signal.UNKNOWN, horizon_years=7, exit_size_usd=900_000_000).needs_review is True


# ---- signal vs numeric agreement / conflict -----------------------------

def test_fast_signal_agrees_with_short_horizon() -> None:
    result = classify(signal=Signal.FAST, horizon_years=4)
    assert result.band is Band.NIMBLE
    assert result.needs_review is False


def test_fast_signal_conflicts_with_medium_horizon() -> None:
    assert classify(signal=Signal.FAST, horizon_years=8).needs_review is True


def test_no_exit_signal_with_contradictory_horizon_flags_review() -> None:
    result = classify(signal=Signal.NONE, horizon_years=3)
    assert result.band is Band.PERMANENT
    assert result.needs_review is True


# ---- config override + explainability -----------------------------------

def test_config_threshold_override() -> None:
    cfg = BandConfig(unicorn_min_years=8)
    assert classify(signal=Signal.UNKNOWN, horizon_years=8, config=cfg).band is Band.UNICORN


def test_result_carries_rationale() -> None:
    result = classify(signal=Signal.FAST)
    assert isinstance(result.rationale, str) and result.rationale
