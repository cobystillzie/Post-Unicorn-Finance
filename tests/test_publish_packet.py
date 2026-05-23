import argparse
import csv
import json
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import export_shareable_atlas  # noqa: E402
import export_research_dossier  # noqa: E402
import publish_atlas_packet  # noqa: E402
from atlas_sqlite import import_csvs  # noqa: E402
from automation_safety import (  # noqa: E402
    AutomationLock,
    AutomationLockError,
    PacketValidationError,
    check_packet_sizes,
    split_git_status_by_prefix,
    write_json_and_markdown_status,
)


def test_shared_lock_blocks_active_holder(tmp_path):
    lock_path = tmp_path / "atlas.lock"
    with AutomationLock("first", lock_path=lock_path):
        with pytest.raises(AutomationLockError):
            with AutomationLock("second", lock_path=lock_path):
                pass


def test_shared_lock_replaces_stale_pid(tmp_path):
    lock_path = tmp_path / "atlas.lock"
    lock_path.write_text(
        json.dumps(
            {
                "owner": "stale",
                "pid": -1,
                "started_at": "2026-05-20T00:00:00+00:00",
            }
        ),
        encoding="utf-8",
    )

    with AutomationLock("fresh", lock_path=lock_path):
        payload = json.loads(lock_path.read_text(encoding="utf-8"))
        assert payload["owner"] == "fresh"


def test_dirty_worktree_classifier_allows_only_site_paths():
    allowed, blocked = split_git_status_by_prefix(
        [
            " M site/index.html",
            "?? site/publish_status.json",
            " M scripts/research_agents.py",
            "?? data/atlas.sqlite",
        ],
        ["site"],
    )

    assert allowed == [" M site/index.html", "?? site/publish_status.json"]
    assert blocked == [" M scripts/research_agents.py", "?? data/atlas.sqlite"]


def test_status_json_and_markdown_are_written(tmp_path):
    status = {
        "status": "published",
        "publish_id": "atlas-test",
        "generated_at": "2026-05-23T00:00:00+00:00",
        "source_head_sha": "abc123",
        "live_url": "https://example.test/",
        "entity_count": 2,
        "claim_count": 3,
        "paper_ready_count": 0,
    }
    json_path = tmp_path / "publish_status.json"
    markdown_path = tmp_path / "publish_status.md"

    write_json_and_markdown_status(json_path, markdown_path, status)

    assert json.loads(json_path.read_text(encoding="utf-8"))["publish_id"] == "atlas-test"
    assert "Status: published" in markdown_path.read_text(encoding="utf-8")


def test_packet_size_thresholds(tmp_path):
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("x" * 32, encoding="utf-8")
    (site / "post_unicorn_industry_atlas_entities_claims.csv").write_text("claim_id\n", encoding="utf-8")

    warnings = check_packet_sizes(site, warn_html_bytes=16, max_html_bytes=64)
    assert warnings
    with pytest.raises(PacketValidationError):
        check_packet_sizes(site, warn_html_bytes=16, max_html_bytes=24)


def test_packet_parity_validation_against_sqlite(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    site = tmp_path / "site"
    import_csvs(db_path)
    html_path, csv_path, _cover = export_shareable_atlas.build_report(db_path, site)
    publish_atlas_packet.inject_publish_metadata(html_path, "atlas-test", "2026-05-23T00:00:00+00:00")
    shutil.copyfile(html_path, site / "index.html")
    export_research_dossier.build_dossier_html(export_research_dossier.DEFAULT_DOSSIER, site, db_path)
    (site / ".nojekyll").write_text("", encoding="utf-8")
    publish_atlas_packet.write_publish_status(
        site,
        {
            "status": "prepared_for_publish",
            "publish_id": "atlas-test",
            "generated_at": "2026-05-23T00:00:00+00:00",
            "source_head_sha": "abc123",
            "live_url": "https://example.test/",
            "entity_count": 0,
            "claim_count": 0,
            "paper_ready_count": 0,
        },
    )

    assert publish_atlas_packet.validate_packet_contents(site, db_path) == []
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    conn = sqlite3.connect(db_path)
    claim_count = conn.execute("SELECT COUNT(*) FROM entity_claims").fetchone()[0]
    conn.close()
    assert len(rows) == claim_count


def test_research_dossier_exports_with_live_counts(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)

    html_path = export_research_dossier.build_dossier_html(export_research_dossier.DEFAULT_DOSSIER, tmp_path / "site", db_path)
    html = html_path.read_text(encoding="utf-8")

    assert "Post-Unicorn Finance Research Dossier" in html
    assert "Industry-establishment dossier" in html
    assert "Industry Atlas" in html
    assert "Paper-ready claims" in html


def test_publish_returns_failure_before_generation_when_validation_fails(tmp_path, monkeypatch):
    generated = {"called": False}

    def fail_validation(_db_path):
        raise publish_atlas_packet.PublishError("validation failed")

    def fail_if_called(*_args, **_kwargs):
        generated["called"] = True
        raise AssertionError("site generation should not run after validation failure")

    captured = []
    monkeypatch.setattr(publish_atlas_packet, "run_pre_publish_validation", fail_validation)
    monkeypatch.setattr(publish_atlas_packet, "generate_site", fail_if_called)
    monkeypatch.setattr(publish_atlas_packet, "write_local_status", lambda status, failure=False: captured.append((status, failure)))

    args = argparse.Namespace(
        db=tmp_path / "missing.sqlite",
        site_dir=tmp_path / "site",
        pages_url="https://example.test/",
        dry_run=True,
        poll_live=False,
        poll_timeout=1,
    )

    assert publish_atlas_packet.publish(args) == 1
    assert generated["called"] is False
    assert captured[-1][0]["status"] == "failed"
    assert captured[-1][1] is True
