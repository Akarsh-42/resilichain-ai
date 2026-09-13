#!/usr/bin/env sh
set -eu

cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_CMD=python3
else
  PYTHON_CMD=python
fi

if [ ! -x .venv/bin/python ]; then
  echo "[ResiliChain] Creating the Python environment..."
  "$PYTHON_CMD" -m venv .venv
fi

echo "[ResiliChain] Installing dependencies..."
.venv/bin/python -m pip install -r requirements.txt

echo "[ResiliChain] Dashboard: http://127.0.0.1:8080"
echo "[ResiliChain] Press Ctrl+C to stop the server."
exec .venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8080
