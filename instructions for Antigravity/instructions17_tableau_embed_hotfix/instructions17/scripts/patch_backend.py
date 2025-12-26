#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

def find_repo_root(start: Path) -> Path:
    for p in [start] + list(start.parents):
        if (p / "aas" / "api.py").exists():
            return p
    raise SystemExit("Could not locate repo root containing aas/api.py")

def patch_api_py(api_path: Path) -> bool:
    txt = api_path.read_text(encoding="utf-8")
    changed = False

    # 1) Ensure urllib.parse.quote import exists
    if "from urllib.parse import quote" not in txt:
        m = re.search(r"^from typing[^\n]*\n", txt, flags=re.M)
        if m:
            insert_at = m.end()
            txt = txt[:insert_at] + "from urllib.parse import quote\n" + txt[insert_at:]
        else:
            m2 = re.search(r"^from __future__ import[^\n]*\n", txt, flags=re.M)
            insert_at = m2.end() if m2 else 0
            txt = txt[:insert_at] + "from urllib.parse import quote\n" + txt[insert_at:]
        changed = True

    # 2) Ensure helper exists
    helper_name = "_build_tableau_embed_url"
    if helper_name not in txt:
        helper_code = (
            "def _build_tableau_embed_url(server_url: str, site_id: str, content_url: str) -> str:\n"
            "    # Build a Tableau Cloud/Server embed URL for a view.\n"
            "    # Canonical: https://<server>/t/<site>/views/<workbook>/<view>?:showVizHome=no&:embed=yes\n"
            "    base = (server_url or '').rstrip('/')\n"
            "    safe_content = '/'.join(quote(part) for part in (content_url or '').lstrip('/').split('/'))\n"
            "    if site_id:\n"
            "        return f\"{base}/t/{site_id}/views/{safe_content}?:showVizHome=no&:embed=yes\"\n"
            "    return f\"{base}/views/{safe_content}?:showVizHome=no&:embed=yes\"\n"
        )
        anchor = '@app.get("/tableau/views")'
        idx = txt.find(anchor)
        if idx != -1:
            txt = txt[:idx] + helper_code + "\n\n" + txt[idx:]
        else:
            txt = txt.rstrip() + "\n\n" + helper_code + "\n"
        changed = True

    # 3) Add embed_url into the /tableau/views response dict (if not already there)
    if '"embed_url"' not in txt:
        txt2, n = re.subn(
            r'"content_url"\s*:\s*v\.content_url\s*\n\s*\}\)',
            '"content_url": v.content_url,\n                "embed_url": _build_tableau_embed_url(server_url, site_id, v.content_url)\n            })',
            txt,
            count=1,
        )
        if n:
            txt = txt2
            changed = True

    if changed:
        backup = api_path.with_suffix(".py.bak_instructions17")
        if not backup.exists():
            backup.write_text(api_path.read_text(encoding="utf-8"), encoding="utf-8")
        api_path.write_text(txt, encoding="utf-8")

    return changed

def main() -> None:
    repo = find_repo_root(Path.cwd())
    api_path = repo / "aas" / "api.py"
    if not api_path.exists():
        raise SystemExit(f"Missing: {api_path}")
    changed = patch_api_py(api_path)
    print(f"[patch_backend] Patched {api_path}: {'YES' if changed else 'NO (already patched)'}")

if __name__ == "__main__":
    main()
