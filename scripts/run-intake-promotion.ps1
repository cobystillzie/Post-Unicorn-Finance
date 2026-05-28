$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
python scripts\research_agents.py promotion-loop --limit 100
python scripts\validate_evidence.py
python scripts\atlas_sqlite.py validate --strict-verified-sources
python -m pytest -q
