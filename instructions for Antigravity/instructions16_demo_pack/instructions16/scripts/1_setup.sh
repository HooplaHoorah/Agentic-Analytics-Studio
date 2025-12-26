#!/usr/bin/env bash
set -euo pipefail
echo "== Instructions16 setup =="
python -m pip install --upgrade pip
python -m pip install -r ../requirements.txt
python -m pip install playwright python-dotenv || true
python -m playwright install chromium || true
echo "Setup complete."
