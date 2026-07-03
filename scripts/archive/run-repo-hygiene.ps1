$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
# DISABLED 2026-06-23: Automatic discovery agents stopped per audit.
# This script previously ran repo hygiene audit.
# To re-enable: remove this exit and restore the python command below.
Write-Host "Post-Unicorn Repo Hygiene Audit DISABLED - automatic discovery stopped."
exit 0
# python scripts\repo_hygiene.py autonomous-cleanup --promotion-limit 10 --push
