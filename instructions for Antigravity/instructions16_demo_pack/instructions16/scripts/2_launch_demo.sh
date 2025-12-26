#!/usr/bin/env bash
set -euo pipefail
echo "== Launching AAS demo =="

ROOT="$(python3 ./tools/find_repo_root.py 2>/dev/null || python ./tools/find_repo_root.py)"
if [ -f "$ROOT/.env" ]; then
  while IFS= read -r line; do
    line="$(echo "$line" | sed -e 's/^\s*//;s/\s*$//')"
    [ -z "$line" ] && continue
    [[ "$line" == \#* ]] && continue
    [[ "$line" != *"="* ]] && continue
    key="${line%%=*}"; val="${line#*=}"
    key="$(echo "$key" | sed -e 's/^\s*//;s/\s*$//')"
    val="$(echo "$val" | sed -e 's/^\s*//;s/\s*$//' -e 's/^"//;s/"$//' -e "s/^'//;s/'$//")"
    export "$key=$val"
  done < "$ROOT/.env"
else
  echo "WARNING: .env not found in repo root. Real Mode may fail."
fi

python ./tools/launcher.py
