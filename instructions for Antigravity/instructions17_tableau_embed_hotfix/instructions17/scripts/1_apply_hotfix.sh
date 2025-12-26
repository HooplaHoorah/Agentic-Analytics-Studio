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

python instructions17/scripts/patch_backend.py
python instructions17/scripts/patch_frontend.py

echo "✅ Instructions17 hotfix applied."
echo "Next:"
echo "  1) Restart backend"
echo "  2) Open http://127.0.0.1:8000/tableau/views and confirm embed_url is present"
echo "  3) Reload demo UI"
