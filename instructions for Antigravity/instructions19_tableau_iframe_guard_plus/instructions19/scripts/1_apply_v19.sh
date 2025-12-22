\
    #!/usr/bin/env bash
    set -euo pipefail

    REPO_ROOT="$(pwd)"

    find_index() {
      local candidates=("web/index.html" "web/dist/index.html" "web/public/index.html" "index.html")
      for rel in "${candidates[@]}"; do
        if [[ -f "$REPO_ROOT/$rel" ]]; then
          echo "$REPO_ROOT/$rel"
          return 0
        fi
      done
      local hit
      hit="$(find "$REPO_ROOT" -maxdepth 4 -name index.html -type f 2>/dev/null | head -n 1 || true)"
      if [[ -n "$hit" ]]; then
        echo "$hit"
        return 0
      fi
      return 1
    }

    INDEX_PATH="$(find_index || true)"
    if [[ -z "${INDEX_PATH:-}" ]]; then
      echo "ERROR: Could not find index.html" >&2
      exit 1
    fi

    echo "Found index.html: $INDEX_PATH"

    if grep -q "AAS TABLEAU IFRAME GUARD+ v19" "$INDEX_PATH"; then
      echo "Guard v19 already installed. Nothing to do."
      exit 0
    fi

    GUARD_FILE="$REPO_ROOT/instructions19/guard_v19.html"
    if [[ ! -f "$GUARD_FILE" ]]; then
      echo "ERROR: Missing guard snippet at $GUARD_FILE" >&2
      exit 1
    fi

    if grep -q "</body>" "$INDEX_PATH"; then
      # insert before </body>
      perl -0777 -pe 's#</body>#`cat '"$GUARD_FILE"'`\n</body>#s' -i "$INDEX_PATH" || true
      # fallback if perl insert failed:
      if ! grep -q "AAS TABLEAU IFRAME GUARD+ v19" "$INDEX_PATH"; then
        tmp="$(mktemp)"
        awk -v guard="$(cat "$GUARD_FILE")" 'BEGIN{added=0} { if(!added && $0 ~ /<\/body>/){ print guard; added=1 } print }' "$INDEX_PATH" > "$tmp"
        mv "$tmp" "$INDEX_PATH"
      fi
    else
      cat "$GUARD_FILE" >> "$INDEX_PATH"
    fi

    echo "✅ Installed Guard v19. Hard refresh your browser to load it."
