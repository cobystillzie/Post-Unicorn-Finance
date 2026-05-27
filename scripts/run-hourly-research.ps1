$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
python scripts\research_agents.py hourly-loop --fetch-limit 5 --web-discovery --web-results-per-target 3 --web-max-new-leads 15
python scripts\atlas_sqlite.py validate --strict-verified-sources
python scripts\export_shareable_atlas.py
