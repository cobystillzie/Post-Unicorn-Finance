$ErrorActionPreference = "Stop"
$repo = Split-Path -Parent $PSScriptRoot
Set-Location $repo
# DISABLED 2026-06-23: Automatic discovery agents stopped per audit.
# This script previously ran daily atlas packet publisher.
# To re-enable: remove this exit and restore the python command below.
Write-Host "Post-Unicorn Daily Packet Publisher DISABLED - automatic discovery stopped."
exit 0
# python scripts\publish_atlas_packet.py --poll-live
