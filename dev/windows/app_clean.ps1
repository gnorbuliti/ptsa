Set-Location (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))

$cacheDirectories = @(
	'__pycache__'
	'.pytest_cache'
	'.mypy_cache'
	'.ruff_cache'
)

foreach ($cacheDirectory in $cacheDirectories) {
	Get-ChildItem -Path . -Recurse -Force -Directory -Filter $cacheDirectory -ErrorAction SilentlyContinue |
		Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}

Get-ChildItem -Path . -Recurse -Force -File -Include '*.pyc', '*.pyo' -ErrorAction SilentlyContinue |
	Remove-Item -Force -ErrorAction SilentlyContinue
