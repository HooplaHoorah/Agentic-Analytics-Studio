#!/usr/bin/env python3
"""Automated AAS walkthrough (API + browser) with a single report output.

- Starts backend uvicorn (if not already reachable)
- Serves frontend from ./web (python http.server)
- Uses Playwright to click through UI (best-effort selectors)
- Optionally approves a Slack action
- Produces: instructions13/out/walkthrough_report.md + json + screenshots

Environment:
  AAS_API_PORT (default 8000)
  AAS_WEB_PORT (default 5173)
  AAS_WALK_MODE: dry|execute (default dry)
  AAS_SLACK_TEST_CHANNEL (default #aas-test)
  AAS_SKIP_BROWSER (1 to skip Playwright)
"""

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
from typing import Any, Dict, Optional, Tuple

from env_utils import parse_env, redact

KEYS = [
    "TABLEAU_SERVER_URL","TABLEAU_SITE_ID","TABLEAU_TOKEN_NAME","TABLEAU_TOKEN_SECRET",
    "SLACK_BOT_TOKEN","AAS_SLACK_TEST_CHANNEL","AAS_WEB_PORT","AAS_API_PORT","AAS_WALK_MODE","AAS_SKIP_BROWSER"
]

def locate_root(start: Path) -> Path:
    def is_root(p: Path) -> bool:
        return (p / "aas").exists() and (p / "requirements.txt").exists()
    for p in [start] + list(start.parents):
        if is_root(p):
            return p
    cwd = Path.cwd().resolve()
    for p in [cwd] + list(cwd.parents):
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
    # If already running, do nothing
    if wait_for_ok(f"http://127.0.0.1:{api_port}/health", timeout_s=2):
        return None
    cmd = [sys.executable, "-m", "uvicorn", "aas.api:app", "--host", "127.0.0.1", "--port", str(api_port)]
    return subprocess.Popen(cmd, cwd=str(root), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

def start_web_server(root: Path, web_port: int) -> Optional[subprocess.Popen]:
    web_dir = root / "web"
    if not web_dir.exists():
        return None
    # If already running, do nothing
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

def slack_verify_last_message(token: str, channel_name: str, marker: str) -> Dict[str, Any]:
    # Best-effort Slack verification: find channel by name, read last 20 messages, look for marker.
    out: Dict[str, Any] = {"attempted": False, "found": False}
    if not token:
        out["reason"] = "missing_token"
        return out
    try:
        from slack_sdk import WebClient  # type: ignore
        client = WebClient(token=token)
        out["attempted"] = True
        # Normalize '#name' -> 'name'
        name = channel_name.lstrip("#")
        # Find channel id
        cursor = None
        chan_id = None
        for _ in range(5):
            resp = client.conversations_list(limit=200, cursor=cursor)
            chans = resp.get("channels", [])
            for c in chans:
                if c.get("name") == name:
                    chan_id = c.get("id")
                    break
            if chan_id:
                break
            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
        if not chan_id:
            out["reason"] = "channel_not_found_via_list"
            return out
        out["channel_id"] = chan_id
        hist = client.conversations_history(channel=chan_id, limit=20)
        msgs = hist.get("messages", [])
        out["checked_messages"] = len(msgs)
        out["found"] = any(marker in (m.get("text") or "") for m in msgs)
        return out
    except Exception as e:
        out["error"] = type(e).__name__
        out["message"] = str(e)
        return out

def run_playwright_walkthrough(web_url: str, out_screens: Path, mode: str) -> Dict[str, Any]:
    res: Dict[str, Any] = {"ran": False, "steps": [], "errors": []}
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as e:
        res["errors"].append(f"playwright_import_failed: {type(e).__name__}: {e}")
        return res

    out_screens.mkdir(parents=True, exist_ok=True)

    def step(name: str, ok: bool, note: str = "", screenshot: Optional[str] = None):
        res["steps"].append({"name": name, "ok": ok, "note": note, "screenshot": screenshot})

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        try:
            res["ran"] = True
            page.goto(web_url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(1000)
            s1 = str(out_screens / "01_home.png")
            page.screenshot(path=s1, full_page=True)
            step("Load UI", True, f"Loaded {web_url}", "screenshots/01_home.png")

            # Try to click Run
            clicked = False
            candidates = [
                ("role", lambda: page.get_by_role("button", name=re.compile(r"^run$|run pipeline|run audit|run", re.I))),
                ("text", lambda: page.locator("button:has-text('Run')")),
                ("id", lambda: page.locator("#run, #run-btn, #runButton")),
            ]
            for kind, locator_fn in candidates:
                try:
                    loc = locator_fn()
                    if loc.count() > 0:
                        loc.first.click(timeout=3000)
                        clicked = True
                        break
                except Exception:
                    continue
            if not clicked:
                s = str(out_screens / "02_no_run_button.png")
                page.screenshot(path=s, full_page=True)
                step("Click Run", False, "Could not find a Run button by heuristics. Manual click needed.", "screenshots/02_no_run_button.png")
            else:
                step("Click Run", True, "Clicked Run button. Waiting for results...")

            # Wait for something that looks like results/actions/viz
            page.wait_for_timeout(2000)

            # If there is an iframe, that may be Tableau embed
            iframe_found = False
            try:
                page.wait_for_selector("iframe", timeout=8000)
                iframe_found = True
            except Exception:
                iframe_found = False

            s2 = str(out_screens / "03_after_run.png")
            page.screenshot(path=s2, full_page=True)
            step("After Run", True, "Captured post-run state", "screenshots/03_after_run.png")

            if iframe_found:
                step("Tableau embed present", True, "Found iframe element (likely Tableau)")
            else:
                step("Tableau embed present", False, "No iframe detected; verify dashboard area manually.")

            if mode == "execute":
                # Attempt to click an Approve button (prefer Slack-related)
                approved = False
                try:
                    # Prefer a section containing 'Slack' then an Approve button within it
                    slack_block = page.locator("text=/slack/i").first
                    # Try find nearby approve
                    approve_btn = page.get_by_role("button", name=re.compile(r"approve", re.I))
                    if approve_btn.count() > 0:
                        approve_btn.first.click(timeout=5000)
                        approved = True
                except Exception:
                    approved = False

                if approved:
                    page.wait_for_timeout(1500)
                    s3 = str(out_screens / "04_after_approve.png")
                    page.screenshot(path=s3, full_page=True)
                    step("Approve Slack action", True, "Clicked Approve (best effort).", "screenshots/04_after_approve.png")
                else:
                    s3 = str(out_screens / "04_no_approve.png")
                    page.screenshot(path=s3, full_page=True)
                    step("Approve Slack action", False, "Could not click Approve automatically; manual approve needed.", "screenshots/04_no_approve.png")

        except Exception as e:
            res["errors"].append(f"walkthrough_failed: {type(e).__name__}: {e}")
            try:
                s = str(out_screens / "99_error.png")
                page.screenshot(path=s, full_page=True)
                res["steps"].append({"name": "Exception screenshot", "ok": False, "note": str(e), "screenshot": "screenshots/99_error.png"})
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
    out_dir = root / "instructions13" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    screens_dir = out_dir / "screenshots"
    screens_dir.mkdir(parents=True, exist_ok=True)

    # Load repo-root .env (and overlay into process env for this tool)
    env_path = root / ".env"
    env_file = parse_env(env_path)
    for k, v in env_file.items():
        if os.getenv(k) in (None, ""):
            os.environ[k] = v

    api_port = int(os.getenv("AAS_API_PORT", "8000"))
    web_port = int(os.getenv("AAS_WEB_PORT", "5173"))
    mode = os.getenv("AAS_WALK_MODE", "dry").strip().lower()
    skip_browser = os.getenv("AAS_SKIP_BROWSER", "0").strip() in ("1","true","yes")

    api_base = f"http://127.0.0.1:{api_port}"
    web_url = f"http://127.0.0.1:{web_port}/index.html"

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    marker = f"[AAS walkthrough {ts}]"

    env_status = {k: redact(k, os.getenv(k, "")) for k in KEYS}

    # Start services (best-effort)
    uvicorn_proc = start_uvicorn(root, api_port)
    web_proc = start_web_server(root, web_port)

    # Wait for API/web
    api_ready = wait_for_ok(f"{api_base}/health", timeout_s=30)
    web_ready = wait_for_ok(f"http://127.0.0.1:{web_port}/", timeout_s=15)

    api_health = http_json(f"{api_base}/health") if api_ready else {"ok": False, "status": None, "error": "not_ready"}
    api_views = http_json(f"{api_base}/tableau/views") if api_ready else {"ok": False, "status": None, "error": "not_ready"}
    api_run = http_json(f"{api_base}/run/pipeline", method="POST", payload={"params":{}}, timeout_s=60) if api_ready else {"ok": False, "status": None, "error": "not_ready"}

    # Determine tableau view stats + embed_url presence
    views_count = None
    embed_present = False
    embed_sample = None
    if api_views.get("ok") and isinstance(api_views.get("json"), dict):
        j = api_views["json"]
        if isinstance(j.get("views"), list):
            views_count = len(j["views"])
            if views_count and isinstance(j["views"][0], dict):
                embed_present = "embed_url" in j["views"][0]
                if embed_present:
                    embed_sample = j["views"][0].get("embed_url")

    # Approve one Slack action via API (only in execute mode)
    approve_res = None
    slack_action = None
    if mode == "execute" and api_run.get("ok") and isinstance(api_run.get("json"), dict):
        actions = api_run["json"].get("actions", [])
        if isinstance(actions, list):
            for a in actions:
                if isinstance(a, dict) and a.get("type") == "slack_message":
                    slack_action = a
                    break
        if slack_action:
            # override channel + set text marker
            chan = os.getenv("AAS_SLACK_TEST_CHANNEL", "#aas-test")
            meta = slack_action.get("metadata") if isinstance(slack_action.get("metadata"), dict) else {}
            meta = dict(meta)
            meta["channel"] = chan
            meta["text"] = f"{marker} " + str(meta.get("text") or "Hello from AAS walkthrough.")
            slack_action["metadata"] = meta
            approve_res = http_json(f"{api_base}/approve", method="POST",
                                    payload={"actions":[slack_action], "approver":"antigravity-instructions13"},
                                    timeout_s=30)

    # Browser walkthrough
    browser_res = {"ran": False, "steps": [], "errors": []}
    if (not skip_browser) and web_ready:
        browser_res = run_playwright_walkthrough(web_url, screens_dir, mode)

    # Slack verification (best-effort)
    slack_verify = {}
    if mode == "execute":
        slack_verify = slack_verify_last_message(
            os.getenv("SLACK_BOT_TOKEN",""),
            os.getenv("AAS_SLACK_TEST_CHANNEL","#aas-test"),
            marker
        )

    # Final PASS/FAIL
    pass_reasons = []
    fail_reasons = []

    if api_health.get("ok"):
        pass_reasons.append("API /health ok")
    else:
        fail_reasons.append("API not healthy/reachable")

    if views_count is not None and views_count > 0:
        pass_reasons.append(f"Tableau views detected: {views_count}")
    else:
        fail_reasons.append("Tableau views missing/empty")

    if api_run.get("ok"):
        pass_reasons.append("Pipeline ran successfully via API")
    else:
        fail_reasons.append("Pipeline run failed via API")

    if embed_present:
        pass_reasons.append("embed_url present in /tableau/views items")
    else:
        fail_reasons.append("embed_url not present in /tableau/views (UI may still work but server isn't providing it)")

    if not skip_browser:
        if browser_res.get("ran") and not browser_res.get("errors"):
            pass_reasons.append("Browser walkthrough ran (Playwright)")
        else:
            fail_reasons.append("Browser walkthrough did not fully run (Playwright missing or selector issues)")

    if mode == "execute":
        if approve_res and approve_res.get("ok") and isinstance(approve_res.get("json"), dict):
            status = approve_res["json"].get("status")
            if status == "success":
                pass_reasons.append("Slack approve returned success")
            else:
                fail_reasons.append(f"Slack approve returned status={status}")
        else:
            fail_reasons.append("Slack approve failed (http/transport)")

        if slack_verify.get("attempted") and slack_verify.get("found"):
            pass_reasons.append("Slack message verified in channel history")
        elif slack_verify.get("attempted"):
            fail_reasons.append("Slack message not found in channel history (channel missing/bot not invited/scopes)")

    overall = "PASS" if not fail_reasons else "FAIL"

    report = {
        "timestamp_utc": ts,
        "mode": mode,
        "overall": overall,
        "repo_root": str(root),
        "api_base": api_base,
        "web_url": web_url,
        "env_status_redacted": env_status,
        "api": {
            "health": api_health,
            "tableau_views": api_views,
            "run_pipeline": api_run,
            "approve": approve_res,
        },
        "analysis": {
            "views_count": views_count,
            "embed_url_present": embed_present,
            "embed_url_sample": embed_sample,
            "slack_action_used": slack_action,
            "slack_verify": slack_verify,
            "pass_reasons": pass_reasons,
            "fail_reasons": fail_reasons,
        },
        "browser": browser_res,
    }

    (out_dir / "walkthrough_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Markdown report
    md = []
    md.append("# AAS Browser Walkthrough Report (instructions13)")
    md.append(f"- Timestamp (UTC): `{ts}`")
    md.append(f"- Mode: `{mode}`")
    md.append(f"- Overall: **{overall}**")
    md.append(f"- API: `{api_base}`")
    md.append(f"- Web: `{web_url}`")
    md.append("")
    md.append("## Env status (redacted)")
    for k, v in env_status.items():
        md.append(f"- `{k}`: **{v}**")
    md.append("")
    md.append("## PASS reasons")
    for r in pass_reasons:
        md.append(f"- ✅ {r}")
    md.append("")
    md.append("## FAIL reasons")
    if fail_reasons:
        for r in fail_reasons:
            md.append(f"- ❌ {r}")
    else:
        md.append("- (none)")
    md.append("")
    md.append("## Browser walkthrough steps")
    if browser_res.get("steps"):
        for s in browser_res["steps"]:
            icon = "✅" if s.get("ok") else "❌"
            line = f"- {icon} {s.get('name')}: {s.get('note','')}".strip()
            if s.get("screenshot"):
                line += f"  (screenshot: `{s['screenshot']}`)"
            md.append(line)
    else:
        md.append("- (no browser steps recorded)")
    if browser_res.get("errors"):
        md.append("")
        md.append("### Browser errors")
        for e in browser_res["errors"]:
            md.append(f"- `{e}`")
    md.append("")
    md.append("## Key API results (abbrev)")
    md.append("### GET /health")
    md.append(f"- ok: `{api_health.get('ok')}` status: `{api_health.get('status')}`")
    if "json" in api_health:
        md.append("```json")
        md.append(json.dumps(api_health["json"], indent=2)[:2000])
        md.append("```")
    md.append("")
    md.append("### GET /tableau/views (counts)")
    md.append(f"- views_count: `{views_count}`")
    md.append(f"- embed_url_present: `{embed_present}`")
    if embed_sample:
        md.append(f"- embed_url_sample: `{embed_sample}`")
    md.append("")
    md.append("### POST /run/pipeline (status)")
    md.append(f"- ok: `{api_run.get('ok')}` status: `{api_run.get('status')}`")
    md.append("")
    if mode == "execute":
        md.append("## Slack verification")
        md.append("```json")
        md.append(json.dumps(slack_verify, indent=2)[:2000])
        md.append("```")
        md.append("")
        md.append("### If you see channel_not_found")
        md.append("- Create the channel named by `AAS_SLACK_TEST_CHANNEL` and invite the bot.")
        md.append("- Or set `AAS_SLACK_TEST_CHANNEL` in `.env` to an existing channel.")
    md.append("")

    (out_dir / "walkthrough_report.md").write_text("\n".join(md), encoding="utf-8")

    # Try to capture logs if we spawned processes
    try:
        if uvicorn_proc and uvicorn_proc.stdout:
            logs = uvicorn_proc.stdout.read()[:20000]
            (out_dir / "uvicorn.log").write_text(logs, encoding="utf-8")
    except Exception:
        pass
    try:
        if web_proc and web_proc.stdout:
            logs = web_proc.stdout.read()[:20000]
            (out_dir / "webserver.log").write_text(logs, encoding="utf-8")
    except Exception:
        pass

    # Clean up procs we started
    stop_proc(web_proc)
    stop_proc(uvicorn_proc)

    print("Wrote: instructions13/out/walkthrough_report.md")
    print("Wrote: instructions13/out/walkthrough_report.json")
    print("Overall:", overall)
    return 0 if overall == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
