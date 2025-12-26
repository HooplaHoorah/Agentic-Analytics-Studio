#!/usr/bin/env bash
set -euo pipefail
ROOT="$(python3 instructions12/tools/find_repo_root.py 2>/dev/null || python instructions12/tools/find_repo_root.py)"
cd "$ROOT"
python instructions12/tools/demo_runner.py --mode execute
echo ""
echo "Send back: instructions12/out/demo_report.md"
