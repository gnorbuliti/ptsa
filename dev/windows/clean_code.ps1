$ErrorActionPreference = "Stop"
$initialLocation = Get-Location

& "$PSScriptRoot\app_clean.ps1"
python -m isort .
python -m ruff check . --fix
python -m black .
& "$PSScriptRoot\app_clean.ps1"
Set-Location $initialLocation
return
