$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
python scripts\repo_hygiene.py autonomous-cleanup --promotion-limit 10 --push
