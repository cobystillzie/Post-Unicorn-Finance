$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
# Tuned 2026-05-28 for continuous week-long discovery (was --fetch-limit 5 / web 3/15).
# Rate-limit jitter inside web_search_results keeps DDG happy at higher volumes.
python scripts\research_agents.py hourly-loop --fetch-limit 60 --web-discovery --web-results-per-target 12 --web-max-new-leads 80
python scripts\atlas_sqlite.py validate --strict-verified-sources
python scripts\export_shareable_atlas.py
