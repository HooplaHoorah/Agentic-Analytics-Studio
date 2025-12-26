#!/usr/bin/env python3
import json
import os
import re
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from env_utils import parse_env, redact

KEYS = [
  "TABLEAU_SERVER_URL","TABLEAU_SITE_ID","TABLEAU_TOKEN_NAME","TABLEAU_TOKEN_SECRET",
  "SLACK_BOT_TOKEN","AAS_SLACK_TEST_CHANNEL","AAS_WEB_PORT","AAS_API_PORT"
]

def locate_root(start: Path) -> Path:
    def is_root(p: Path) -> bool:
        return (p / "aas").exists() and (p / "requirements.txt").exists()
    for p in [start] + list(start.parents):
        if is_root(p):
            return p
    for p in [Path.cwd().resolve()] + list(Path.cwd().resolve().parents):
        if is_root(p):
            return p
    raise RuntimeError("Could not locate repo root")

def http_json(url: str, method: str = "GET", payload: Optional[dict] = None, timeout_s: int = 20) -> Dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return {"ok": True, "status": resp.status, "json": json.loads(body)}
            except Exception:
                return {"ok": True, "status": resp.status, "raw": body}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": e.code, "error": "HTTPError", "raw": body}
    except Exception as e:
        return {"ok": False, "status": None, "error": type(e).__name__, "message": str(e)}

def wait_for_ok(url: str, timeout_s: int = 30) -> bool:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        r = http_json(url, timeout_s=5)
        if r.get("ok"):
            return True
        time.sleep(0.75)
    return False

def start_uvicorn(root: Path, api_port: int) -> Optional[subprocess.Popen]:
    if wait_for_ok(f"http://127.0.0.1:{api_port}/health", timeout_s=2):
        return None
    cmd = [sys.executable, "-m", "uvicorn", "aas.api:app", "--host", "127.0.0.1", "--port", str(api_port)]
    return subprocess.Popen(cmd, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def start_web_server(root: Path, web_port: int) -> Optional[subprocess.Popen]:
    web_dir = root / "web"
    if not web_dir.exists():
        return None
    if wait_for_ok(f"http://127.0.0.1:{web_port}/", timeout_s=2):
        return None
    cmd = [sys.executable, "-m", "http.server", str(web_port), "--bind", "127.0.0.1"]
    return subprocess.Popen(cmd, cwd=str(web_dir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def stop_proc(p: Optional[subprocess.Popen]):
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

def slack_find_channel_id(token: str, channel_name: str) -> Optional[str]:
    if not token:
        return None
    name = channel_name.lstrip("#")
    try:
        from slack_sdk import WebClient  # type: ignore
        client = WebClient(token=token)
        cursor = None
        for _ in range(6):
            resp = client.conversations_list(limit=200, cursor=cursor, types="public_channel,private_channel")
            for c in resp.get("channels", []):
                if c.get("name") == name:
                    return c.get("id")
            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
    except Exception:
        return None
    return None

def slack_verify_marker(token: str, channel_id: str, marker: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"attempted": False, "found": False, "checked_messages": 0}
    if not token or not channel_id:
        out["reason"] = "missing_token_or_channel_id"
        return out
    try:
        from slack_sdk import WebClient  # type: ignore
        client = WebClient(token=token)
        out["attempted"] = True
        hist = client.conversations_history(channel=channel_id, limit=30)
        msgs = hist.get("messages", [])
        out["checked_messages"] = len(msgs)
        out["found"] = any(marker in (m.get("text") or "") for m in msgs)
        return out
    except Exception as e:
        out["error"] = type(e).__name__
        out["message"] = str(e)
        return out

def run_playwright(web_url: str, screens_dir: Path) -> Dict[str, Any]:
    res: Dict[str, Any] = {"ran": False, "steps": [], "errors": []}
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as e:
        res["errors"].append(f"playwright_import_failed: {type(e).__name__}: {e}")
        return res

    screens_dir.mkdir(parents=True, exist_ok=True)

    def step(name: str, ok: bool, note: str = "", screenshot: Optional[str] = None):
        res["steps"].append({"name": name, "ok": ok, "note": note, "screenshot": screenshot})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            res["ran"] = True
            page.goto(web_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(800)
            page.screenshot(path=str(screens_dir / "01_home.png"), full_page=True)
            step("Load UI", True, f"Loaded {web_url}", "screenshots/01_home.png")

            clicked = False
            candidates = [
                lambda: page.get_by_role("button", name=re.compile(r"^run$|run pipeline|run audit|run", re.I)),
                lambda: page.locator("button:has-text('Run')"),
                lambda: page.locator("#run, #run-btn, #runButton"),
            ]
            for fn in candidates:
                try:
                    loc = fn()
                    if loc.count() > 0:
                        loc.first.click(timeout=4000)
                        clicked = True
                        break
                except Exception:
                    continue
            if not clicked:
                page.screenshot(path=str(screens_dir / "02_no_run_button.png"), full_page=True)
                step("Click Run", False, "Could not find Run button automatically.", "screenshots/02_no_run_button.png")
            else:
                step("Click Run", True, "Clicked Run. Waiting for results...")

            page.wait_for_timeout(2500)

            iframe_found = False
            try:
                page.wait_for_selector("iframe", timeout=10000)
                iframe_found = True
            except Exception:
                iframe_found = False

            page.screenshot(path=str(screens_dir / "03_after_run.png"), full_page=True)
            step("After Run", True, "Captured post-run state", "screenshots/03_after_run.png")
            step("Tableau iframe present", iframe_found, "Iframe detected" if iframe_found else "No iframe detected")

        except Exception as e:
            res["errors"].append(f"walkthrough_failed: {type(e).__name__}: {e}")
            try:
                page.screenshot(path=str(screens_dir / "99_error.png"), full_page=True)
                res["steps"].append({"name":"Exception screenshot","ok":False,"note":str(e),"screenshot":"screenshots/99_error.png"})
            except Exception:
                pass
        finally:
            try:
                browser.close()
            except Exception:
                pass
    return res

def main() -> int:
    root = locate_root(Path(__file__).resolve())
    out_dir = root / "instructions14" / "out"
    screens_dir = out_dir / "screenshots"
    out_dir.mkdir(parents=True, exist_ok=True)
    screens_dir.mkdir(parents=True, exist_ok=True)

    env_file = parse_env(root / ".env")
    for k, v in env_file.items():
        if os.getenv(k) in (None, ""):
            os.environ[k] = v

    api_port = int(os.getenv("AAS_API_PORT", "8000"))
    web_port = int(os.getenv("AAS_WEB_PORT", "5173"))
    chan = os.getenv("AAS_SLACK_TEST_CHANNEL", "#sales-alerts").strip()
    token = os.getenv("SLACK_BOT_TOKEN", "")

    api_base = f"http://127.0.0.1:{api_port}"
    web_url = f"http://127.0.0.1:{web_port}/index.html"
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    marker = f"[AAS execute {ts}]"

    env_status = {k: redact(k, os.getenv(k, "")) for k in KEYS}

    uvicorn_proc = start_uvicorn(root, api_port)
    web_proc = start_web_server(root, web_port)

    api_ready = wait_for_ok(f"{api_base}/health", timeout_s=30)
    web_ready = wait_for_ok(f"http://127.0.0.1:{web_port}/", timeout_s=15)

    api_health = http_json(f"{api_base}/health") if api_ready else {"ok": False, "status": None, "error": "not_ready"}
    api_views = http_json(f"{api_base}/tableau/views") if api_ready else {"ok": False, "status": None, "error": "not_ready"}
    api_run = http_json(f"{api_base}/run/pipeline", method="POST", payload={"params":{}}, timeout_s=60) if api_ready else {"ok": False, "status": None, "error": "not_ready"}

    views_count = None
    embed_present = False
    if api_views.get("ok") and isinstance(api_views.get("json"), dict):
        j = api_views["json"]
        if isinstance(j.get("views"), list):
            views_count = len(j["views"])
            if views_count and isinstance(j["views"][0], dict):
                embed_present = "embed_url" in j["views"][0]

    slack_action = None
    approve = None
    chan_id = slack_find_channel_id(token, chan)
    if api_run.get("ok") and isinstance(api_run.get("json"), dict):
        actions = api_run["json"].get("actions", [])
        if isinstance(actions, list):
            for a in actions:
                if isinstance(a, dict) and a.get("type") == "slack_message":
                    slack_action = a
                    break
        if slack_action:
            meta = slack_action.get("metadata") if isinstance(slack_action.get("metadata"), dict) else {}
            meta = dict(meta)
            meta["channel"] = chan_id or chan
            meta["text"] = f"{marker} " + str(meta.get("text") or "AAS execute walkthrough message.")
            slack_action["metadata"] = meta
            approve = http_json(f"{api_base}/approve", method="POST",
                                payload={"actions":[slack_action], "approver":"antigravity-instructions14"},
                                timeout_s=30)

    browser = run_playwright(web_url, screens_dir) if web_ready else {"ran": False, "steps": [], "errors": ["web_not_ready"]}
    slack_verify = slack_verify_marker(token, chan_id, marker) if chan_id else {"attempted": False, "found": False, "reason": "channel_id_not_found"}

    pass_reasons, fail_reasons = [], []
    if api_health.get("ok"): pass_reasons.append("API /health ok")
    else: fail_reasons.append("API not healthy/reachable")

    if views_count and views_count > 0: pass_reasons.append(f"Tableau views detected: {views_count}")
    else: fail_reasons.append("Tableau views missing/empty")

    if api_run.get("ok"): pass_reasons.append("Pipeline ran successfully")
    else: fail_reasons.append("Pipeline run failed")

    if embed_present: pass_reasons.append("embed_url present in /tableau/views")
    else: fail_reasons.append("embed_url not present in /tableau/views")

    if approve and approve.get("ok") and isinstance(approve.get("json"), dict) and approve["json"].get("status") == "success":
        pass_reasons.append("Slack approve returned success")
    else:
        fail_reasons.append("Slack approve did not return success (check channel + bot membership)")

    if slack_verify.get("attempted") and slack_verify.get("found"):
        pass_reasons.append("Slack message verified in channel history")
    else:
        fail_reasons.append("Slack message not verified in history")

    if browser.get("ran") and not browser.get("errors"):
        pass_reasons.append("Browser walkthrough ran (Playwright)")
    else:
        fail_reasons.append("Browser walkthrough incomplete (Playwright missing or selector mismatch)")

    overall = "PASS" if not fail_reasons else "FAIL"

    report = {
        "timestamp_utc": ts,
        "overall": overall,
        "api_base": api_base,
        "web_url": web_url,
        "env_status_redacted": env_status,
        "api": {"health": api_health, "tableau_views": api_views, "run_pipeline": api_run, "approve": approve},
        "analysis": {
            "views_count": views_count,
            "embed_url_present": embed_present,
            "slack_channel_name": chan,
            "slack_channel_id": chan_id,
            "marker": marker,
            "slack_verify": slack_verify,
            "pass_reasons": pass_reasons,
            "fail_reasons": fail_reasons,
        },
        "browser": browser,
    }

    (out_dir / "walkthrough_execute.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = []
    md.append("# AAS Execute Walkthrough Report (instructions14)")
    md.append(f"- Timestamp (UTC): `{ts}`")
    md.append(f"- Overall: **{overall}**")
    md.append(f"- Channel: `{chan}`  id: `{chan_id}`")
    md.append("")
    md.append("## PASS reasons")
    for r in pass_reasons: md.append(f"- ✅ {r}")
    md.append("")
    md.append("## FAIL reasons")
    if fail_reasons:
        for r in fail_reasons: md.append(f"- ❌ {r}")
    else:
        md.append("- (none)")
    md.append("")
    md.append("## Browser steps")
    for s in browser.get("steps", []):
        icon = "✅" if s.get("ok") else "❌"
        line = f"- {icon} {s.get('name')}: {s.get('note','')}".strip()
        if s.get("screenshot"):
            line += f"  (screenshot: `{s['screenshot']}`)"
        md.append(line)
    if browser.get("errors"):
        md.append("")
        md.append("### Browser errors")
        for e in browser["errors"]:
            md.append(f"- `{e}`")
    md.append("")
    md.append("## Slack verification")
    md.append(f"- marker: `{marker}`")
    md.append("```json")
    md.append(json.dumps(slack_verify, indent=2)[:2000])
    md.append("```")
    md.append("")
    md.append("If Slack fails: create the channel and invite the bot: `/invite @AAS-Bot`.")
    (out_dir / "walkthrough_execute.md").write_text("\n".join(md), encoding="utf-8")

    stop_proc(web_proc)
    stop_proc(uvicorn_proc)

    print("Wrote: instructions14/out/walkthrough_execute.md")
    return 0 if overall == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
