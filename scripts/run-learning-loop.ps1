$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
python scripts\learning_ops.py learning-loop --review-limit 250
python scripts\validate_evidence.py
python scripts\atlas_sqlite.py validate --strict-verified-sources
python -m pytest -q
