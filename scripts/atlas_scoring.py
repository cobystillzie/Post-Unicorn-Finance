"""Scoring helpers for the Post-Unicorn Finance atlas."""

from __future__ import annotations


STATUS_WEIGHT = {
    "verified_fact": 14,
    "candidate_evidence": 7,
    "inference": 1,
    "user_thesis": 0,
    "needs_verification": -8,
}

ACTIVE_WEIGHT = {
    "active": 8,
    "historical": 3,
    "inactive": 1,
    "unknown": -4,
}

SOURCE_TIER_WEIGHT = {
    "public_web": 7,
    "open_dataset": 3,
    "paid_optional": 0,
}

ROLE_WEIGHT = {
    "SMV capital provider": 12,
    "software acquirer": 12,
    "capital provider": 10,
    "capital platform": 9,
    "SaaS acquirer": 10,
    "patient capital investor": 10,
    "search fund investor": 10,
    "acquisition marketplace": 9,
    "startup studio": 8,
    "venture studio": 8,
    "sovereign wealth investor": 7,
    "public innovation fund": 7,
    "public capital institution": 7,
}


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def entity_score(row: dict[str, str]) -> int:
    """Return the atlas priority score for one industry entity row.

    This is a verification-priority score, not an investment score.
    """
    score = parse_int(row.get("fit_score", "0"))
    score += STATUS_WEIGHT.get(row.get("evidence_status", ""), 0)
    score += ACTIVE_WEIGHT.get(row.get("active_status", ""), 0)
    score += SOURCE_TIER_WEIGHT.get(row.get("source_tier", ""), 0)

    role = row.get("ecosystem_role", "")
    score += ROLE_WEIGHT.get(role, 0)
    if "non-unicorn" in row.get("non_unicorn_thesis", "").lower():
        score += 4
    if "Atlas seed row" in row.get("notes", ""):
        score -= 2
    return score


def default_claim_confidence(evidence_status: str) -> int:
    """Map evidence status to a conservative default claim confidence."""
    return {
        "verified_fact": 90,
        "candidate_evidence": 65,
        "inference": 45,
        "user_thesis": 0,
        "needs_verification": 25,
    }.get(evidence_status, 25)
