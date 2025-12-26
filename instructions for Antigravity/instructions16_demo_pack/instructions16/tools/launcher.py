#!/usr/bin/env python3
from __future__ import annotations

import os, sys, time, signal, subprocess, webbrowser
from pathlib import Path
from typing import Optional

def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(12):
        if (cur / "aas" / "api.py").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise RuntimeError("Could not find repo root from " + str(start))

def wait_url(url: str, timeout_s: int = 25) -> bool:
    import urllib.request
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.7)
    return False

def start_api(root: Path, port: int, log_path: Path) -> Optional[subprocess.Popen]:
    # if already up, don't start
    if wait_url(f"http://127.0.0.1:{port}/health", timeout_s=2):
        return None
    cmd = [sys.executable, "-m", "uvicorn", "aas.api:app", "--host", "127.0.0.1", "--port", str(port)]
    log_f = log_path.open("w", encoding="utf-8")
    return subprocess.Popen(cmd, cwd=str(root), stdout=log_f, stderr=subprocess.STDOUT, env=os.environ.copy())

def start_web(root: Path, port: int, log_path: Path) -> Optional[subprocess.Popen]:
    web_dir = root / "web"
    if not web_dir.exists():
        return None
    if wait_url(f"http://127.0.0.1:{port}/", timeout_s=2):
        return None
    cmd = [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"]
    log_f = log_path.open("w", encoding="utf-8")
    return subprocess.Popen(cmd, cwd=str(web_dir), stdout=log_f, stderr=subprocess.STDOUT, env=os.environ.copy())

def stop(p: Optional[subprocess.Popen]):
    if not p:
        return
    try:
        if os.name == "nt":
            p.terminate()
        else:
            p.send_signal(signal.SIGTERM)
        p.wait(timeout=5)
    except Exception:
        try:
            p.kill()
        except Exception:
            pass

def main() -> int:
    here = Path(__file__).resolve()
    root = find_repo_root(here)
    api_port = int(os.getenv("AAS_API_PORT", "8000"))
    web_port = int(os.getenv("AAS_WEB_PORT", "5173"))
    url = f"http://localhost:{web_port}/index.html"

    out_dir = root / "instructions16" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    api_log = out_dir / "demo_api.log"
    web_log = out_dir / "demo_web.log"

    api_p = start_api(root, api_port, api_log)
    web_p = start_web(root, web_port, web_log)

    ok_api = wait_url(f"http://127.0.0.1:{api_port}/health", timeout_s=30)
    ok_web = wait_url(f"http://127.0.0.1:{web_port}/", timeout_s=15)

    print(f"API: {'OK' if ok_api else 'NOT READY'}  http://127.0.0.1:{api_port}")
    print(f"WEB: {'OK' if ok_web else 'NOT READY'}  {url}")
    if ok_web:
        webbrowser.open(url)

    print("\nPress Ctrl+C to stop (or close this window if you started servers elsewhere).")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        stop(web_p)
        stop(api_p)
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
