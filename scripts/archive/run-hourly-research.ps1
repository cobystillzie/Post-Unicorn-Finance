$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
# DISABLED 2026-06-23: Automatic discovery agents stopped per audit.
# This script previously ran hourly research loop with web discovery.
# To re-enable: remove this exit and restore the python commands below.
Write-Host "Post-Unicorn Hourly Research Loop DISABLED - automatic discovery stopped."
exit 0
# python scripts\research_agents.py hourly-loop --fetch-limit 60 --web-discovery --web-results-per-target 12 --web-max-new-leads 80
# python scripts\atlas_sqlite.py validate --strict-verified-sources
# python scripts\export_shareable_atlas.py
