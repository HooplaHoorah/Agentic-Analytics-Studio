#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

TARGET_IFRAME_URL = "https://10ax.online.tableau.com/"
GOOD_EMBED_SCRIPT = "https://public.tableau.com/javascripts/api/tableau.embedding.3.latest.min.js"

def find_repo_root(start: Path) -> Path:
    for p in [start] + list(start.parents):
        if (p / "aas" / "api.py").exists():
            return p
    raise SystemExit("Could not locate repo root containing aas/api.py")

def patch_index_html(path: Path) -> bool:
    txt = path.read_text(encoding="utf-8", errors="ignore")

    # Only patch likely AAS demo pages
    if "Agentic Analytics Studio" not in txt and "AAS" not in txt:
        return False

    changed = False

    # 1) Fix bad default iframe src pointing at Tableau Cloud root.
    if TARGET_IFRAME_URL in txt:
        txt = txt.replace(TARGET_IFRAME_URL, "about:blank")
        changed = True

    # 2) Fix malformed Tableau Embedding API script src.
    if "tableau.embedding.3.latest.min.js" in txt and GOOD_EMBED_SCRIPT not in txt:
        txt2 = re.sub(
            r'src=["\']https?://[^"\']*tableau\.embedding\.3\.latest\.min\.js["\']',
            f'src="{GOOD_EMBED_SCRIPT}"',
            txt,
            flags=re.I,
        )
        txt2 = re.sub(
            r'src=["\']tableau\.embedding\.3\.latest\.min\.js["\']',
            f'src="{GOOD_EMBED_SCRIPT}"',
            txt2,
            flags=re.I,
        )
        if txt2 != txt:
            txt = txt2
            changed = True

    if changed:
        backup = path.with_suffix(path.suffix + ".bak_instructions17")
        if not backup.exists():
            backup.write_text(path.read_text(encoding="utf-8", errors="ignore"), encoding="utf-8")
        path.write_text(txt, encoding="utf-8")

    return changed

def main() -> None:
    repo = find_repo_root(Path.cwd())
    skip_dirs = {"venv", ".venv", "node_modules", ".git", "__pycache__"}
    patched = []

    for p in repo.rglob("index.html"):
        if any(part in skip_dirs for part in p.parts):
            continue
        try:
            if patch_index_html(p):
                patched.append(str(p.relative_to(repo)))
        except Exception:
            continue

    if patched:
        print("[patch_frontend] Patched index.html files:")
        for x in patched:
            print("  -", x)
    else:
        print("[patch_frontend] No matching index.html found (or already clean).")

if __name__ == "__main__":
    main()
