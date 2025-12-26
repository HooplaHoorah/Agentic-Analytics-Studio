#!/usr/bin/env python3
from __future__ import annotations

import json, os, time, urllib.request, urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from redact import redact

def now_tag() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")

def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(12):
        if (cur / "aas" / "api.py").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise RuntimeError("Could not find repo root")

def parse_env(path: Path) -> Dict[str, str]:
    out: Dict[str, str] = {}
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out

def http_json(url: str, method: str="GET", payload: Optional[dict]=None, timeout_s: int=60) -> Dict[str, Any]:
    headers = {"Content-Type":"application/json"}
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as r:
            raw = r.read().decode("utf-8", errors="replace")
            try:
                return {"ok": True, "status": r.status, "json": json.loads(raw)}
            except Exception:
                return {"ok": True, "status": r.status, "raw": raw}
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": e.code, "error":"HTTPError", "raw": raw}
    except Exception as e:
        return {"ok": False, "status": None, "error": type(e).__name__, "message": str(e)}

def try_playwright_screens(url: str, out_dir: Path) -> Dict[str, Any]:
    res: Dict[str, Any] = {"attempted": False, "available": False, "screenshots": [], "errors": []}
    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as e:
        res["errors"].append(f"playwright_not_available: {type(e).__name__}: {e}")
        return res

    res["attempted"] = True
    screens = out_dir / "screenshots"
    screens.mkdir(parents=True, exist_ok=True)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(800)
            s1 = screens / "01_home.png"
            page.screenshot(path=str(s1), full_page=True)
            res["screenshots"].append(str(s1.relative_to(out_dir)))
            # click Run best-effort
            try:
                page.locator("button:has-text('Run')").first.click(timeout=3000)
            except Exception:
                pass
            page.wait_for_timeout(2500)
            s2 = screens / "02_after_run.png"
            page.screenshot(path=str(s2), full_page=True)
            res["screenshots"].append(str(s2.relative_to(out_dir)))
            browser.close()
        res["available"] = True
    except Exception as e:
        res["errors"].append(f"playwright_failed: {type(e).__name__}: {e}")
    return res

def main() -> int:
    here = Path(__file__).resolve()
    root = find_repo_root(here)
    out_dir = root / "instructions16" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    # load .env into process env (only if not already set)
    env = parse_env(root / ".env")
    for k, v in env.items():
        if os.getenv(k) in (None, ""):
            os.environ[k] = v

    api_port = int(os.getenv("AAS_API_PORT", "8000"))
    web_port = int(os.getenv("AAS_WEB_PORT", "5173"))
    api_base = os.getenv("AAS_API_BASE", f"http://127.0.0.1:{api_port}").rstrip("/")
    web_url = f"http://localhost:{web_port}/index.html"
    run_tag = now_tag()

    exec_slack = os.getenv("AAS_EVIDENCE_EXECUTE_SLACK", "0").strip() in ("1","true","True","YES","yes")
    slack_channel = os.getenv("AAS_SLACK_CHANNEL", "#aas-test").strip()

    env_status = {}
    for k in ["TABLEAU_SERVER_URL","TABLEAU_SITE_ID","TABLEAU_TOKEN_NAME","TABLEAU_TOKEN_SECRET","SLACK_BOT_TOKEN"]:
        env_status[k] = redact(k, os.getenv(k, ""))

    artifacts: Dict[str, Any] = {
        "run_tag": run_tag,
        "api_base": api_base,
        "web_url": web_url,
        "env_status_redacted": env_status,
        "execute_slack": exec_slack,
        "slack_channel": slack_channel,
        "api": {},
        "screenshots": {},
        "notes": [],
    }

    # API snapshots
    artifacts["api"]["health"] = http_json(f"{api_base}/health")
    artifacts["api"]["tableau_views"] = http_json(f"{api_base}/tableau/views")
    artifacts["api"]["run_pipeline"] = http_json(f"{api_base}/run/pipeline", method="POST", payload={"params":{}}, timeout_s=90)

    # Optional Slack execution (approve 1 slack action)
    approve = None
    if exec_slack and artifacts["api"]["run_pipeline"].get("ok") and isinstance(artifacts["api"]["run_pipeline"].get("json"), dict):
        actions = artifacts["api"]["run_pipeline"]["json"].get("actions", [])
        slack_action = None
        if isinstance(actions, list):
            for a in actions:
                if isinstance(a, dict) and (a.get("type") or "").lower() == "slack_message":
                    slack_action = a
                    break
        if slack_action is None:
            artifacts["notes"].append("No slack_message action found; creating synthetic slack action for evidence.")
            slack_action = {"type":"slack_message","title":"AAS evidence ping","description":"Synthetic slack message",
                           "priority":"low","metadata":{"channel":slack_channel,"text":f"[AAS evidence {run_tag}] ping"}}
        else:
            meta = dict(slack_action.get("metadata") or {})
            meta["channel"] = slack_channel
            meta["text"] = f"[AAS evidence {run_tag}] " + str(meta.get("text") or "AAS evidence message.")
            slack_action = dict(slack_action)
            slack_action["metadata"] = meta

        approve = http_json(f"{api_base}/approve", method="POST",
                            payload={"actions":[slack_action], "approver":"instructions16-evidence"},
                            timeout_s=45)
    else:
        artifacts["notes"].append("Slack execution skipped (dry mode). Set AAS_EVIDENCE_EXECUTE_SLACK=1 to include it.")

    artifacts["api"]["approve"] = approve

    # Audit trails
    artifacts["api"]["approvals"] = http_json(f"{api_base}/approvals")
    artifacts["api"]["executions"] = http_json(f"{api_base}/executions")

    # Optional screenshots
    artifacts["screenshots"] = try_playwright_screens(web_url, out_dir)

    # Summaries for markdown
    views_cnt = None
    embed_present = False
    tv = artifacts["api"]["tableau_views"]
    if tv.get("ok") and isinstance(tv.get("json"), dict):
        views = tv["json"].get("views", [])
        if isinstance(views, list):
            views_cnt = len(views)
            if views_cnt and isinstance(views[0], dict):
                embed_present = "embed_url" in views[0]

    actions_cnt = None
    rp = artifacts["api"]["run_pipeline"]
    if rp.get("ok") and isinstance(rp.get("json"), dict):
        acts = rp["json"].get("actions", [])
        if isinstance(acts, list):
            actions_cnt = len(acts)

    slack_ok = None
    if approve and approve.get("ok") and isinstance(approve.get("json"), dict):
        # best-effort: find a slack execution_result with details.ok
        ex = approve["json"].get("execution_results", [])
        if isinstance(ex, list):
            for r in ex:
                if isinstance(r, dict) and (r.get("type") or "").lower() == "slack_message":
                    det = r.get("details", {})
                    if isinstance(det, dict):
                        slack_ok = det.get("ok")
                    break

    # Write artifacts
    (out_dir / "evidence_artifacts.json").write_text(json.dumps(artifacts, indent=2), encoding="utf-8")

    lines = []
    status = "PASS"
    if not artifacts["api"]["health"].get("ok"):
        status = "FAIL"
    if views_cnt is None or views_cnt == 0:
        status = "FAIL"
    if actions_cnt is None or actions_cnt == 0:
        status = "FAIL"
    if exec_slack and slack_ok is not True:
        status = "FAIL"

    lines.append(f"# Evidence Report ({status})")
    lines.append("")
    lines.append(f"- Run tag (UTC): `{run_tag}`")
    lines.append(f"- API base: `{api_base}`")
    lines.append(f"- Demo URL: `{web_url}`")
    lines.append(f"- Tableau views detected: `{views_cnt}` (embed_url present: `{embed_present}`)")
    lines.append(f"- Pipeline actions generated: `{actions_cnt}`")
    lines.append(f"- Slack executed in report: `{exec_slack}`")
    if exec_slack:
        lines.append(f"- Slack API ok: `{slack_ok}` (channel: `{slack_channel}`)")
    lines.append("")
    lines.append("## Redacted env proof")
    for k, v in env_status.items():
        lines.append(f"- `{k}`: **{v}**")
    lines.append("")
    lines.append("## Screenshots (if available)")
    s = artifacts["screenshots"]
    if s.get("available"):
        for p in s.get("screenshots", []):
            lines.append(f"- `{p}`")
    else:
        lines.append(f"- Not captured (reason: {', '.join(s.get('errors', [])[:2])})")
    lines.append("")
    lines.append("## Notes")
    for n in artifacts.get("notes", []):
        lines.append(f"- {n}")
    lines.append("")
    lines.append("Full machine-readable output: `instructions16/out/evidence_artifacts.json`")

    (out_dir / "evidence_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("Wrote: instructions16/out/evidence_report.md")
    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
