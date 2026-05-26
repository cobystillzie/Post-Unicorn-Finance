import json
import sqlite3
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import learning_ops  # noqa: E402
import research_agents  # noqa: E402
from atlas_sqlite import import_csvs  # noqa: E402


def first_claim_id(db_path: Path) -> str:
    conn = sqlite3.connect(db_path)
    claim_id = conn.execute("SELECT claim_id FROM entity_claims ORDER BY claim_id LIMIT 1").fetchone()[0]
    conn.close()
    return claim_id


def test_build_review_queue_writes_claim_rows(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    output_dir = tmp_path / "learning"
    import_csvs(db_path)

    rows = learning_ops.build_review_queue(db_path, output_dir, limit=5)

    assert len(rows) == 5
    assert rows[0]["target_type"] == "claim"
    assert rows[0]["target_id"]
    assert "accepted" in rows[0]["allowed_labels"]
    assert (output_dir / "review_queue.csv").exists()


def test_fine_tune_readiness_blocks_without_review_labels(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    output_dir = tmp_path / "learning"
    import_csvs(db_path)

    manifest = learning_ops.fine_tune_readiness(db_path, output_dir, min_examples=1, min_eval_examples=1)

    assert manifest["status"] == "blocked"
    assert manifest["counts"] == {"all": 0, "train": 0, "eval": 0}
    assert (output_dir / "fine_tune_manifest.json").exists()


def test_feedback_label_exports_training_example(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    output_dir = tmp_path / "learning"
    import_csvs(db_path)
    claim_id = first_claim_id(db_path)

    result = research_agents.add_feedback(
        db_path,
        target_type="claim",
        target_id=claim_id,
        label="accepted",
        rationale="Test review accepts the source-backed claim.",
        reviewer="pytest",
        direct_evidence="The source text directly supports the claim.",
    )
    counts = learning_ops.export_training_examples(db_path, output_dir)

    assert result == 0
    assert counts["all"] == 1
    rows = [
        json.loads(line)
        for line in (output_dir / "training" / "claim_review_all.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert rows[0]["task"] == "claim_review"
    assert rows[0]["expected_output"]["label"] == "accepted"
    assert rows[0]["input"]["direct_evidence"] == "The source text directly supports the claim."


def test_baseline_evaluation_uses_reviewed_labels(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    output_dir = tmp_path / "learning"
    import_csvs(db_path)
    claim_id = first_claim_id(db_path)
    research_agents.add_feedback(
        db_path,
        target_type="claim",
        target_id=claim_id,
        label="needs_more_source",
        rationale="Test review asks for more source support.",
        reviewer="pytest",
        direct_evidence="",
    )

    metrics = learning_ops.evaluate_baseline(db_path, output_dir)

    assert metrics["status"] == "ok"
    assert metrics["evaluated_examples"] == 1
    assert "accuracy" in metrics
    assert (output_dir / "metrics" / "baseline_claim_review.json").exists()

