import csv
import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from atlas_sqlite import import_csvs, ranked_rows_from_db, validate_database  # noqa: E402
import export_shareable_atlas  # noqa: E402
import research_agents  # noqa: E402
from research_agents import run_loop, source_urls_to_fetch  # noqa: E402


def csv_count(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def add_fake_source_pages_for_verified_claims(db_path: Path) -> None:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    claims = conn.execute(
        "SELECT DISTINCT source_url FROM entity_claims WHERE evidence_status = 'verified_fact'"
    ).fetchall()
    for index, claim in enumerate(claims, start=1):
        conn.execute(
            """
            INSERT OR REPLACE INTO source_pages (
                page_id, source_url, fetched_at, status_code, fetch_status,
                content_type, title, raw_text, text_hash, error
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"test-page-{index}",
                claim["source_url"],
                "2026-05-22T00:00:00+00:00",
                200,
                "ok",
                "text/html",
                "Test source",
                "Direct source text evidence for a verified atlas claim.",
                "testhash",
                "",
            ),
        )
    conn.commit()
    conn.close()


def copy_evidence(tmp_path: Path, monkeypatch) -> Path:
    evidence_dir = tmp_path / "evidence"
    shutil.copytree(ROOT / "data" / "evidence", evidence_dir)
    monkeypatch.setattr(research_agents, "EVIDENCE", evidence_dir)
    return evidence_dir


def append_csv_row(path: Path, row: dict[str, str]) -> None:
    with path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = list(rows[0].keys())
    rows.append(row)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def add_source_registry_row(evidence_dir: Path, source_url: str, name: str) -> None:
    append_csv_row(
        evidence_dir / "source_registry.csv",
        {
            "source_url": source_url,
            "source_name": name,
            "source_type": "official_site",
            "source_quality": "primary",
            "license_or_access": "public web",
            "notes": "Test source.",
            "last_checked": "2026-05-22",
        },
    )


def add_intake_row(evidence_dir: Path, **overrides: str) -> dict[str, str]:
    row = {
        "lead_id": "intake-promotable-smv",
        "name": "Promotable SMV Fund",
        "lead_type": "test_lead",
        "website": "https://promotablesmv.example/",
        "source_urls": "https://promotablesmv.example/",
        "discovered_from": "test",
        "target_asset_class": "SMV",
        "target_entity_type": "capital provider",
        "active_status": "unknown",
        "source_tier": "public_web",
        "priority": "high",
        "evidence_status": "needs_verification",
        "review_status": "queued",
        "created_at": "2026-05-22",
        "notes": "Test intake row.",
    }
    row.update(overrides)
    append_csv_row(evidence_dir / "entity_intake_queue.csv", row)
    add_source_registry_row(evidence_dir, row["website"], f"{row['name']} official site")
    return row


def add_source_page(db_path: Path, source_url: str, raw_text: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute(
        """
        INSERT OR REPLACE INTO source_pages (
            page_id, source_url, fetched_at, status_code, fetch_status,
            content_type, title, raw_text, text_hash, error
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            f"page-{abs(hash(source_url))}",
            source_url,
            "2026-05-22T00:00:00+00:00",
            200,
            "ok",
            "text/html",
            "Test source",
            raw_text,
            "testhash",
            "",
        ),
    )
    conn.commit()
    conn.close()


def test_sqlite_import_preserves_csv_counts(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    counts = import_csvs(db_path)

    assert counts["industry_entities"] == csv_count(ROOT / "data" / "evidence" / "industry_entities.csv")
    assert counts["entity_claims"] == csv_count(ROOT / "data" / "evidence" / "entity_claims.csv")
    assert counts["entity_intake_queue"] == csv_count(ROOT / "data" / "evidence" / "entity_intake_queue.csv")
    assert validate_database(db_path, exact_csv_counts=True) == []


def test_strict_validation_accepts_verified_claim_source_text(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)
    add_fake_source_pages_for_verified_claims(db_path)

    assert validate_database(db_path, strict_verified_sources=True, exact_csv_counts=True) == []


def test_scoring_examples_tinyseed_and_khazanah(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)
    rows = ranked_rows_from_db(db_path, 1000)
    by_name = {row["name"]: row for row in rows}

    assert by_name["TinySeed"]["fit_score"] == "93"
    assert by_name["TinySeed"]["atlas_priority_score"] == "120"
    assert by_name["Khazanah Nasional"]["fit_score"] == "74"
    assert by_name["Khazanah Nasional"]["atlas_priority_score"] == "94"


def test_ranked_rows_default_can_include_all_entities(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)

    assert len(ranked_rows_from_db(db_path, 0)) == csv_count(ROOT / "data" / "evidence" / "industry_entities.csv")
    assert len(ranked_rows_from_db(db_path, 50)) == 50


def test_instrument_mapping_tinyseed_not_khazanah(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    tinyseed = conn.execute(
        """
        SELECT instrument_id
        FROM instrument_provider_map
        WHERE provider_name = 'TinySeed'
        """
    ).fetchall()
    khazanah = conn.execute(
        """
        SELECT instrument_id
        FROM instrument_provider_map
        WHERE provider_name = 'Khazanah Nasional'
        """
    ).fetchall()
    conn.close()

    assert {row["instrument_id"] for row in tinyseed} == {"revenue_share"}
    assert khazanah == []


def test_instrument_is_not_primary_entity_class(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    primary_instrument = conn.execute(
        "SELECT COUNT(*) FROM industry_entities WHERE primary_asset_class = 'Instrument'"
    ).fetchone()[0]
    mapped_instrument = conn.execute(
        "SELECT COUNT(*) FROM instrument_provider_map WHERE asset_class = 'Instrument'"
    ).fetchone()[0]
    mapping_count = conn.execute("SELECT COUNT(*) FROM instrument_provider_map").fetchone()[0]
    conn.close()

    assert primary_instrument == 0
    assert mapped_instrument == 0
    assert mapping_count == 73
    assert validate_database(db_path, exact_csv_counts=True) == []


def test_shareable_atlas_separates_instruments_from_asset_sections(tmp_path):
    db_path = ROOT / "data" / "atlas.sqlite"
    if not db_path.exists():
        db_path = tmp_path / "atlas.sqlite"
        import_csvs(db_path)

    conn = sqlite3.connect(db_path)
    entity_count = conn.execute("SELECT COUNT(*) FROM industry_entities").fetchone()[0]
    claim_count = conn.execute("SELECT COUNT(*) FROM entity_claims").fetchone()[0]
    mapping_count = conn.execute("SELECT COUNT(*) FROM instrument_provider_map").fetchone()[0]
    conn.close()

    html_path, csv_path, _cover_path = export_shareable_atlas.build_report(db_path, tmp_path / "exports")
    html = html_path.read_text(encoding="utf-8")
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))

    assert html.count('class="entity-card"') == entity_count
    assert html.count('class="claim"') == claim_count
    assert len(csv_rows) == claim_count
    assert mapping_count == 73
    assert 'id="asset-instrument"' not in html
    assert "Instrument Providers And Financing Mechanisms" in html
    assert "research_dossier.html" in html
    assert "Research Dossier v0.1" in html
    assert all(row["primary_asset_class"] != "Instrument" for row in csv_rows)


def test_onesixone_is_intake_only():
    with (ROOT / "data" / "evidence" / "entity_intake_queue.csv").open("r", encoding="utf-8", newline="") as handle:
        intake_rows = list(csv.DictReader(handle))
    with (ROOT / "data" / "evidence" / "industry_entities.csv").open("r", encoding="utf-8", newline="") as handle:
        entity_rows = list(csv.DictReader(handle))
    with (ROOT / "data" / "evidence" / "entity_claims.csv").open("r", encoding="utf-8", newline="") as handle:
        claim_rows = list(csv.DictReader(handle))

    assert any(row["name"] == "OneSixOne Ventures" for row in intake_rows)
    assert all(row["name"] != "OneSixOne Ventures" for row in entity_rows)
    assert all(row["entity_name"] != "OneSixOne Ventures" for row in claim_rows)


def test_source_fetch_prioritizes_verified_and_intake_urls(tmp_path):
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    urls = source_urls_to_fetch(conn, verified_only=False, limit=5)
    conn.close()

    assert urls[0] == "https://tinyseed.com/"
    assert "https://www.onesixone.ventures/" in urls


def test_search_queue_uses_scrape_targets():
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "scrape_seed_searches.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    queue_path = ROOT / "data" / "exports" / "search_queue.csv"
    targets_path = ROOT / "data" / "evidence" / "scrape_targets.csv"
    with queue_path.open("r", encoding="utf-8", newline="") as handle:
        queue_rows = list(csv.DictReader(handle))

    intake_path = ROOT / "data" / "evidence" / "entity_intake_queue.csv"
    assert len(queue_rows) == csv_count(targets_path) + csv_count(intake_path)
    assert queue_rows[0]["queue_id"].startswith("atlas-search-")
    assert queue_rows[0]["intake_table"] == "industry_entities.csv + entity_claims.csv"
    assert queue_rows[-1]["queue_id"].startswith("entity-intake-")
    assert queue_rows[-1]["intake_table"] == "entity_intake_queue.csv"
    assert queue_rows[-1]["query"].startswith("OneSixOne Ventures")


def test_hourly_loop_does_not_mark_paper_ready(tmp_path, monkeypatch):
    db_path = tmp_path / "atlas.sqlite"

    def fake_fetch_url(_source_url: str, timeout: int = 20) -> dict[str, object]:
        return {
            "status_code": 200,
            "fetch_status": "ok",
            "content_type": "text/html",
            "title": "Test source",
            "raw_text": "TinySeed revenue-based B2B SaaS source text. OneSixOne Ventures pre-seed platform source text.",
            "error": "",
        }

    monkeypatch.setattr("research_agents.fetch_url", fake_fetch_url)

    assert run_loop(db_path, fetch_limit=5, verified_only=False, mode="hourly-loop-test") == 0

    conn = sqlite3.connect(db_path)
    paper_ready = conn.execute("SELECT COUNT(*) FROM entity_claims WHERE paper_ready = 1").fetchone()[0]
    conn.close()
    assert paper_ready == 0


def test_promote_intake_creates_candidate_entity_and_claim(tmp_path, monkeypatch):
    evidence_dir = copy_evidence(tmp_path, monkeypatch)
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)
    add_intake_row(evidence_dir)
    add_source_page(
        db_path,
        "https://promotablesmv.example/",
        "Promotable SMV Fund is a capital efficient founder-led B2B SaaS capital provider for bootstrapped software companies.",
    )

    assert research_agents.promote_intake_agent(db_path, limit=10) == 0

    entity_rows = list(csv.DictReader((evidence_dir / "industry_entities.csv").open("r", encoding="utf-8", newline="")))
    claim_rows = list(csv.DictReader((evidence_dir / "entity_claims.csv").open("r", encoding="utf-8", newline="")))
    intake_rows = list(csv.DictReader((evidence_dir / "entity_intake_queue.csv").open("r", encoding="utf-8", newline="")))
    promoted_entity = next(row for row in entity_rows if row["name"] == "Promotable SMV Fund")
    promoted_claim = next(row for row in claim_rows if row["entity_name"] == "Promotable SMV Fund")
    promoted_intake = next(row for row in intake_rows if row["name"] == "Promotable SMV Fund")

    assert promoted_entity["primary_asset_class"] == "SMV"
    assert promoted_entity["evidence_status"] == "candidate_evidence"
    assert promoted_claim["evidence_status"] == "candidate_evidence"
    assert promoted_intake["review_status"] == "promoted"

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    assert conn.execute("SELECT COUNT(*) FROM entity_claims WHERE entity_name = 'Promotable SMV Fund' AND paper_ready = 0").fetchone()[0] == 1
    review = conn.execute("SELECT * FROM intake_promotion_reviews WHERE name = 'Promotable SMV Fund'").fetchone()
    conn.close()
    assert review["status"] == "promoted"
    assert "capital efficient" in review["source_snippet"].lower()


def test_promote_intake_marks_duplicate_without_new_entity(tmp_path, monkeypatch):
    evidence_dir = copy_evidence(tmp_path, monkeypatch)
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)
    add_intake_row(
        evidence_dir,
        lead_id="intake-duplicate-tinyseed",
        name="TinySeed",
        website="https://tinyseed.com/",
        source_urls="https://tinyseed.com/",
    )
    before = csv_count(evidence_dir / "industry_entities.csv")

    assert research_agents.promote_intake_agent(db_path, limit=10) == 0

    intake_rows = list(csv.DictReader((evidence_dir / "entity_intake_queue.csv").open("r", encoding="utf-8", newline="")))
    duplicate = next(row for row in intake_rows if row["lead_id"] == "intake-duplicate-tinyseed")
    assert duplicate["review_status"] == "duplicate"
    assert csv_count(evidence_dir / "industry_entities.csv") == before


def test_promote_intake_marks_weak_source_needs_more_source(tmp_path, monkeypatch):
    evidence_dir = copy_evidence(tmp_path, monkeypatch)
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)
    add_intake_row(
        evidence_dir,
        lead_id="intake-weak-source",
        name="Weak Source Capital",
        website="https://weaksource.example/",
        source_urls="https://weaksource.example/",
    )
    add_source_page(db_path, "https://weaksource.example/", "Weak Source Capital has a website.")

    assert research_agents.promote_intake_agent(db_path, limit=10) == 0

    intake_rows = list(csv.DictReader((evidence_dir / "entity_intake_queue.csv").open("r", encoding="utf-8", newline="")))
    weak = next(row for row in intake_rows if row["lead_id"] == "intake-weak-source")
    assert weak["review_status"] == "needs_more_source"
    assert all(row["name"] != "Weak Source Capital" for row in csv.DictReader((evidence_dir / "industry_entities.csv").open("r", encoding="utf-8", newline="")))


def test_failed_intake_review_source_matches_checks(tmp_path, monkeypatch):
    evidence_dir = copy_evidence(tmp_path, monkeypatch)
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)
    add_intake_row(
        evidence_dir,
        lead_id="intake-audit-source",
        name="Audit Source Capital",
        website="https://auditsource.example/",
        source_urls="https://auditsource.example/;https://profiles.example/audit-source-capital",
    )
    add_source_page(db_path, "https://auditsource.example/", "Audit Source Capital has a website.")
    add_source_page(
        db_path,
        "https://profiles.example/audit-source-capital",
        "Audit Source Capital is listed as a capital provider, but this profile does not confirm auditsource.example.",
    )

    assert research_agents.promote_intake_agent(db_path, limit=10) == 0

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    review = conn.execute(
        "SELECT source_url, checks FROM intake_promotion_reviews WHERE lead_id = 'intake-audit-source'"
    ).fetchone()
    conn.close()

    checks = json.loads(review["checks"])
    assert review["source_url"] == checks["source_url"]


def test_onesixone_unknown_candidate_is_not_promoted_from_uvc_only_source(tmp_path, monkeypatch):
    evidence_dir = copy_evidence(tmp_path, monkeypatch)
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)
    add_source_page(
        db_path,
        "https://www.onesixone.ventures/",
        "OneSixOne Ventures is a pre-seed VC firm and community for early-stage startups.",
    )

    assert research_agents.promote_intake_agent(db_path, limit=10) == 0

    intake_rows = list(csv.DictReader((evidence_dir / "entity_intake_queue.csv").open("r", encoding="utf-8", newline="")))
    onesixone = next(row for row in intake_rows if row["name"] == "OneSixOne Ventures")
    assert onesixone["review_status"] == "needs_more_source"
    assert all(row["name"] != "OneSixOne Ventures" for row in csv.DictReader((evidence_dir / "industry_entities.csv").open("r", encoding="utf-8", newline="")))


def test_verify_intake_writes_review_without_promoting(tmp_path, monkeypatch):
    evidence_dir = copy_evidence(tmp_path, monkeypatch)
    db_path = tmp_path / "atlas.sqlite"
    import_csvs(db_path)
    add_intake_row(evidence_dir)
    add_source_page(
        db_path,
        "https://promotablesmv.example/",
        "Promotable SMV Fund is a capital efficient founder-led B2B SaaS capital provider for bootstrapped software companies.",
    )

    assert research_agents.verify_intake_agent(db_path, limit=10) == 0

    entity_rows = list(csv.DictReader((evidence_dir / "industry_entities.csv").open("r", encoding="utf-8", newline="")))
    assert all(row["name"] != "Promotable SMV Fund" for row in entity_rows)
    conn = sqlite3.connect(db_path)
    status = conn.execute("SELECT status FROM intake_promotion_reviews WHERE name = 'Promotable SMV Fund'").fetchone()[0]
    conn.close()
    assert status == "ready_for_promotion"
