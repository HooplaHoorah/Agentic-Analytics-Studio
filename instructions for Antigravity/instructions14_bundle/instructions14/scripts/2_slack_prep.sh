#!/usr/bin/env bash
set -euo pipefail
ROOT="$(python3 instructions14/tools/find_repo_root.py 2>/dev/null || python instructions14/tools/find_repo_root.py)"
cd "$ROOT"

if [ -f ".env" ]; then
  while IFS= read -r line; do
    line="$(echo "$line" | sed -e 's/^\s*//;s/\s*$//')"
    [ -z "$line" ] && continue
    [[ "$line" == \#* ]] && continue
    [[ "$line" != *"="* ]] && continue
    key="${line%%=*}"; val="${line#*=}"
    key="$(echo "$key" | sed -e 's/^\s*//;s/\s*$//')"
    val="$(echo "$val" | sed -e 's/^\s*//;s/\s*$//' -e 's/^"//;s/"$//' -e "s/^'//;s/'$//")"
    export "$key=$val"
  done < .env
fi

python instructions14/tools/slack_prep.py
echo ""
echo "Send back: instructions14/out/slack_prep.md"
