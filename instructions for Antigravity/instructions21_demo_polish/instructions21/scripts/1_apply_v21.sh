#!/usr/bin/env bash
set -euo pipefail

find_root() {
  local p="$PWD"
  while true; do
    if [[ -f "$p/aas/api.py" ]]; then
      echo "$p"
      return
    fi
    if [[ "$p" == "/" ]]; then
      echo "Could not find repo root (missing aas/api.py) from $PWD" >&2
      exit 1
    fi
    p="$(dirname "$p")"
  done
}

repo="$(find_root)"
echo "Repo root: $repo"
cd "$repo"

python instructions21/scripts/patch_index_html_v21.py
echo "✅ v21 applied. Hard refresh the browser (Ctrl+Shift+R) before recording."
