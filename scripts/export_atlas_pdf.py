"""Render the shareable atlas HTML packet to an attachment-friendly PDF."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_HTML = ROOT / "site" / "post_unicorn_industry_atlas_packet.html"
DEFAULT_PDF = ROOT / "site" / "post_unicorn_industry_atlas_packet.pdf"


class PdfExportError(RuntimeError):
    """Raised when the atlas PDF cannot be generated or validated."""


def browser_candidates() -> list[Path]:
    candidates: list[Path] = []
    for env_name in ("POST_UNICORN_CHROME_PATH", "CHROME_PATH", "PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH"):
        value = os.environ.get(env_name)
        if value:
            candidates.append(Path(value))

    for command in ("chrome", "chrome.exe", "google-chrome", "chromium", "chromium-browser", "msedge", "msedge.exe"):
        resolved = shutil.which(command)
        if resolved:
            candidates.append(Path(resolved))

    if os.name == "nt":
        env = os.environ
        candidates.extend(
            [
                Path(env.get("PROGRAMFILES", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
                Path(env.get("PROGRAMFILES(X86)", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
                Path(env.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
                Path(env.get("PROGRAMFILES", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
                Path(env.get("PROGRAMFILES(X86)", "")) / "Microsoft" / "Edge" / "Application" / "msedge.exe",
            ]
        )

    seen: set[Path] = set()
    existing: list[Path] = []
    for candidate in candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        if candidate.exists():
            existing.append(candidate)
    return existing


def find_browser(explicit_path: Path | None = None) -> Path:
    if explicit_path:
        if explicit_path.exists():
            return explicit_path
        raise PdfExportError(f"browser path does not exist: {explicit_path}")

    candidates = browser_candidates()
    if candidates:
        return candidates[0]
    raise PdfExportError(
        "could not find Chrome, Chromium, or Edge for PDF export. "
        "Set POST_UNICORN_CHROME_PATH to the browser executable."
    )


def validate_pdf(pdf_path: Path, *, min_bytes: int = 10_000) -> None:
    if not pdf_path.exists():
        raise PdfExportError(f"PDF was not created: {pdf_path}")
    if pdf_path.stat().st_size < min_bytes:
        raise PdfExportError(f"PDF is too small to be a usable atlas packet: {pdf_path.stat().st_size} bytes")
    with pdf_path.open("rb") as handle:
        header = handle.read(5)
    if header != b"%PDF-":
        raise PdfExportError(f"PDF header is invalid for {pdf_path}")


def render_pdf(html_path: Path, pdf_path: Path, *, browser_path: Path | None = None) -> Path:
    html_path = html_path.resolve()
    pdf_path = pdf_path.resolve()
    if not html_path.exists():
        raise PdfExportError(f"HTML packet does not exist: {html_path}")

    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    if pdf_path.exists():
        pdf_path.unlink()

    browser = find_browser(browser_path)
    command = [
        str(browser),
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--run-all-compositor-stages-before-draw",
        "--virtual-time-budget=3000",
        "--print-to-pdf-no-header",
        f"--print-to-pdf={pdf_path}",
        html_path.as_uri(),
    ]
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    if result.returncode != 0:
        raise PdfExportError(
            "browser PDF export failed\n"
            f"command: {' '.join(command)}\n"
            f"stdout: {result.stdout[-1200:]}\n"
            f"stderr: {result.stderr[-1200:]}"
        )
    validate_pdf(pdf_path)
    return pdf_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the Post-Unicorn Finance atlas HTML packet to PDF.")
    parser.add_argument("--html", type=Path, default=DEFAULT_HTML)
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    parser.add_argument("--browser", type=Path, default=None)
    args = parser.parse_args()

    try:
        pdf_path = render_pdf(args.html, args.pdf, browser_path=args.browser)
    except PdfExportError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Wrote atlas PDF: {pdf_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
