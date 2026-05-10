#!/bin/sh
cd "$(dirname "$0")" || exit 1

echo ""
echo "ProcureWise is starting..."
echo "Open: http://127.0.0.1:8502"
echo "Keep this Terminal window open while using the app."
echo ""

if command -v python3 >/dev/null 2>&1; then
  python3 app/basic_server.py
else
  python app/basic_server.py
fi

