#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

MARKER = "AAS_DEMO_POLISH_V21"
SNIPPET = r"""<!-- AAS_DEMO_POLISH_V21: BEGIN -->
<script>
(function(){
  // 1) Wrap buildDomTree if it exists / appears later (prevents cross-origin iframe throws).
  function wrapBuildDomTree(fn){
    if (fn && fn.__aasWrapped) return fn;
    const wrapped = function(){
      try { return fn.apply(this, arguments); }
      catch (e) { return null; }
    };
    wrapped.__aasWrapped = true;
    return wrapped;
  }

  if (typeof window.buildDomTree === "function"){
    window.buildDomTree = wrapBuildDomTree(window.buildDomTree);
  } else {
    const start = Date.now();
    const t = setInterval(() => {
      if (typeof window.buildDomTree === "function"){
        window.buildDomTree = wrapBuildDomTree(window.buildDomTree);
        clearInterval(t);
      } else if (Date.now() - start > 8000){
        clearInterval(t);
      }
    }, 250);
  }

  // 2) Console sanitizer (filters known-benign cross-origin/noise strings only).
  const NOISE = [
    "Failed to read a named property 'document' from 'Window'",
    "Blocked a frame with origin",
    "Refused to display",
    "X-Frame-Options",
    "Failed to execute 'postMessage' on 'DOMWindow'",
    "origin 'null'"
  ];

  function isNoise(msg){
    if (!msg) return false;
    const s = String(msg);
    return NOISE.some(n => s.includes(n));
  }

  const origError = console.error.bind(console);
  const origWarn  = console.warn.bind(console);

  console.error = function(){
    try {
      if (arguments && arguments.length && isNoise(arguments[0])) return;
    } catch(e) {}
    return origError.apply(console, arguments);
  };

  console.warn = function(){
    try {
      if (arguments && arguments.length && isNoise(arguments[0])) return;
    } catch(e) {}
    return origWarn.apply(console, arguments);
  };

  window.addEventListener("error", function(ev){
    try {
      const msg = ev && (ev.message || ev.error);
      if (isNoise(msg)) {
        ev.preventDefault && ev.preventDefault();
        return false;
      }
    } catch(e) {}
  }, true);
})();
</script>

<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='14' fill='%234c8dff'/%3E%3Ctext x='32' y='42' font-size='34' text-anchor='middle' fill='white' font-family='Arial,Helvetica,sans-serif'%3EA%3C/text%3E%3C/svg%3E">
<!-- AAS_DEMO_POLISH_V21: END -->"""

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
    if "</head>" in low:
        idx = low.rfind("</head>")
        new_html = html[:idx] + "\n\n" + SNIPPET + "\n\n" + html[idx:]
    elif "</body>" in low:
        idx = low.rfind("</body>")
        new_html = html[:idx] + "\n\n" + SNIPPET + "\n\n" + html[idx:]
    else:
        new_html = html + "\n\n" + SNIPPET + "\n"

    backup = path.with_suffix(path.suffix + ".bak_instructions21")
    if not backup.exists():
        backup.write_text(html, encoding="utf-8")
    path.write_text(new_html, encoding="utf-8")
    return True

def main() -> None:
    repo = find_repo_root(Path.cwd())
    skip_dirs = ('venv', '.venv', 'node_modules', '.git', '__pycache__')
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
        print("[v21] Injected demo polish into:")
        for x in patched:
            print("  -", x)
    else:
        print("[v21] No index.html patched (already patched or not found).")

if __name__ == "__main__":
    main()
