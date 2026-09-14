Set-Location (Split-Path -Parent (Split-Path -Parent $PSScriptRoot))

$excludedDirectories = @(
    '.venv'
    'venv'
    'env'
    'virtualenv'
)

$cacheDirectories = @(
    '__pycache__'
    '.pytest_cache'
    '.mypy_cache'
    '.ruff_cache'
    '.tox'
    '.nox'
)

$buildDirectories = @(
    'build'
    'dist'
)

function Test-IsExcludedPath {
    param (
        [string]$Path
    )

    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $parts = $fullPath -split '[\\/]'

    foreach ($excluded in $excludedDirectories) {
        if ($parts -contains $excluded) {
            return $true
        }
    }

    return $false
}

# Remove cache/build directories
Get-ChildItem -Path . -Recurse -Force -Directory -ErrorAction SilentlyContinue |
    Where-Object {
        (
            $cacheDirectories -contains $_.Name -or
            $buildDirectories -contains $_.Name -or
            $_.Name -like '*.egg-info' -or
            $_.Name -like '*.dist-info'
        ) -and
        -not (Test-IsExcludedPath $_.FullName)
    } |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Remove Python bytecode
Get-ChildItem -Path . -Recurse -Force -File -ErrorAction SilentlyContinue |
    Where-Object {
        $_.Extension -in @('.pyc', '.pyo', '.egg') -and
        -not (Test-IsExcludedPath $_.FullName)
    } |
    Remove-Item -Force -ErrorAction SilentlyContinue
