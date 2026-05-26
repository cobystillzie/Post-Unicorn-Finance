"""Git hygiene audit and guarded autonomous cleanup for the atlas repo.

Audit mode classifies dirty files and writes a local report.
Autonomous mode may validate, commit recognized safe groups, and push.
It never deletes, resets, stashes, rebases, or force-pushes.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from automation_safety import AutomationLock, AutomationLockError


ROOT = Path(__file__).resolve().parents[1]
EXPORTS = ROOT / "data" / "exports"

REPORT_JSON = "repo_hygiene_status.json"
REPORT_MD = "repo_hygiene_status.md"

SAFE_COMMIT_CATEGORIES = {
    "evidence_csv_churn",
    "publish_site",
    "code",
    "tests",
    "docs_or_repo_config",
    "github_workflow",
}

COMMIT_GROUPS = {
    "evidence": {"evidence_csv_churn"},
    "site": {"publish_site"},
    "repo": {"code", "tests", "docs_or_repo_config", "github_workflow"},
}

COMMIT_MESSAGES = {
    "evidence": "chore(evidence): snapshot atlas evidence",
    "site": "chore(site): update atlas packet",
    "repo": "chore(repo): apply hygiene-safe updates",
}


@dataclass(frozen=True)
class CommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str


class HygieneBlocker(RuntimeError):
    """Raised when autonomous cleanup would be unsafe."""

    def __init__(self, message: str, payload: dict[str, object] | None = None) -> None:
        super().__init__(message)
        self.payload = payload or {}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def run_git(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def run_command(args: list[str], *, check: bool = True, timeout: int | None = None) -> CommandResult:
    result = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    wrapped = CommandResult(args=args, returncode=result.returncode, stdout=result.stdout, stderr=result.stderr)
    if check and wrapped.returncode != 0:
        raise HygieneBlocker(
            f"Command failed: {' '.join(args)}",
            {"args": args, "returncode": wrapped.returncode, "stdout": wrapped.stdout, "stderr": wrapped.stderr},
        )
    return wrapped


def parse_status_path(line: str) -> str:
    raw = line[3:].strip()
    if " -> " in raw:
        raw = raw.split(" -> ", 1)[1]
    return raw.strip().strip('"').replace("\\", "/")


def parse_status_line(line: str) -> dict[str, str]:
    if line.startswith("## "):
        return {"code": "##", "path": "", "raw": line}
    return {"code": line[:2], "path": parse_status_path(line), "raw": line}


def categorize_path(path: str, code: str = "") -> str:
    normalized = path.replace("\\", "/")
    if code == "!!":
        return "ignored_generated"
    if normalized in {"data/learning", "data/learning/", "data/learning/.gitkeep"}:
        return "docs_or_repo_config"
    if normalized.startswith(".env") or "credential" in normalized.lower() or "secret" in normalized.lower():
        return "blocked_secret_or_env"
    if normalized.startswith("data/evidence/"):
        return "evidence_csv_churn" if normalized.endswith(".csv") else "other_dirty"
    if normalized.startswith("data/exports/"):
        return "local_exports"
    if normalized.startswith("data/runtime/") or normalized.startswith("data/learning/"):
        return "local_runtime_or_learning"
    if normalized.startswith("site/"):
        return "publish_site"
    if normalized.startswith(".github/"):
        return "github_workflow"
    if normalized.startswith("scripts/"):
        return "code"
    if normalized.startswith("tests/"):
        return "tests"
    if normalized.startswith("docs/") or normalized in {"README.md", ".gitignore"}:
        return "docs_or_repo_config"
    if normalized.endswith(".sqlite") or ".sqlite-" in normalized:
        return "local_database"
    if "__pycache__/" in normalized or normalized.endswith(".pyc") or ".pytest_cache/" in normalized:
        return "ignored_generated"
    return "other_dirty"


def pathspec_for_row(row: dict[str, str]) -> str:
    path = row["path"]
    normalized = path.rstrip("/").replace("\\", "/")
    if normalized == "data/learning":
        return "data/learning/.gitkeep"
    return path


def is_staged_status(code: str) -> bool:
    return bool(code) and code[0] not in {" ", "?"}


def blocked_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    blocked: list[dict[str, str]] = []
    for row in rows:
        if row["category"] not in SAFE_COMMIT_CATEGORIES:
            blocked.append(row)
            continue
        if is_staged_status(row["code"]):
            blocked.append(row)
    return blocked


def commit_plan(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    plan: dict[str, list[str]] = {group: [] for group in COMMIT_GROUPS}
    for row in rows:
        if row["category"] not in SAFE_COMMIT_CATEGORIES or is_staged_status(row["code"]):
            continue
        for group, categories in COMMIT_GROUPS.items():
            if row["category"] in categories:
                pathspec = pathspec_for_row(row)
                if pathspec not in plan[group]:
                    plan[group].append(pathspec)
                break
    return {group: paths for group, paths in plan.items() if paths}


def staged_paths() -> list[str]:
    result = run_git(["diff", "--cached", "--name-only"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def git_status(include_ignored: bool = False) -> list[dict[str, str]]:
    args = ["status", "--porcelain=v1", "--branch", "--untracked-files=all"]
    if include_ignored:
        args.append("--ignored=matching")
    result = run_git(args)
    if result.returncode != 0:
        raise RuntimeError(result.stderr or result.stdout)
    rows = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        parsed = parse_status_line(line)
        if parsed["code"] == "##":
            continue
        parsed["category"] = categorize_path(parsed["path"], parsed["code"])
        rows.append(parsed)
    return rows


def branch_status() -> dict[str, object]:
    branch_result = run_git(["rev-parse", "--abbrev-ref", "HEAD"])
    upstream_result = run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
    upstream = upstream_result.stdout.strip() if upstream_result.returncode == 0 else ""
    ahead = 0
    behind = 0
    if upstream:
        counts = run_git(["rev-list", "--left-right", "--count", f"{branch}...{upstream}"])
        if counts.returncode == 0:
            parts = counts.stdout.strip().split()
            if len(parts) == 2:
                ahead = int(parts[0])
                behind = int(parts[1])
    return {"branch": branch, "upstream": upstream, "ahead": ahead, "behind": behind}


def summarize(rows: list[dict[str, str]]) -> dict[str, object]:
    categories: dict[str, list[dict[str, str]]] = {}
    for row in rows:
        categories.setdefault(row["category"], []).append(row)
    counts = {category: len(items) for category, items in sorted(categories.items())}
    risky = [
        category
        for category in counts
        if category
        not in {
            "evidence_csv_churn",
            "local_exports",
            "local_runtime_or_learning",
            "local_database",
            "ignored_generated",
        }
    ]
    return {
        "counts": counts,
        "categories": categories,
        "risky_categories": risky,
        "has_evidence_churn": bool(counts.get("evidence_csv_churn")),
        "has_code_or_docs_churn": any(category in counts for category in ["code", "tests", "docs_or_repo_config"]),
        "has_publish_churn": bool(counts.get("publish_site")),
    }


def recommendations(summary: dict[str, object], branch: dict[str, object]) -> list[str]:
    counts = summary["counts"]
    notes: list[str] = []
    if branch.get("behind"):
        notes.append(f"Remote is ahead by {branch['behind']} commit(s); autonomous cleanup may fast-forward only.")
    if counts.get("evidence_csv_churn"):
        notes.append("Evidence CSV changes should be validated, reviewed, and committed as an evidence snapshot if they are real atlas growth.")
    if counts.get("publish_site"):
        notes.append("Site changes should be published only through scripts/publish_atlas_packet.py.")
    if summary["has_code_or_docs_churn"]:
        notes.append("Code/docs/tests changes should stay separate from evidence snapshot commits.")
    if counts.get("other_dirty"):
        notes.append("Other dirty files require manual classification before cleanup.")
    if not counts:
        notes.append("Worktree is clean.")
    notes.append("No destructive cleanup is performed by this script.")
    return notes


def write_report(payload: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / REPORT_JSON
    markdown_path = output_dir / REPORT_MD
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")

    lines = [
        "# Repo Hygiene Status",
        "",
        f"Generated: {payload['generated_at']}",
        f"Branch: {payload['branch']['branch']}",
        f"Upstream: {payload['branch']['upstream'] or 'none'}",
        f"Ahead: {payload['branch']['ahead']}",
        f"Behind: {payload['branch']['behind']}",
        "",
        "## Dirty Categories",
    ]
    counts = payload["summary"]["counts"]
    if counts:
        for category, count in counts.items():
            lines.append(f"- {category}: {count}")
    else:
        lines.append("- none: 0")

    lines.extend(["", "## Files"])
    categories = payload["summary"]["categories"]
    if categories:
        for category, rows in categories.items():
            lines.append(f"### {category}")
            for row in rows:
                lines.append(f"- `{row['code']}` `{row['path']}`")
    else:
        lines.append("- No dirty files.")

    lines.extend(["", "## Recommendations"])
    for note in payload["recommendations"]:
        lines.append(f"- {note}")

    if payload.get("autonomous"):
        auto = payload["autonomous"]
        lines.extend(["", "## Autonomous Cleanup"])
        lines.append(f"- Dry run: {auto.get('dry_run')}")
        lines.append(f"- Push requested: {auto.get('push_requested')}")
        lines.append(f"- Status: {auto.get('status')}")
        if auto.get("commands"):
            lines.append("- Commands:")
            for command in auto["commands"]:  # type: ignore[index]
                lines.append(f"  - {command}")
        if auto.get("commit_plan"):
            lines.append("- Commit plan:")
            for group, paths in auto["commit_plan"].items():  # type: ignore[union-attr]
                lines.append(f"  - {group}: {len(paths)} path(s)")
        if auto.get("commits"):
            lines.append("- Commits:")
            for commit in auto["commits"]:  # type: ignore[index]
                lines.append(f"  - {commit}")
        if auto.get("push"):
            lines.append(f"- Push: {auto.get('push')}")
        if auto.get("blocker"):
            lines.append(f"- Blocker: {auto.get('blocker')}")

    lines.extend(
        [
            "",
            "## Policy",
            "- Audit mode does not delete, reset, stash, stage, commit, or push files.",
            "- Autonomous mode may stage, commit, and push only recognized safe path groups after validation.",
            "- Evidence files are research artifacts, not disposable cache.",
            "- Generated ignored files may be pruned later only through an explicit destructive-clean policy.",
        ]
    )
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, markdown_path


def build_payload(include_ignored: bool = False) -> dict[str, object]:
    rows = git_status(include_ignored=include_ignored)
    branch = branch_status()
    summary = summarize(rows)
    return {
        "generated_at": now_iso(),
        "include_ignored": include_ignored,
        "branch": branch,
        "summary": summary,
        "recommendations": recommendations(summary, branch),
    }


def run_validation_commands() -> list[str]:
    commands = [
        [sys.executable, "scripts/research_agents.py", "promotion-loop", "--limit", "10"],
        [sys.executable, "scripts/validate_evidence.py"],
        [sys.executable, "scripts/atlas_sqlite.py", "validate", "--strict-verified-sources"],
        [sys.executable, "-m", "pytest", "-q"],
    ]
    executed: list[str] = []
    for command in commands:
        result = run_command(command, timeout=180)
        executed.append(" ".join(command))
        if result.returncode != 0:
            raise HygieneBlocker(
                f"Validation command failed: {' '.join(command)}",
                {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
            )
    return executed


def run_promotion_and_validation_direct(promotion_limit: int) -> list[str]:
    from research_agents import DEFAULT_DB, promotion_loop

    commands = [f"promotion_loop(limit={promotion_limit})"]
    promotion_status = promotion_loop(DEFAULT_DB, limit=promotion_limit)
    if promotion_status != 0:
        raise HygieneBlocker("promotion-loop failed", {"returncode": promotion_status})
    validation_commands = [
        [sys.executable, "scripts/validate_evidence.py"],
        [sys.executable, "scripts/atlas_sqlite.py", "validate", "--strict-verified-sources"],
        [sys.executable, "-m", "pytest", "-q"],
    ]
    for command in validation_commands:
        result = run_command(command, timeout=180)
        commands.append(" ".join(command))
        if result.returncode != 0:
            raise HygieneBlocker(
                f"Validation command failed: {' '.join(command)}",
                {"stdout": result.stdout, "stderr": result.stderr, "returncode": result.returncode},
            )
    return commands


def fetch_and_fast_forward(dry_run: bool) -> list[str]:
    commands: list[str] = []
    if dry_run:
        commands.append("dry-run: skip git fetch and fast-forward")
        return commands
    result = run_git(["fetch", "origin"])
    commands.append("git fetch origin")
    if result.returncode != 0:
        raise HygieneBlocker("git fetch origin failed", {"stdout": result.stdout, "stderr": result.stderr})
    branch = branch_status()
    if branch["ahead"] and branch["behind"]:
        raise HygieneBlocker(
            "branch has diverged from upstream; fast-forward-only policy blocks cleanup",
            {"branch": branch},
        )
    if branch["behind"]:
        merge = run_git(["merge", "--ff-only", "@{u}"])
        commands.append("git merge --ff-only @{u}")
        if merge.returncode != 0:
            raise HygieneBlocker("fast-forward failed", {"stdout": merge.stdout, "stderr": merge.stderr, "branch": branch})
    return commands


def ensure_no_unknown_or_staged(rows: list[dict[str, str]]) -> None:
    blocked = blocked_rows(rows)
    if blocked:
        raise HygieneBlocker(
            "dirty files include blocked categories or pre-staged changes",
            {"blocked": blocked},
        )


def group_allowed_staged_paths(group: str, paths: list[str]) -> bool:
    categories = COMMIT_GROUPS[group]
    return all(categorize_path(path) in categories for path in paths)


def create_commit(group: str, paths: list[str], dry_run: bool) -> str | None:
    if dry_run:
        return None
    if not paths:
        return None
    add = run_git(["add", "--", *paths])
    if add.returncode != 0:
        raise HygieneBlocker(f"git add failed for {group}", {"stdout": add.stdout, "stderr": add.stderr, "paths": paths})
    staged = staged_paths()
    if not staged:
        return None
    if not group_allowed_staged_paths(group, staged):
        run_git(["restore", "--staged", "--", *staged])
        raise HygieneBlocker("staged paths escaped commit group", {"group": group, "staged": staged})
    commit = run_git(["commit", "-m", COMMIT_MESSAGES[group]])
    if commit.returncode != 0:
        raise HygieneBlocker(f"git commit failed for {group}", {"stdout": commit.stdout, "stderr": commit.stderr})
    sha = run_git(["rev-parse", "--short", "HEAD"])
    return sha.stdout.strip() if sha.returncode == 0 else COMMIT_MESSAGES[group]


def push_if_requested(push: bool, dry_run: bool, commits: list[str]) -> str:
    if not push:
        return "not_requested"
    if dry_run:
        return "dry_run_skipped"
    if not commits:
        return "no_commits_to_push"
    status = branch_status()
    if status["behind"]:
        raise HygieneBlocker("branch is behind before push", {"branch": status})
    push_result = run_git(["push", "origin", "HEAD:main"])
    if push_result.returncode != 0:
        raise HygieneBlocker("git push failed", {"stdout": push_result.stdout, "stderr": push_result.stderr})
    return "pushed"


def autonomous_cleanup(
    *,
    output_dir: Path,
    promotion_limit: int,
    push: bool,
    dry_run: bool,
    include_ignored: bool = False,
) -> dict[str, object]:
    commands: list[str] = []
    commits: list[str] = []
    autonomous: dict[str, object] = {
        "status": "started",
        "dry_run": dry_run,
        "push_requested": push,
        "promotion_limit": promotion_limit,
        "commands": commands,
        "commits": commits,
    }
    try:
        commands.extend(fetch_and_fast_forward(dry_run=dry_run))
        if dry_run:
            commands.append(f"dry-run: skip promotion_loop(limit={promotion_limit})")
            commands.append("dry-run: skip validation commands")
        else:
            commands.extend(run_promotion_and_validation_direct(promotion_limit))

        rows = git_status(include_ignored=include_ignored)
        ensure_no_unknown_or_staged(rows)
        plan = commit_plan(rows)
        autonomous["commit_plan"] = plan
        for group in ["evidence", "site", "repo"]:
            sha = create_commit(group, plan.get(group, []), dry_run=dry_run)
            if sha:
                commits.append(f"{group}:{sha}")
        autonomous["push"] = push_if_requested(push, dry_run=dry_run, commits=commits)
        autonomous["status"] = "ok"
    except HygieneBlocker as exc:
        autonomous["status"] = "blocked"
        autonomous["blocker"] = str(exc)
        autonomous["blocker_payload"] = exc.payload

    payload = build_payload(include_ignored=include_ignored)
    payload["autonomous"] = autonomous
    write_report(payload, output_dir)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=str(EXPORTS))
    parser.add_argument("--include-ignored", action="store_true")
    sub = parser.add_subparsers(dest="command")

    autonomous = sub.add_parser("autonomous-cleanup")
    autonomous.add_argument("--promotion-limit", type=int, default=10)
    autonomous.add_argument("--push", action="store_true")
    autonomous.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        with AutomationLock("repo-hygiene-audit"):
            if args.command == "autonomous-cleanup":
                payload = autonomous_cleanup(
                    output_dir=Path(args.output_dir),
                    promotion_limit=args.promotion_limit,
                    push=args.push,
                    dry_run=args.dry_run,
                    include_ignored=args.include_ignored,
                )
                json_path = Path(args.output_dir) / REPORT_JSON
                markdown_path = Path(args.output_dir) / REPORT_MD
                if payload["autonomous"]["status"] == "blocked":  # type: ignore[index]
                    print(f"Repo hygiene autonomous cleanup blocked: {payload['autonomous']['blocker']}", file=sys.stderr)  # type: ignore[index]
                    return 1
            else:
                payload = build_payload(include_ignored=args.include_ignored)
                json_path, markdown_path = write_report(payload, Path(args.output_dir))
    except AutomationLockError as exc:
        print(f"Repo hygiene audit skipped: {exc}", file=sys.stderr)
        return 2

    counts = payload["summary"]["counts"]
    print(f"Wrote {json_path}")
    print(f"Wrote {markdown_path}")
    print(json.dumps(counts, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
