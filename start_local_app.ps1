$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (Test-Path $BundledPython) {
    $Python = $BundledPython
} else {
    $Python = "python"
}

Write-Host ""
Write-Host "ProcureWise is starting..."
Write-Host "Open: http://127.0.0.1:8502"
Write-Host "Keep this PowerShell window open while using the app."
Write-Host ""

& $Python "app\basic_server.py"

