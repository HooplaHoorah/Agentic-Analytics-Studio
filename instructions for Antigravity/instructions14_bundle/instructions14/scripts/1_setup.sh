#!/usr/bin/env bash
set -euo pipefail
ROOT="$(python3 instructions14/tools/find_repo_root.py 2>/dev/null || python instructions14/tools/find_repo_root.py)"
cd "$ROOT"

if [ ! -d ".venv" ]; then
  python3 -m venv .venv || python -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install playwright slack_sdk tableauserverclient
python -m playwright install chromium
echo "Setup complete."
