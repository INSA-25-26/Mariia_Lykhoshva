$env:PYTHONPATH = ".\"

$venvPython = ".\.venv\Scripts\python.exe"
if (Test-Path $venvPython) {
	& $venvPython -m pytest tests/ -v
}
else {
	python -m pytest tests/ -v
}
