import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import repo_hygiene  # noqa: E402


def test_parse_status_line_handles_modified_path():
    parsed = repo_hygiene.parse_status_line(" M data/evidence/entity_claims.csv")

    assert parsed["code"] == " M"
    assert parsed["path"] == "data/evidence/entity_claims.csv"


def test_parse_status_line_handles_rename_target():
    parsed = repo_hygiene.parse_status_line("R  old/path.csv -> data/evidence/new.csv")

    assert parsed["code"] == "R "
    assert parsed["path"] == "data/evidence/new.csv"


def test_categorize_dirty_paths():
    assert repo_hygiene.categorize_path("data/evidence/entity_claims.csv") == "evidence_csv_churn"
    assert repo_hygiene.categorize_path("data/evidence/notes.tmp") == "other_dirty"
    assert repo_hygiene.categorize_path("site/index.html") == "publish_site"
    assert repo_hygiene.categorize_path("scripts/research_agents.py") == "code"
    assert repo_hygiene.categorize_path("tests/test_repo_hygiene.py") == "tests"
    assert repo_hygiene.categorize_path("data/learning/review_queue.csv") == "local_runtime_or_learning"
    assert repo_hygiene.categorize_path("data/learning/") == "docs_or_repo_config"
    assert repo_hygiene.categorize_path(".env") == "blocked_secret_or_env"
    assert repo_hygiene.categorize_path("anything/cache.pyc", "!!") == "ignored_generated"


def test_summarize_flags_evidence_and_code_separately():
    rows = [
        {"code": " M", "path": "data/evidence/entity_claims.csv", "raw": " M data/evidence/entity_claims.csv", "category": "evidence_csv_churn"},
        {"code": " M", "path": "scripts/research_agents.py", "raw": " M scripts/research_agents.py", "category": "code"},
    ]

    summary = repo_hygiene.summarize(rows)

    assert summary["counts"] == {"code": 1, "evidence_csv_churn": 1}
    assert summary["has_evidence_churn"] is True
    assert summary["has_code_or_docs_churn"] is True


def test_blocked_rows_reject_unknown_and_prestaged_changes():
    rows = [
        {"code": " M", "path": "scripts/research_agents.py", "raw": " M scripts/research_agents.py", "category": "code"},
        {"code": "M ", "path": "docs/research/repo_hygiene.md", "raw": "M  docs/research/repo_hygiene.md", "category": "docs_or_repo_config"},
        {"code": "??", "path": "scratch.tmp", "raw": "?? scratch.tmp", "category": "other_dirty"},
    ]

    blocked = repo_hygiene.blocked_rows(rows)

    assert [row["path"] for row in blocked] == ["docs/research/repo_hygiene.md", "scratch.tmp"]


def test_commit_plan_groups_safe_paths():
    rows = [
        {"code": " M", "path": "data/evidence/entity_claims.csv", "raw": " M data/evidence/entity_claims.csv", "category": "evidence_csv_churn"},
        {"code": " M", "path": "site/index.html", "raw": " M site/index.html", "category": "publish_site"},
        {"code": " M", "path": "scripts/repo_hygiene.py", "raw": " M scripts/repo_hygiene.py", "category": "code"},
        {"code": "??", "path": "data/learning/", "raw": "?? data/learning/", "category": "docs_or_repo_config"},
    ]

    plan = repo_hygiene.commit_plan(rows)

    assert plan["evidence"] == ["data/evidence/entity_claims.csv"]
    assert plan["site"] == ["site/index.html"]
    assert plan["repo"] == ["scripts/repo_hygiene.py", "data/learning/.gitkeep"]


def test_group_allowed_staged_paths_rejects_cross_group_paths():
    assert repo_hygiene.group_allowed_staged_paths("evidence", ["data/evidence/entity_claims.csv"])
    assert not repo_hygiene.group_allowed_staged_paths("evidence", ["scripts/repo_hygiene.py"])


def test_autonomous_cleanup_dry_run_reports_plan_without_commits(tmp_path, monkeypatch):
    rows = [
        {"code": " M", "path": "data/evidence/entity_claims.csv", "raw": " M data/evidence/entity_claims.csv", "category": "evidence_csv_churn"},
        {"code": "??", "path": "scripts/repo_hygiene.py", "raw": "?? scripts/repo_hygiene.py", "category": "code"},
    ]

    monkeypatch.setattr(repo_hygiene, "fetch_and_fast_forward", lambda dry_run: ["dry-run: sync skipped"])
    monkeypatch.setattr(repo_hygiene, "git_status", lambda include_ignored=False: rows)
    monkeypatch.setattr(repo_hygiene, "branch_status", lambda: {"branch": "main", "upstream": "origin/main", "ahead": 0, "behind": 0})

    payload = repo_hygiene.autonomous_cleanup(
        output_dir=tmp_path,
        promotion_limit=10,
        push=True,
        dry_run=True,
    )

    assert payload["autonomous"]["status"] == "ok"
    assert payload["autonomous"]["push"] == "dry_run_skipped"
    assert payload["autonomous"]["commit_plan"]["evidence"] == ["data/evidence/entity_claims.csv"]
    assert payload["autonomous"]["commit_plan"]["repo"] == ["scripts/repo_hygiene.py"]
    assert payload["autonomous"]["commits"] == []


def test_autonomous_cleanup_blocks_unknown_dirty_files(tmp_path, monkeypatch):
    rows = [
        {"code": "??", "path": "scratch.tmp", "raw": "?? scratch.tmp", "category": "other_dirty"},
    ]

    monkeypatch.setattr(repo_hygiene, "fetch_and_fast_forward", lambda dry_run: ["dry-run: sync skipped"])
    monkeypatch.setattr(repo_hygiene, "git_status", lambda include_ignored=False: rows)
    monkeypatch.setattr(repo_hygiene, "branch_status", lambda: {"branch": "main", "upstream": "origin/main", "ahead": 0, "behind": 0})

    payload = repo_hygiene.autonomous_cleanup(
        output_dir=tmp_path,
        promotion_limit=10,
        push=False,
        dry_run=True,
    )

    assert payload["autonomous"]["status"] == "blocked"
    assert "blocked categories" in payload["autonomous"]["blocker"]
