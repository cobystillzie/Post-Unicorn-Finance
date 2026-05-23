"""Guarded publisher for the Post-Unicorn Finance GitHub Pages atlas packet."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

from automation_safety import (
    EXPORTS_DIR,
    ROOT,
    AutomationLock,
    AutomationLockError,
    CommandError,
    PacketValidationError,
    check_packet_sizes,
    git_status_lines,
    paths_are_site_only,
    run_command,
    split_git_status_by_prefix,
    write_json_and_markdown_status,
)
from atlas_sqlite import DEFAULT_DB
from export_shareable_atlas import build_report


DEFAULT_SITE_DIR = ROOT / "site"
DEFAULT_PAGES_URL = "https://cobystillzie.github.io/Post-Unicorn-Finance/"
REQUIRED_SITE_FILES = [
    "index.html",
    "post_unicorn_industry_atlas_packet.html",
    "post_unicorn_industry_atlas_entities_claims.csv",
    "post_unicorn_industry_atlas_cover_note.md",
    "publish_status.json",
    "publish_status.md",
    ".nojekyll",
]


class PublishError(RuntimeError):
    """Raised when a publish guard blocks the packet update."""


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def short_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def git_stdout(args: list[str]) -> str:
    return run_command(["git", *args]).stdout.strip()


def ensure_main_branch_ready() -> None:
    run_command(["git", "fetch", "origin"])
    branch = git_stdout(["rev-parse", "--abbrev-ref", "HEAD"])
    if branch != "main":
        raise PublishError(f"publisher must run from main; current branch is {branch}")

    upstream = git_stdout(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    if upstream != "origin/main":
        raise PublishError(f"main must track origin/main before publishing; current upstream is {upstream}")

    ahead_behind = git_stdout(["rev-list", "--left-right", "--count", "HEAD...origin/main"]).split()
    ahead = int(ahead_behind[0])
    behind = int(ahead_behind[1])
    if ahead:
        raise PublishError(f"local main is {ahead} commit(s) ahead before publishing; push or reconcile first")
    if behind:
        status = git_status_lines()
        if status:
            raise PublishError("local main is behind origin/main and the worktree is not clean; refusing to fast-forward")
        run_command(["git", "merge", "--ff-only", "origin/main"])


def ensure_no_unrelated_dirty_changes() -> None:
    allowed, blocked = split_git_status_by_prefix(git_status_lines(), ["site"])
    if blocked:
        details = "\n".join(blocked[:12])
        raise PublishError(f"unrelated worktree changes block publishing:\n{details}")
    if allowed:
        print(f"Allowed existing site-only changes before publish: {len(allowed)}")


def ensure_pages_available() -> str:
    result = run_command(
        ["gh", "api", "repos/cobystillzie/Post-Unicorn-Finance/pages", "--jq", ".html_url"],
        check=False,
    )
    if result.returncode != 0:
        remediation = (
            "GitHub Pages is not available through gh api. Confirm `gh auth status`, then enable Pages with "
            "`gh api --method POST repos/cobystillzie/Post-Unicorn-Finance/pages -f build_type=workflow` "
            "or verify Pages settings in GitHub."
        )
        raise PublishError(f"{remediation}\n{result.stderr.strip()}")
    return result.stdout.strip() or DEFAULT_PAGES_URL


def run_pre_publish_validation(db_path: Path) -> list[dict[str, object]]:
    commands = [
        [sys.executable, str(ROOT / "scripts" / "validate_evidence.py")],
        [sys.executable, str(ROOT / "scripts" / "atlas_sqlite.py"), "validate", "--strict-verified-sources"],
    ]
    results: list[dict[str, object]] = []
    for command in commands:
        result = run_command(command, check=True)
        results.append(
            {
                "command": " ".join(command),
                "returncode": result.returncode,
                "stdout_tail": result.stdout[-1200:],
                "stderr_tail": result.stderr[-1200:],
            }
        )
    if not db_path.exists():
        raise PublishError(f"SQLite atlas does not exist: {db_path}")
    return results


def sqlite_counts(db_path: Path) -> dict[str, int]:
    with sqlite3.connect(db_path) as conn:
        return {
            "entity_count": conn.execute("SELECT COUNT(*) FROM industry_entities").fetchone()[0],
            "claim_count": conn.execute("SELECT COUNT(*) FROM entity_claims").fetchone()[0],
            "instrument_mapping_count": conn.execute("SELECT COUNT(*) FROM instrument_provider_map").fetchone()[0],
            "paper_ready_count": conn.execute("SELECT COUNT(*) FROM entity_claims WHERE paper_ready = 1").fetchone()[0],
        }


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inject_publish_metadata(html_path: Path, publish_id: str, generated_at: str) -> None:
    html = html_path.read_text(encoding="utf-8")
    meta = (
        f'  <meta name="post-unicorn-publish-id" content="{publish_id}">\n'
        f'  <meta name="post-unicorn-published-at" content="{generated_at}">'
    )
    if "post-unicorn-publish-id" in html:
        html = "\n".join(line for line in html.splitlines() if "post-unicorn-publish-id" not in line and "post-unicorn-published-at" not in line)
    html = html.replace("</head>", f"{meta}\n</head>")
    footer_line = f"<p>Publish ID: {publish_id}. Published at {generated_at}.</p>"
    html = html.replace("</footer>", f"      {footer_line}\n    </footer>")
    html_path.write_text(html, encoding="utf-8")


def generate_site(db_path: Path, site_dir: Path, publish_id: str, generated_at: str) -> dict[str, str]:
    html_path, csv_path, cover_path = build_report(db_path, site_dir)
    inject_publish_metadata(html_path, publish_id, generated_at)
    index_path = site_dir / "index.html"
    shutil.copyfile(html_path, index_path)
    (site_dir / ".nojekyll").write_text("", encoding="utf-8")
    return {
        "html_path": str(html_path),
        "csv_path": str(csv_path),
        "cover_note_path": str(cover_path),
        "index_path": str(index_path),
        "packet_sha256": file_sha256(index_path),
    }


def validate_packet_contents(site_dir: Path, db_path: Path, *, require_status: bool = True) -> list[str]:
    errors: list[str] = []
    required = REQUIRED_SITE_FILES if require_status else [name for name in REQUIRED_SITE_FILES if not name.startswith("publish_status")]
    for filename in required:
        if not (site_dir / filename).exists():
            errors.append(f"missing required site file: {filename}")

    index_path = site_dir / "index.html"
    csv_path = site_dir / "post_unicorn_industry_atlas_entities_claims.csv"
    if not index_path.exists() or not csv_path.exists():
        return errors

    counts = sqlite_counts(db_path)
    html = index_path.read_text(encoding="utf-8")
    if "working research export" not in html:
        errors.append("missing working-research disclaimer")
    if "not paper-ready" not in html:
        errors.append("missing paper-ready disclaimer")
    if 'id="asset-instrument"' in html:
        errors.append("HTML still contains a top-level Instrument asset section")
    if html.count('class="entity-card"') != counts["entity_count"]:
        errors.append(f"entity card count mismatch: html={html.count('class=\"entity-card\"')} sqlite={counts['entity_count']}")
    if html.count('class="claim"') != counts["claim_count"]:
        errors.append(f"claim count mismatch: html={html.count('class=\"claim\"')} sqlite={counts['claim_count']}")

    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    if len(csv_rows) != counts["claim_count"]:
        errors.append(f"CSV claim row count mismatch: csv={len(csv_rows)} sqlite={counts['claim_count']}")
    if any(row.get("primary_asset_class") == "Instrument" for row in csv_rows):
        errors.append("CSV contains primary_asset_class=Instrument")
    if errors:
        raise PacketValidationError("; ".join(errors))
    return errors


def write_publish_status(site_dir: Path, status: dict[str, object]) -> None:
    write_json_and_markdown_status(site_dir / "publish_status.json", site_dir / "publish_status.md", status)


def write_local_status(status: dict[str, object], *, failure: bool = False) -> None:
    target_dir = EXPORTS_DIR / ("publish_failures" if failure else "publish_status")
    write_json_and_markdown_status(target_dir / "latest.json", target_dir / "latest.md", status)


def stage_and_commit_site(message: str) -> str | None:
    run_command(["git", "add", "site"])
    staged_result = run_command(["git", "diff", "--cached", "--name-only"], check=True)
    staged_paths = [line.strip() for line in staged_result.stdout.splitlines() if line.strip()]
    if not staged_paths:
        return None
    if not paths_are_site_only(staged_paths):
        raise PublishError(f"publisher attempted to stage non-site paths: {staged_paths}")
    run_command(["git", "commit", "-m", message])
    return git_stdout(["rev-parse", "HEAD"])


def push_with_one_site_rebase() -> None:
    result = run_command(["git", "push", "--no-verify", "origin", "main"], check=False, timeout=180)
    if result.returncode == 0:
        return

    run_command(["git", "fetch", "origin"])
    changed = run_command(["git", "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"]).stdout.splitlines()
    if not paths_are_site_only(changed):
        raise PublishError(f"push failed and last commit is not site-only:\n{result.stderr}")
    rebase = run_command(["git", "rebase", "origin/main"], check=False, timeout=180)
    if rebase.returncode != 0:
        run_command(["git", "rebase", "--abort"], check=False)
        raise PublishError(f"push failed and safe rebase failed:\n{result.stderr}\n{rebase.stderr}")
    retry = run_command(["git", "push", "--no-verify", "origin", "main"], check=False, timeout=180)
    if retry.returncode != 0:
        raise PublishError(f"push failed after one safe rebase:\n{retry.stderr}")


def poll_live_page(live_url: str, publish_id: str, *, timeout_seconds: int, interval_seconds: int = 15) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            request = Request(live_url, headers={"User-Agent": "post-unicorn-publisher/1.0"})
            with urlopen(request, timeout=20) as response:
                body = response.read().decode("utf-8", errors="replace")
            if publish_id in body:
                return True
        except (OSError, URLError):
            pass
        time.sleep(interval_seconds)
    return False


def build_status(
    *,
    status: str,
    publish_id: str,
    generated_at: str,
    source_head_sha: str,
    live_url: str,
    counts: dict[str, int],
    packet: dict[str, str],
    validation_results: list[dict[str, object]],
    warnings: list[str],
    dry_run: bool,
    site_commit_sha: str = "",
    live_visible: bool | None = None,
    error: str = "",
) -> dict[str, object]:
    return {
        "status": status,
        "publish_id": publish_id,
        "generated_at": generated_at,
        "source_head_sha": source_head_sha,
        "site_commit_sha": site_commit_sha,
        "live_url": live_url,
        "live_visible": live_visible,
        "dry_run": dry_run,
        **counts,
        "packet": packet,
        "validation_results": validation_results,
        "warnings": warnings,
        "error": error,
    }


def publish(args: argparse.Namespace) -> int:
    db_path = args.db.resolve()
    site_dir = args.site_dir.resolve()
    generated_at = now_iso()
    publish_id = f"atlas-{short_timestamp()}"
    source_head_sha = ""
    counts: dict[str, int] = {}
    packet: dict[str, str] = {}
    validation_results: list[dict[str, object]] = []
    warnings: list[str] = []
    live_url = args.pages_url

    try:
        with AutomationLock("daily-atlas-packet-publisher"):
            if args.dry_run:
                validation_results = run_pre_publish_validation(db_path)
                source_head_sha = git_stdout(["rev-parse", "HEAD"])
                counts = sqlite_counts(db_path)
                packet = generate_site(db_path, site_dir, publish_id, generated_at)
                warnings.extend(check_packet_sizes(site_dir))
                validate_packet_contents(site_dir, db_path, require_status=False)
                status = build_status(
                    status="dry_run_success",
                    publish_id=publish_id,
                    generated_at=generated_at,
                    source_head_sha=source_head_sha,
                    live_url=live_url,
                    counts=counts,
                    packet=packet,
                    validation_results=validation_results,
                    warnings=warnings,
                    dry_run=True,
                )
                write_publish_status(site_dir, status)
                write_local_status(status)
                print(json.dumps(status, indent=2, sort_keys=True))
                return 0

            if site_dir != DEFAULT_SITE_DIR.resolve():
                raise PublishError(f"real publish must write to {DEFAULT_SITE_DIR}; got {site_dir}")

            ensure_main_branch_ready()
            ensure_no_unrelated_dirty_changes()
            live_url = args.pages_url or ensure_pages_available()
            validation_results = run_pre_publish_validation(db_path)
            source_head_sha = git_stdout(["rev-parse", "HEAD"])
            counts = sqlite_counts(db_path)
            packet = generate_site(db_path, site_dir, publish_id, generated_at)
            warnings.extend(check_packet_sizes(site_dir))
            status = build_status(
                status="published",
                publish_id=publish_id,
                generated_at=generated_at,
                source_head_sha=source_head_sha,
                live_url=live_url,
                counts=counts,
                packet=packet,
                validation_results=validation_results,
                warnings=warnings,
                dry_run=False,
            )
            write_publish_status(site_dir, status)
            validate_packet_contents(site_dir, db_path, require_status=True)
            ensure_no_unrelated_dirty_changes()
            site_commit_sha = stage_and_commit_site("chore: publish daily atlas packet")
            if site_commit_sha is None:
                status["status"] = "no_site_changes"
                write_local_status(status)
                print(json.dumps(status, indent=2, sort_keys=True))
                return 0

            push_with_one_site_rebase()
            pushed_sha = git_stdout(["rev-parse", "HEAD"])
            live_visible = None
            if args.poll_live:
                live_visible = poll_live_page(live_url, publish_id, timeout_seconds=args.poll_timeout)
                if not live_visible:
                    warnings.append(f"live page did not show publish_id within {args.poll_timeout}s")
            final_status = build_status(
                status="published" if live_visible is not False else "published_pending_live_visibility",
                publish_id=publish_id,
                generated_at=generated_at,
                source_head_sha=source_head_sha,
                live_url=live_url,
                counts=counts,
                packet=packet,
                validation_results=validation_results,
                warnings=warnings,
                dry_run=False,
                site_commit_sha=pushed_sha,
                live_visible=live_visible,
            )
            write_local_status(final_status)
            print(json.dumps(final_status, indent=2, sort_keys=True))
            return 0
    except (AutomationLockError, CommandError, PacketValidationError, PublishError) as exc:
        failure_counts = counts or (sqlite_counts(db_path) if db_path.exists() else {})
        failure_status = build_status(
            status="failed",
            publish_id=publish_id,
            generated_at=generated_at,
            source_head_sha=source_head_sha,
            live_url=live_url,
            counts=failure_counts,
            packet=packet,
            validation_results=validation_results,
            warnings=warnings,
            dry_run=args.dry_run,
            error=str(exc),
        )
        write_local_status(failure_status, failure=True)
        print(json.dumps(failure_status, indent=2, sort_keys=True))
        return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Safely publish the Post-Unicorn Finance atlas packet to GitHub Pages.")
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--site-dir", type=Path, default=DEFAULT_SITE_DIR)
    parser.add_argument("--pages-url", default=DEFAULT_PAGES_URL)
    parser.add_argument("--dry-run", action="store_true", help="Generate and validate packet files without git commit/push.")
    parser.add_argument("--poll-live", action="store_true", help="Poll GitHub Pages for the new publish ID after push.")
    parser.add_argument("--poll-timeout", type=int, default=300)
    args = parser.parse_args()
    return publish(args)


if __name__ == "__main__":
    raise SystemExit(main())
