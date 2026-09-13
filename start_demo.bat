@echo off
setlocal
cd /d "%~dp0"

where py >nul 2>&1
if %errorlevel% equ 0 (
  set "PYTHON_CMD=py"
) else (
  set "PYTHON_CMD=python"
)

if not exist ".venv\Scripts\python.exe" (
  echo [ResiliChain] Creating the Python environment...
  %PYTHON_CMD% -m venv .venv || goto :error
)

echo [ResiliChain] Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt || goto :error

echo.
echo [ResiliChain] Dashboard: http://127.0.0.1:8080
echo [ResiliChain] Press Ctrl+C to stop the server.
echo.
".venv\Scripts\python.exe" -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8080
goto :eof

:error
echo.
echo ResiliChain could not start. Confirm that Python 3.11 or newer is installed.
pause
exit /b 1
