"""Learning operations for the Post-Unicorn Finance atlas.

This module turns human review decisions into a supervised-learning corpus.
It deliberately does not call any external fine-tuning API. A fine-tune is only
prepared when the reviewed corpus is large enough to evaluate safely.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

from atlas_sqlite import DEFAULT_DB, exec_script, import_csvs, now_iso, open_db
from automation_safety import AutomationLock


ROOT = Path(__file__).resolve().parents[1]
LEARNING_DIR = ROOT / "data" / "learning"
MIN_FINE_TUNE_EXAMPLES = 1000
MIN_EVAL_EXAMPLES = 100
REVIEW_QUEUE_LIMIT = 250

ALLOWED_REVIEW_LABELS = [
    "accepted",
    "rejected",
    "needs_more_source",
    "wrong_bucket",
    "duplicate",
    "too_broad",
    "paper_ready",
]


def ensure_db(db_path: Path) -> None:
    if not db_path.exists():
        import_csvs(db_path)
        return
    with open_db(db_path) as conn:
        exec_script(conn)
        conn.commit()


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if rows:
        fieldnames = list(rows[0].keys())
    else:
        fieldnames = [
            "target_id",
            "target_type",
            "entity_name",
            "primary_asset_class",
            "evidence_status",
            "paper_ready",
            "source_url",
            "review_priority",
            "review_reason",
            "claim",
            "source_text_snippet",
            "allowed_labels",
        ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def stable_split(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return "eval" if int(digest[:2], 16) < 51 else "train"


def claim_priority(row: sqlite3.Row) -> tuple[int, str]:
    score = 0
    reasons: list[str] = []
    if row["paper_ready"] == 0:
        score += 10
        reasons.append("not paper-ready")
    if row["evidence_status"] == "verified_fact":
        score += 35
        reasons.append("verified_fact needs review")
    if row["evidence_status"] == "candidate_evidence":
        score += 20
        reasons.append("candidate evidence needs accept/reject label")
    if row["source_quality"] in {"unknown", "social"}:
        score += 15
        reasons.append("low source-quality label")
    if row["primary_asset_class"] in {"SMV", "LMV"}:
        score += 10
        reasons.append("priority asset bucket")
    if "intake_" in row["claim_type"]:
        score += 10
        reasons.append("auto-promoted intake claim")
    if not row["source_text_snippet"]:
        score += 8
        reasons.append("missing source snippet")
    return score, "; ".join(reasons)


def build_review_queue(db_path: Path, output_dir: Path = LEARNING_DIR, limit: int = REVIEW_QUEUE_LIMIT) -> list[dict[str, object]]:
    ensure_db(db_path)
    with open_db(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
                c.claim_id,
                c.entity_name,
                c.claim_type,
                c.claim,
                c.source_url,
                c.source_quality,
                c.source_tier,
                c.evidence_status,
                c.paper_ready,
                c.source_text_snippet,
                e.primary_asset_class,
                COALESCE(r.review_status, '') AS review_status
            FROM entity_claims c
            LEFT JOIN industry_entities e ON e.entity_id = c.entity_id
            LEFT JOIN claim_reviews r ON r.claim_id = c.claim_id
            WHERE c.paper_ready = 0
              AND COALESCE(r.review_status, '') NOT IN ('accepted', 'rejected', 'paper_ready')
            """
        ).fetchall()

    scored: list[dict[str, object]] = []
    for row in rows:
        priority, reason = claim_priority(row)
        scored.append(
            {
                "target_id": row["claim_id"],
                "target_type": "claim",
                "entity_name": row["entity_name"],
                "primary_asset_class": row["primary_asset_class"] or "",
                "evidence_status": row["evidence_status"],
                "paper_ready": row["paper_ready"],
                "source_url": row["source_url"],
                "review_priority": priority,
                "review_reason": reason,
                "claim": row["claim"],
                "source_text_snippet": row["source_text_snippet"],
                "allowed_labels": ";".join(ALLOWED_REVIEW_LABELS),
            }
        )
    scored.sort(key=lambda item: (-int(item["review_priority"]), str(item["entity_name"]), str(item["target_id"])))
    queued = scored[:limit]
    write_csv(output_dir / "review_queue.csv", queued)
    return queued


def reviewed_claim_examples(db_path: Path) -> list[dict]:
    ensure_db(db_path)
    with open_db(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT
                r.review_id,
                r.claim_id,
                r.review_status,
                r.reviewer,
                r.direct_evidence,
                r.rationale,
                r.created_at,
                r.paper_ready,
                c.entity_name,
                c.claim_type,
                c.claim,
                c.source_url,
                c.source_quality,
                c.source_tier,
                c.evidence_status,
                c.source_text_snippet,
                e.primary_asset_class,
                e.entity_type
            FROM claim_reviews r
            JOIN entity_claims c ON c.claim_id = r.claim_id
            LEFT JOIN industry_entities e ON e.entity_id = c.entity_id
            ORDER BY r.created_at
            """
        ).fetchall()

    examples: list[dict] = []
    for row in rows:
        split = stable_split(row["review_id"])
        examples.append(
            {
                "example_id": row["review_id"],
                "task": "claim_review",
                "split": split,
                "input": {
                    "entity_name": row["entity_name"],
                    "primary_asset_class": row["primary_asset_class"] or "",
                    "entity_type": row["entity_type"] or "",
                    "claim_type": row["claim_type"],
                    "claim": row["claim"],
                    "source_url": row["source_url"],
                    "source_quality": row["source_quality"],
                    "source_tier": row["source_tier"],
                    "evidence_status": row["evidence_status"],
                    "source_text_snippet": row["source_text_snippet"],
                    "direct_evidence": row["direct_evidence"],
                },
                "expected_output": {
                    "label": row["review_status"],
                    "paper_ready": bool(row["paper_ready"]),
                    "rationale": row["rationale"],
                },
                "label_source": {
                    "reviewer": row["reviewer"],
                    "created_at": row["created_at"],
                },
            }
        )
    return examples


def export_training_examples(db_path: Path, output_dir: Path = LEARNING_DIR) -> dict[str, int]:
    examples = reviewed_claim_examples(db_path)
    train = [example for example in examples if example["split"] == "train"]
    eval_rows = [example for example in examples if example["split"] == "eval"]
    write_jsonl(output_dir / "training" / "claim_review_all.jsonl", examples)
    write_jsonl(output_dir / "training" / "claim_review_train.jsonl", train)
    write_jsonl(output_dir / "training" / "claim_review_eval.jsonl", eval_rows)
    return {"all": len(examples), "train": len(train), "eval": len(eval_rows)}


def baseline_prediction(example: dict) -> str:
    input_row = example["input"]
    if input_row["evidence_status"] == "verified_fact" and (input_row["source_text_snippet"] or input_row["direct_evidence"]):
        return "accepted"
    if input_row["source_quality"] in {"unknown", "social"}:
        return "needs_more_source"
    if not input_row["source_text_snippet"] and not input_row["direct_evidence"]:
        return "needs_more_source"
    return "accepted"


def evaluate_baseline(db_path: Path, output_dir: Path = LEARNING_DIR) -> dict[str, object]:
    examples = reviewed_claim_examples(db_path)
    if not examples:
        metrics: dict[str, object] = {
            "status": "blocked_no_labels",
            "evaluated_examples": 0,
            "accuracy": None,
            "notes": "No human-reviewed claim labels exist yet.",
        }
    else:
        correct = 0
        by_label: dict[str, dict[str, int]] = {}
        for example in examples:
            expected = example["expected_output"]["label"]
            predicted = baseline_prediction(example)
            correct += int(expected == predicted)
            by_label.setdefault(expected, {"total": 0, "correct": 0})
            by_label[expected]["total"] += 1
            by_label[expected]["correct"] += int(expected == predicted)
        metrics = {
            "status": "ok",
            "evaluated_examples": len(examples),
            "accuracy": correct / len(examples),
            "by_label": by_label,
            "notes": "Baseline is a deterministic rule set, not a trained model.",
        }
    (output_dir / "metrics").mkdir(parents=True, exist_ok=True)
    (output_dir / "metrics" / "baseline_claim_review.json").write_text(
        json.dumps(metrics, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return metrics


def fine_tune_readiness(
    db_path: Path,
    output_dir: Path = LEARNING_DIR,
    min_examples: int = MIN_FINE_TUNE_EXAMPLES,
    min_eval_examples: int = MIN_EVAL_EXAMPLES,
) -> dict[str, object]:
    counts = export_training_examples(db_path, output_dir)
    ready = counts["all"] >= min_examples and counts["eval"] >= min_eval_examples
    manifest = {
        "status": "ready" if ready else "blocked",
        "created_at": now_iso(),
        "task": "claim_review",
        "counts": counts,
        "requirements": {
            "min_examples": min_examples,
            "min_eval_examples": min_eval_examples,
        },
        "training_file": str(output_dir / "training" / "claim_review_train.jsonl"),
        "eval_file": str(output_dir / "training" / "claim_review_eval.jsonl"),
        "notes": "No external fine-tune job is launched by this command.",
    }
    (output_dir / "fine_tune_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def learning_status(db_path: Path, output_dir: Path = LEARNING_DIR) -> dict[str, object]:
    ensure_db(db_path)
    with open_db(db_path) as conn:
        conn.row_factory = sqlite3.Row
        counts = {
            "review_feedback": conn.execute("SELECT COUNT(*) FROM review_feedback").fetchone()[0],
            "claim_reviews": conn.execute("SELECT COUNT(*) FROM claim_reviews").fetchone()[0],
            "paper_ready_claims": conn.execute("SELECT COUNT(*) FROM entity_claims WHERE paper_ready = 1").fetchone()[0],
            "unreviewed_verified_claims": conn.execute(
                "SELECT COUNT(*) FROM entity_claims WHERE evidence_status = 'verified_fact' AND paper_ready = 0"
            ).fetchone()[0],
            "candidate_claims": conn.execute(
                "SELECT COUNT(*) FROM entity_claims WHERE evidence_status = 'candidate_evidence'"
            ).fetchone()[0],
            "queued_intakes": conn.execute(
                "SELECT COUNT(*) FROM entity_intake_queue WHERE review_status IN ('queued', 'needs_more_source')"
            ).fetchone()[0],
        }
    training_counts = export_training_examples(db_path, output_dir)
    readiness = fine_tune_readiness(db_path, output_dir)
    baseline = evaluate_baseline(db_path, output_dir)
    status = {
        "generated_at": now_iso(),
        "counts": counts,
        "training_counts": training_counts,
        "fine_tune": readiness,
        "baseline": baseline,
    }
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "learning_status.json").write_text(json.dumps(status, indent=2, sort_keys=True), encoding="utf-8")
    lines = [
        "# Learning Status",
        "",
        f"Generated: {status['generated_at']}",
        "",
        "## Label Counts",
        f"- Review feedback rows: {counts['review_feedback']}",
        f"- Claim review rows: {counts['claim_reviews']}",
        f"- Paper-ready claims: {counts['paper_ready_claims']}",
        f"- Unreviewed verified claims: {counts['unreviewed_verified_claims']}",
        f"- Candidate claims: {counts['candidate_claims']}",
        f"- Queued/needs-source intakes: {counts['queued_intakes']}",
        "",
        "## Training Corpus",
        f"- All examples: {training_counts['all']}",
        f"- Train examples: {training_counts['train']}",
        f"- Eval examples: {training_counts['eval']}",
        "",
        "## Fine-Tune Gate",
        f"- Status: {readiness['status']}",
        f"- Required examples: {readiness['requirements']['min_examples']}",
        f"- Required eval examples: {readiness['requirements']['min_eval_examples']}",
        "",
        "## Baseline Evaluation",
        f"- Status: {baseline['status']}",
        f"- Evaluated examples: {baseline['evaluated_examples']}",
        f"- Accuracy: {baseline['accuracy']}",
        "",
        "## Next Action",
    ]
    if readiness["status"] == "blocked":
        lines.append("- Review and label claims from `data/learning/review_queue.csv`; do not fine-tune yet.")
    else:
        lines.append("- Corpus threshold is met. Run provider-specific fine-tune setup after reviewing the manifest.")
    (output_dir / "learning_status.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return status


def learning_loop(db_path: Path, output_dir: Path = LEARNING_DIR, review_limit: int = REVIEW_QUEUE_LIMIT) -> int:
    with AutomationLock("learning-loop"):
        review_rows = build_review_queue(db_path, output_dir, limit=review_limit)
        status = learning_status(db_path, output_dir)
    print(f"Learning loop wrote {len(review_rows)} review queue rows")
    print(f"Reviewed examples: {status['training_counts']['all']}")
    print(f"Fine-tune status: {status['fine_tune']['status']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", default=str(DEFAULT_DB))
    parser.add_argument("--output-dir", default=str(LEARNING_DIR))
    sub = parser.add_subparsers(dest="command", required=True)

    queue = sub.add_parser("build-review-queue")
    queue.add_argument("--limit", type=int, default=REVIEW_QUEUE_LIMIT)

    sub.add_parser("export-training")
    sub.add_parser("evaluate-baseline")

    fine_tune = sub.add_parser("prepare-fine-tune")
    fine_tune.add_argument("--min-examples", type=int, default=MIN_FINE_TUNE_EXAMPLES)
    fine_tune.add_argument("--min-eval-examples", type=int, default=MIN_EVAL_EXAMPLES)

    loop = sub.add_parser("learning-loop")
    loop.add_argument("--review-limit", type=int, default=REVIEW_QUEUE_LIMIT)

    sub.add_parser("status")

    args = parser.parse_args()
    db_path = Path(args.db)
    output_dir = Path(args.output_dir)

    if args.command == "build-review-queue":
        rows = build_review_queue(db_path, output_dir, limit=args.limit)
        print(f"Wrote {len(rows)} rows to {output_dir / 'review_queue.csv'}")
        return 0
    if args.command == "export-training":
        counts = export_training_examples(db_path, output_dir)
        print(json.dumps(counts, sort_keys=True))
        return 0
    if args.command == "evaluate-baseline":
        metrics = evaluate_baseline(db_path, output_dir)
        print(json.dumps(metrics, sort_keys=True))
        return 0
    if args.command == "prepare-fine-tune":
        manifest = fine_tune_readiness(db_path, output_dir, args.min_examples, args.min_eval_examples)
        print(json.dumps(manifest, sort_keys=True))
        return 0 if manifest["status"] == "ready" else 2
    if args.command == "learning-loop":
        return learning_loop(db_path, output_dir, review_limit=args.review_limit)
    if args.command == "status":
        status = learning_status(db_path, output_dir)
        print(json.dumps(status, sort_keys=True))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
