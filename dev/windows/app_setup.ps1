if (Test-Path Function:\deactivate) {
	deactivate
}

if (-not (Test-Path .\venv)) {
	python -m venv venv
}

.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install ".[dev]"