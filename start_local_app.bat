@echo off
setlocal
cd /d "%~dp0"

set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"
set "BUNDLED_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%VENV_PYTHON%" (
  set "PYTHON=%VENV_PYTHON%"
) else if exist "%BUNDLED_PYTHON%" (
  set "PYTHON=%BUNDLED_PYTHON%"
) else (
  set "PYTHON=python"
)

echo.
echo ProcureWise is starting...
echo Open: http://127.0.0.1:8502
echo Keep this window open while using the app.
echo.

"%PYTHON%" app\basic_server.py
