"""Shared safety utilities for local Post-Unicorn automation jobs."""

from __future__ import annotations

import json
import os
import subprocess
import ctypes
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_DIR = ROOT / "data" / "runtime"
EXPORTS_DIR = ROOT / "data" / "exports"
LOCK_PATH = RUNTIME_DIR / "post_unicorn_automation.lock"
DEFAULT_STALE_AFTER_SECONDS = 3 * 60 * 60


class AutomationLockError(RuntimeError):
    """Raised when another local atlas automation owns the shared lock."""


class CommandError(RuntimeError):
    """Raised when a subprocess exits unsuccessfully."""

    def __init__(self, result: "CommandResult") -> None:
        self.result = result
        message = (
            f"Command failed with exit code {result.returncode}: {' '.join(result.args)}\n"
            f"STDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )
        super().__init__(message)


class PacketValidationError(RuntimeError):
    """Raised when generated packet files fail publish safety checks."""


@dataclass(frozen=True)
class CommandResult:
    args: list[str]
    returncode: int
    stdout: str
    stderr: str


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def pid_exists(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        process_query_limited_information = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(process_query_limited_information, False, pid)
        if handle:
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        return False
    try:
        os.kill(pid, 0)
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def run_command(
    args: Iterable[str],
    *,
    cwd: Path = ROOT,
    check: bool = True,
    timeout: int | None = None,
) -> CommandResult:
    result = subprocess.run(
        list(args),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
        timeout=timeout,
    )
    wrapped = CommandResult(
        args=list(args),
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )
    if check and wrapped.returncode != 0:
        raise CommandError(wrapped)
    return wrapped


def _lock_payload(owner: str, stale_after_seconds: int) -> dict[str, object]:
    return {
        "owner": owner,
        "pid": os.getpid(),
        "cwd": str(ROOT),
        "started_at": now_iso(),
        "stale_after_seconds": stale_after_seconds,
    }


def _read_lock(path: Path) -> dict[str, object]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _lock_age_seconds(payload: dict[str, object]) -> float | None:
    started_at = payload.get("started_at")
    if not isinstance(started_at, str) or not started_at:
        return None
    try:
        started = datetime.fromisoformat(started_at)
    except ValueError:
        return None
    if started.tzinfo is None:
        started = started.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - started.astimezone(timezone.utc)).total_seconds()


def stale_lock_reason(payload: dict[str, object], stale_after_seconds: int) -> str | None:
    pid = payload.get("pid")
    if not isinstance(pid, int):
        return "lock file has no valid pid"
    if not pid_exists(pid):
        return f"pid {pid} is not running"
    age = _lock_age_seconds(payload)
    if age is None:
        return "lock file has no valid timestamp"
    if age > stale_after_seconds:
        return f"lock age {int(age)}s exceeded {stale_after_seconds}s"
    return None


class AutomationLock:
    """Exclusive file lock shared by research, promotion, and publish loops."""

    def __init__(
        self,
        owner: str,
        *,
        lock_path: Path = LOCK_PATH,
        stale_after_seconds: int = DEFAULT_STALE_AFTER_SECONDS,
    ) -> None:
        self.owner = owner
        self.lock_path = lock_path
        self.stale_after_seconds = stale_after_seconds
        self._payload = _lock_payload(owner, stale_after_seconds)
        self._acquired = False

    def __enter__(self) -> "AutomationLock":
        self.acquire()
        return self

    def __exit__(self, _exc_type, _exc, _tb) -> None:
        self.release()

    def acquire(self) -> None:
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        for _attempt in range(2):
            try:
                fd = os.open(str(self.lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError:
                current = _read_lock(self.lock_path)
                reason = stale_lock_reason(current, self.stale_after_seconds)
                if reason:
                    self.lock_path.unlink(missing_ok=True)
                    continue
                owner = current.get("owner", "unknown")
                pid = current.get("pid", "unknown")
                started = current.get("started_at", "unknown")
                raise AutomationLockError(f"Shared automation lock is held by {owner} pid={pid} started_at={started}")
            else:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(self._payload, handle, indent=2, sort_keys=True)
                    handle.write("\n")
                self._acquired = True
                return
        raise AutomationLockError(f"Could not acquire shared automation lock at {self.lock_path}")

    def release(self) -> None:
        if not self._acquired:
            return
        current = _read_lock(self.lock_path)
        if current.get("pid") == self._payload["pid"] and current.get("owner") == self.owner:
            self.lock_path.unlink(missing_ok=True)
        self._acquired = False


def git_status_lines() -> list[str]:
    result = run_command(["git", "status", "--porcelain=v1", "--untracked-files=all"])
    return [line for line in result.stdout.splitlines() if line.strip()]


def git_status_paths(line: str) -> list[str]:
    raw = line[3:].strip()
    if " -> " in raw:
        parts = raw.split(" -> ")
    else:
        parts = [raw]
    return [part.strip().strip('"').replace("\\", "/") for part in parts if part.strip()]


def split_git_status_by_prefix(lines: Iterable[str], allowed_prefixes: Iterable[str]) -> tuple[list[str], list[str]]:
    prefixes = tuple(prefix.replace("\\", "/").rstrip("/") + "/" for prefix in allowed_prefixes)
    allowed: list[str] = []
    blocked: list[str] = []
    for line in lines:
        paths = git_status_paths(line)
        if paths and all(path.startswith(prefixes) for path in paths):
            allowed.append(line)
        else:
            blocked.append(line)
    return allowed, blocked


def paths_are_site_only(paths: Iterable[str], site_dir_name: str = "site") -> bool:
    prefix = site_dir_name.rstrip("/\\") + "/"
    return all(path.replace("\\", "/").startswith(prefix) for path in paths)


def write_json_and_markdown_status(json_path: Path, markdown_path: Path, status: dict[str, object]) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    lines = [
        "# Post-Unicorn Atlas Publish Status",
        "",
        f"- Status: {status.get('status', 'unknown')}",
        f"- Publish ID: {status.get('publish_id', '')}",
        f"- Generated at: {status.get('generated_at', '')}",
        f"- Source head SHA: {status.get('source_head_sha', '')}",
        f"- Live URL: {status.get('live_url', '')}",
        f"- Entity count: {status.get('entity_count', '')}",
        f"- Claim count: {status.get('claim_count', '')}",
        f"- Paper-ready claims: {status.get('paper_ready_count', '')}",
    ]
    if status.get("warnings"):
        lines.extend(["", "## Warnings"])
        for warning in status["warnings"]:  # type: ignore[index]
            lines.append(f"- {warning}")
    if status.get("error"):
        lines.extend(["", "## Error", "", str(status["error"])])
    markdown_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def check_packet_sizes(
    site_dir: Path,
    *,
    warn_html_bytes: int = 2_000_000,
    max_html_bytes: int = 5_000_000,
    max_csv_bytes: int = 20_000_000,
    warn_pdf_bytes: int = 15_000_000,
    max_pdf_bytes: int = 50_000_000,
) -> list[str]:
    warnings: list[str] = []
    html_path = site_dir / "index.html"
    csv_path = site_dir / "post_unicorn_industry_atlas_entities_claims.csv"
    pdf_path = site_dir / "post_unicorn_industry_atlas_packet.pdf"
    if not html_path.exists():
        raise PacketValidationError(f"missing packet HTML: {html_path}")
    if not csv_path.exists():
        raise PacketValidationError(f"missing packet CSV: {csv_path}")
    if not pdf_path.exists():
        raise PacketValidationError(f"missing packet PDF: {pdf_path}")
    html_size = html_path.stat().st_size
    csv_size = csv_path.stat().st_size
    pdf_size = pdf_path.stat().st_size
    if html_size > max_html_bytes:
        raise PacketValidationError(f"packet HTML too large: {html_size} bytes > {max_html_bytes}")
    if csv_size > max_csv_bytes:
        raise PacketValidationError(f"packet CSV too large: {csv_size} bytes > {max_csv_bytes}")
    if pdf_size > max_pdf_bytes:
        raise PacketValidationError(f"packet PDF too large: {pdf_size} bytes > {max_pdf_bytes}")
    if html_size > warn_html_bytes:
        warnings.append(f"packet HTML is large: {html_size} bytes > warning threshold {warn_html_bytes}")
    if pdf_size > warn_pdf_bytes:
        warnings.append(f"packet PDF is large: {pdf_size} bytes > warning threshold {warn_pdf_bytes}")
    return warnings
