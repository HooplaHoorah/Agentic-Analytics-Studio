#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

MARKER = "AAS_FILE_PROTOCOL_GUARD_V20"
SNIPPET = r"""<!-- AAS_FILE_PROTOCOL_GUARD_V20: BEGIN -->
<style>
  #aas-file-protocol-guard {
    position: fixed;
    top: 12px;
    left: 12px;
    right: 12px;
    z-index: 10000;
    display: none;
    padding: 12px 14px;
    border-radius: 14px;
    background: rgba(25, 30, 40, 0.94);
    color: #fff;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    box-shadow: 0 10px 28px rgba(0,0,0,0.28);
  }
  #aas-file-protocol-guard .row { display:flex; gap:12px; align-items:center; justify-content:space-between; flex-wrap:wrap; }
  #aas-file-protocol-guard .msg { font-size: 14px; line-height: 1.35; opacity: 0.96; }
  #aas-file-protocol-guard .btns { display:flex; gap:8px; }
  #aas-file-protocol-guard button { border:0; border-radius: 10px; padding: 8px 10px; font-size: 13px; cursor:pointer; }
  #aas-file-protocol-guard button.primary { background:#4c8dff; color:#fff; }
  #aas-file-protocol-guard button.secondary { background: rgba(255,255,255,0.12); color:#fff; }
  #aas-file-protocol-guard code { background: rgba(255,255,255,0.10); padding: 2px 6px; border-radius: 8px; }
</style>

<div id="aas-file-protocol-guard" role="alert">
  <div class="row">
    <div class="msg">
      <strong>Heads up:</strong> You opened this page via <code>file://</code>. That breaks fetch/CORS and Tableau embeds (origin becomes <code>null</code>).
      <br/>
      Please run the demo over HTTP (recommended: <code>http://localhost:5173/index.html</code>).
    </div>
    <div class="btns">
      <button id="aas-open-http" class="primary">Open HTTP demo</button>
      <button id="aas-dismiss-http" class="secondary">Dismiss</button>
    </div>
  </div>
</div>

<script>
(function(){
  const target = "http://localhost:5173/index.html";

  function show(){
    const el = document.getElementById("aas-file-protocol-guard");
    if (!el) return;
    el.style.display = "block";

    const open = document.getElementById("aas-open-http");
    const dismiss = document.getElementById("aas-dismiss-http");
    if (open) open.onclick = () => window.open(target, "_blank", "noopener,noreferrer");
    if (dismiss) dismiss.onclick = () => { el.style.display = "none"; };
  }

  if (window.location && window.location.protocol === "file:"){
    if (document.readyState === "loading"){
      document.addEventListener("DOMContentLoaded", show);
    } else {
      show();
    }
  }
})();
</script>
<!-- AAS_FILE_PROTOCOL_GUARD_V20: END -->"""

def find_repo_root(start: Path) -> Path:
    for p in [start] + list(start.parents):
        if (p / "aas" / "api.py").exists():
            return p
    raise SystemExit("Could not locate repo root containing aas/api.py")

def should_patch(html: str) -> bool:
    if "Agentic Analytics Studio" in html:
        return True
    low = html.lower()
    return ("tableau" in low) and ("<iframe" in low)

def patch_index(path: Path) -> bool:
    html = path.read_text(encoding="utf-8", errors="ignore")
    if MARKER in html:
        return False
    if not should_patch(html):
        return False

    low = html.lower()
    if "</body>" in low:
        idx = low.rfind("</body>")
        new_html = html[:idx] + "\n\n" + SNIPPET + "\n\n" + html[idx:]
    else:
        new_html = html + "\n\n" + SNIPPET + "\n"

    backup = path.with_suffix(path.suffix + ".bak_instructions20")
    if not backup.exists():
        backup.write_text(html, encoding="utf-8")
    path.write_text(new_html, encoding="utf-8")
    return True

def main() -> None:
    repo = find_repo_root(Path.cwd())
    skip_dirs = {"venv",".venv","node_modules",".git","__pycache__"}
    patched = []

    for p in repo.rglob("index.html"):
        if any(part in skip_dirs for part in p.parts):
            continue
        try:
            if patch_index(p):
                patched.append(str(p.relative_to(repo)))
        except Exception:
            continue

    if patched:
        print("[v20] Injected file:// guard into:")
        for x in patched:
            print("  -", x)
    else:
        print("[v20] No index.html patched (already patched or not found).")

if __name__ == "__main__":
    main()
