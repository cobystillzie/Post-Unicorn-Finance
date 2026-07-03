"""Phase-1 liquidity re-audit harness.

Joins the 123-entity audit set with the 110 verified funds, classifies each
entity's liquidity horizon from STORED self-described text (zero new fetches by
default -> zero hallucination risk), and writes liquidity_horizons.csv plus a
markdown review report. Records proposed reclasses but MOVES NO ROWS.

Run:  python -m liquidity.reaudit            (stored text only)
      python -m liquidity.reaudit --enrich   (also scrape unknown/low-conf sites)
"""
from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from liquidity.bands import Band, classify
from liquidity.signals import extract_signal

ROOT = Path(__file__).resolve().parent.parent
AUDIT_CSV = ROOT / "data" / "evidence" / "atlas_asset_class_audit.csv"
VERIFIED_CSV = ROOT / "data" / "evidence" / "funds_verified.csv"
OUT_CSV = ROOT / "data" / "evidence" / "liquidity_horizons.csv"
REPORT_DIR = ROOT / "docs" / "research"

OUT_FIELDS = [
    "fund_id", "name", "liquidity_signal", "horizon_years", "exit_size_usd",
    "evidence_quote", "evidence_url", "source_tier", "confidence",
    "current_class", "proposed_band", "proposed_reclass", "needs_review", "audited_at",
]


def _read_csv(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def _num(x: float | None) -> str:
    return "" if x is None else f"{x:g}"


def run(enrich: bool = False) -> dict:
    audit = _read_csv(AUDIT_CSV)
    verified = {r["fund_id"]: r for r in _read_csv(VERIFIED_CSV)}
    today = date.today().isoformat()
    rows: list[dict] = []

    fetch = None
    if enrich:
        from liquidity.scraper import fetch_page_text
        fetch = fetch_page_text

    for a in audit:
        fid = a["fund_id"]
        v = verified.get(fid, {})
        url = (v.get("evidence_url") or a.get("evidence_url") or "").strip()
        text = " ".join(x for x in (v.get("self_id_quote", ""), v.get("notes", ""), a.get("flag", "")) if x)
        match = extract_signal(text)
        source_tier = "stated" if match.horizon_years is not None else "language"

        if enrich and match.signal.value == "unknown" and fetch and url:
            fr = fetch(url)
            if fr.ok and fr.text:
                m2 = extract_signal(fr.text)
                if m2.signal.value != "unknown":
                    match, source_tier = m2, ("stated" if m2.horizon_years is not None else "language")

        result = classify(
            signal=match.signal, horizon_years=match.horizon_years, exit_size_usd=match.exit_size_usd
        )
        current = a.get("asset_class", "")
        proposed = result.band.value
        moveable = proposed not in (Band.NEEDS_REVIEW.value, Band.UNKNOWN.value)
        reclass = f"{current}->{proposed}" if (moveable and proposed != current) else ""

        rows.append({
            "fund_id": fid, "name": a.get("name", ""),
            "liquidity_signal": match.signal.value,
            "horizon_years": _num(match.horizon_years),
            "exit_size_usd": _num(match.exit_size_usd),
            "evidence_quote": match.quote, "evidence_url": url,
            "source_tier": source_tier, "confidence": match.confidence,
            "current_class": current, "proposed_band": proposed,
            "proposed_reclass": reclass, "needs_review": str(result.needs_review),
            "audited_at": today,
        })

    with open(OUT_CSV, "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=OUT_FIELDS)
        w.writeheader()
        w.writerows(rows)

    report_path = _write_report(rows, today, enrich)
    return {"rows": len(rows), "csv": str(OUT_CSV), "report": str(report_path)}


def _tally(rows: list[dict], key: str) -> dict:
    out: dict[str, int] = {}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def _write_report(rows: list[dict], today: str, enrich: bool) -> Path:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORT_DIR / f"liquidity_reaudit_{today}.md"
    reclasses = [r for r in rows if r["proposed_reclass"]]
    review = [r for r in rows if r["needs_review"] == "True"]

    lines: list[str] = [
        f"# Liquidity re-audit — {today}", "",
        f"Source: stored self-described text{' + site enrichment' if enrich else ''} "
        "(no rows moved — proposed reclasses only).",
        f"Entities: {len(rows)}  ·  proposed reclasses: {len(reclasses)}  ·  needs_review: {len(review)}",
        "", "## Signal distribution",
    ]
    lines += [f"- {k}: {n}" for k, n in _tally(rows, "liquidity_signal").items()]
    lines += ["", "## Proposed band distribution"]
    lines += [f"- {k}: {n}" for k, n in _tally(rows, "proposed_band").items()]

    lines += ["", "## Proposed reclasses (NOT executed — pending Ethan cutoff sign-off)", "",
              "| fund_id | name | current | proposed | signal | yrs | $exit | evidence |",
              "|---|---|---|---|---|---|---|---|"]
    for r in reclasses:
        q = r["evidence_quote"].replace("|", "/")[:80]
        lines.append(f"| {r['fund_id']} | {r['name']} | {r['current_class']} | {r['proposed_band']} | "
                     f"{r['liquidity_signal']} | {r['horizon_years']} | {r['exit_size_usd']} | {q} |")

    lines += ["", "## Needs review (axis conflict / no evidence)", "",
              "| fund_id | name | current | signal | yrs | $exit | why/evidence |",
              "|---|---|---|---|---|---|---|"]
    for r in review:
        q = r["evidence_quote"].replace("|", "/")[:80]
        lines.append(f"| {r['fund_id']} | {r['name']} | {r['current_class']} | {r['liquidity_signal']} | "
                     f"{r['horizon_years']} | {r['exit_size_usd']} | {q} |")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description="Phase-1 liquidity re-audit (record, don't move).")
    ap.add_argument("--enrich", action="store_true", help="scrape sites for entities with no stored signal")
    args = ap.parse_args()
    summary = run(enrich=args.enrich)
    print(f"Wrote {summary['rows']} rows -> {summary['csv']}")
    print(f"Report -> {summary['report']}")


if __name__ == "__main__":
    main()
