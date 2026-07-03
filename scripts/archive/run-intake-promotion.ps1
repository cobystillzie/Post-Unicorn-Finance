$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
# DISABLED 2026-06-23: Automatic discovery agents stopped per audit.
# This script previously ran intake promotion loop.
# To re-enable: remove this exit and restore the python commands below.
Write-Host "Post-Unicorn Intake Promotion Loop DISABLED - automatic discovery stopped."
exit 0
# python scripts\research_agents.py promotion-loop --limit 100
# python scripts\validate_evidence.py
# python scripts\atlas_sqlite.py validate --strict-verified-sources
# python -m pytest -q
