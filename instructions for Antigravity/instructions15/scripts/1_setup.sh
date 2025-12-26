#!/usr/bin/env bash
set -euo pipefail
echo "== Instructions15 setup =="
python -m pip install --upgrade pip
python -m pip install -r ../requirements.txt
python -m pip install -r ../instructions15/requirements.txt
echo "OK"
