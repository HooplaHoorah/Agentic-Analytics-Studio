#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

MARKER = "AAS_TABLEAU_GUARD_V18"
SNIPPET = r"""<!-- AAS_TABLEAU_GUARD_V18: BEGIN -->
<style>
  #aas-tableau-banner {
    position: absolute;
    top: 10px;
    left: 10px;
    right: 10px;
    z-index: 9999;
    display: none;
    padding: 12px 14px;
    border-radius: 12px;
    background: rgba(25, 30, 40, 0.92);
    color: #fff;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif;
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
  }
  #aas-tableau-banner .row {
    display: flex;
    gap: 10px;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
  }
  #aas-tableau-banner .msg {
    line-height: 1.3;
    font-size: 14px;
    opacity: 0.95;
  }
  #aas-tableau-banner .btns { display: flex; gap: 8px; }
  #aas-tableau-banner button {
    border: 0;
    border-radius: 10px;
    padding: 8px 10px;
    font-size: 13px;
    cursor: pointer;
  }
  #aas-tableau-banner button.primary { background: #4c8dff; color: #fff; }
  #aas-tableau-banner button.secondary { background: rgba(255,255,255,0.12); color: #fff; }
  #aas-tableau-banner button.ghost { background: transparent; color: rgba(255,255,255,0.85); }
</style>

<div id="aas-tableau-banner" role="alert">
  <div class="row">
    <div class="msg">
      <strong>Tableau didn’t finish loading.</strong>
      Your Tableau session may have expired. Click <b>Open in new tab</b> to sign in, then come back and hit <b>Retry</b>.
    </div>
    <div class="btns">
      <button id="aas-tableau-open" class="primary">Open in new tab</button>
      <button id="aas-tableau-retry" class="secondary">Retry</button>
      <button id="aas-tableau-dismiss" class="ghost">Dismiss</button>
    </div>
  </div>
</div>

<script>
(function(){
  const LOAD_TIMEOUT_MS = 8000;

  function isLikelyLogin(url){
    if(!url) return false;
    const u = String(url).toLowerCase();
    return u.includes("/signin") || u.includes("/login") || u.includes("auth") || u.includes("sso");
  }

  function findTableauIframe(){
    const iframes = Array.from(document.querySelectorAll("iframe"));
    const bySrc = iframes.find(f => (f.getAttribute("src") || "").includes("tableau"));
    if (bySrc) return bySrc;

    const container = document.querySelector("#tableau, #tableau-container, #dashboard, .dashboard, .insight, .insight-dashboard");
    if (container){
      const f = container.querySelector("iframe");
      if (f) return f;
    }
    return iframes[0] || null;
  }

  function ensureBannerParent(){
    const frame = findTableauIframe();
    const banner = document.getElementById("aas-tableau-banner");
    if (!banner) return null;

    let parent = frame ? frame.parentElement : document.body;
    if (!parent) parent = document.body;

    const style = window.getComputedStyle(parent);
    if (style.position === "static"){
      parent.style.position = "relative";
    }
    if (!banner.parentElement || banner.parentElement !== parent){
      parent.appendChild(banner);
    }
    return frame;
  }

  function showBanner(openUrl, retryFn){
    const banner = document.getElementById("aas-tableau-banner");
    if (!banner) return;
    banner.style.display = "block";

    const openBtn = document.getElementById("aas-tableau-open");
    const retryBtn = document.getElementById("aas-tableau-retry");
    const dismissBtn = document.getElementById("aas-tableau-dismiss");

    if (openBtn){
      openBtn.onclick = () => { if (openUrl) window.open(openUrl, "_blank", "noopener,noreferrer"); };
    }
    if (retryBtn){
      retryBtn.onclick = () => { if (retryFn) retryFn(); };
    }
    if (dismissBtn){
      dismissBtn.onclick = () => { banner.style.display = "none"; };
    }
  }

  function hideBanner(){
    const banner = document.getElementById("aas-tableau-banner");
    if (!banner) return;
    banner.style.display = "none";
  }

  function attachGuard(){
    const frame = ensureBannerParent();
    if (!frame) return;

    let timer = null;
    let lastSrc = frame.getAttribute("src") || "";

    function startLoadGuard(src){
      hideBanner();
      if (timer) { clearTimeout(timer); timer = null; }

      if (isLikelyLogin(src)){
        showBanner(src, () => { frame.setAttribute("src", src); startLoadGuard(src); });
        return;
      }

      timer = setTimeout(() => {
        showBanner(src, () => { frame.setAttribute("src", src); startLoadGuard(src); });
      }, LOAD_TIMEOUT_MS);
    }

    frame.addEventListener("load", () => {
      if (timer) { clearTimeout(timer); timer = null; }
      hideBanner();
    }, { passive: true });

    frame.addEventListener("error", () => {
      if (timer) { clearTimeout(timer); timer = null; }
      const src = frame.getAttribute("src") || "";
      showBanner(src, () => { frame.setAttribute("src", src); startLoadGuard(src); });
    }, { passive: true });

    const obs = new MutationObserver(() => {
      const src = frame.getAttribute("src") || "";
      if (src && src !== lastSrc){
        lastSrc = src;
        startLoadGuard(src);
      }
    });
    obs.observe(frame, { attributes: true, attributeFilter: ["src"] });

    if (lastSrc){
      startLoadGuard(lastSrc);
    }
  }

  if (document.readyState === "loading"){
    document.addEventListener("DOMContentLoaded", attachGuard);
  } else {
    attachGuard();
  }
})();
</script>
<!-- AAS_TABLEAU_GUARD_V18: END -->"""

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

    backup = path.with_suffix(path.suffix + ".bak_instructions18")
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
        print("[v18] Injected Tableau guard/banner into:")
        for x in patched:
            print("  -", x)
    else:
        print("[v18] No index.html patched (already patched or not found).")

if __name__ == "__main__":
    main()
