from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv


def _now_tag() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def find_repo_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(12):
        if (cur / "aas" / "api.py").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise RuntimeError("Could not locate repo root (expected to find aas/api.py above this script).")


@dataclass
class StepResult:
    name: str
    ok: bool
    details: Dict[str, Any]


def http_json(method: str, url: str, **kwargs) -> Tuple[int, Any]:
    resp = requests.request(method, url, timeout=60, **kwargs)
    try:
        return resp.status_code, resp.json()
    except Exception:
        return resp.status_code, resp.text


def wait_for_health(api_base: str, timeout_s: int = 30) -> bool:
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            code, body = http_json("GET", f"{api_base}/health")
            if code == 200 and isinstance(body, dict) and body.get("status") in ("ok", "OK"):
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def start_api(repo_root: Path, api_base: str, out_dir: Path) -> Optional[subprocess.Popen]:
    # Loads .env (repo root) into this process environment, then spawns uvicorn with the same env.
    env_path = repo_root / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    host = "127.0.0.1"
    port = "8000"
    try:
        port = api_base.split(":")[-1].strip("/")
    except Exception:
        pass

    log_path = out_dir / "api.log"
    log_f = log_path.open("w", encoding="utf-8")

    cmd = [sys.executable, "-m", "uvicorn", "aas.api:app", "--host", host, "--port", str(port)]
    p = subprocess.Popen(
        cmd,
        cwd=str(repo_root),
        stdout=log_f,
        stderr=subprocess.STDOUT,
        env=os.environ.copy(),
    )
    return p


def pick_slack_action(actions: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    for a in actions:
        if (a.get("type") or "").lower() == "slack_message":
            return a
    return None


def normalize_channel(ch: str) -> str:
    ch = (ch or "").strip()
    if not ch:
        return ch
    return ch if ch.startswith("#") else f"#{ch}"


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    repo_root = find_repo_root(script_dir)
    out_dir = script_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    api_base = os.getenv("AAS_API_BASE", "http://127.0.0.1:8000").rstrip("/")
    auto_start = os.getenv("AAS_AUTO_START_API", "1").strip() not in ("0", "false", "False", "")
    slack_channel_override = normalize_channel(os.getenv("AAS_SLACK_CHANNEL", "#aas-test"))
    verify_mode = os.getenv("AAS_VERIFY_MODE", "api").strip().lower()

    artifacts: Dict[str, Any] = {
        "run_tag": _now_tag(),
        "api_base": api_base,
        "repo_root": str(repo_root),
        "verify_mode": verify_mode,
        "steps": [],
    }

    steps: List[StepResult] = []
    api_proc: Optional[subprocess.Popen] = None

    # Step 1: Health (and optional auto-start)
    health_ok = wait_for_health(api_base, timeout_s=5)
    if not health_ok and auto_start:
        try:
            api_proc = start_api(repo_root, api_base, out_dir)
            health_ok = wait_for_health(api_base, timeout_s=40)
        except Exception as e:
            steps.append(StepResult("api_autostart", False, {"error": str(e)}))

    steps.append(StepResult("api_health", bool(health_ok), {"checked": f"{api_base}/health"}))
    if not health_ok:
        artifacts["steps"] = [s.__dict__ for s in steps]
        (out_dir / "verify_artifacts.json").write_text(json.dumps(artifacts, indent=2), encoding="utf-8")
        (out_dir / "verify_report.md").write_text(
            f"# Verify Report (FAIL)\n\nAPI not reachable at `{api_base}`.\n",
            encoding="utf-8",
        )
        return 2

    # Step 2: Tableau views
    code, views_body = http_json("GET", f"{api_base}/tableau/views")
    views: List[Dict[str, Any]] = []
    tableau_status = None
    if isinstance(views_body, dict):
        tableau_status = views_body.get("status")
        views = views_body.get("views") or []
    steps.append(
        StepResult(
            "tableau_views",
            code == 200 and isinstance(views, list) and len(views) > 0 and tableau_status in (None, "success"),
            {"http": code, "status": tableau_status, "view_count": len(views)},
        )
    )

    # Step 3: Run pipeline
    code, run_body = http_json("POST", f"{api_base}/run/pipeline", json={"params": {}})
    actions: List[Dict[str, Any]] = []
    analysis: Dict[str, Any] = {}
    run_id = None
    if isinstance(run_body, dict):
        run_id = run_body.get("run_id")
        actions = run_body.get("actions") or []
        analysis = run_body.get("analysis") or {}
    steps.append(
        StepResult(
            "run_pipeline",
            code == 200 and isinstance(run_body, dict) and isinstance(actions, list) and len(actions) > 0,
            {
                "http": code,
                "run_id": run_id,
                "actions_count": len(actions),
                "analysis_keys": sorted(list(analysis.keys()))[:25],
            },
        )
    )

    # Step 4: Approve + execute ONE Slack action (forced to known channel)
    slack_action = pick_slack_action(actions) or {
        "type": "slack_message",
        "title": "AAS demo slack ping",
        "description": "Synthetic slack message for verification run.",
        "priority": "low",
        "metadata": {"channel": slack_channel_override, "text": f"[AAS verify {artifacts['run_tag']}] test message"},
    }

    # Force channel to override for reliability
    slack_action = dict(slack_action)
    slack_action["metadata"] = dict(slack_action.get("metadata") or {})
    if slack_channel_override:
        slack_action["metadata"]["channel"] = slack_channel_override

    approve_payload = {"actions": [slack_action], "approver": "instructions15-verifier", "run_id": run_id}
    code, approve_body = http_json("POST", f"{api_base}/approve", json=approve_payload)

    slack_exec_ok = False
    slack_exec_details: Dict[str, Any] = {"http": code}
    if isinstance(approve_body, dict):
        slack_exec_details["approval_id"] = approve_body.get("approval_id")
        slack_exec_details["executed_count"] = approve_body.get("executed_count")
        exec_results = approve_body.get("execution_results") or []
        slack_exec_details["execution_results_count"] = len(exec_results)

        # Find slack execution result
        slack_result = None
        for r in exec_results:
            if (r.get("type") or "").lower() == "slack_message":
                slack_result = r
                break
        slack_exec_details["slack_result"] = slack_result

        # "API verify" uses Slack postMessage response (details.ok == True)
        if slack_result and isinstance(slack_result, dict):
            status = slack_result.get("status")
            details = slack_result.get("details") or {}
            ok_field = None
            if isinstance(details, dict):
                ok_field = details.get("ok")
            slack_exec_details["slack_status"] = status
            slack_exec_details["slack_ok"] = ok_field
            slack_exec_details["slack_channel_id"] = details.get("channel") if isinstance(details, dict) else None
            slack_exec_details["slack_ts"] = details.get("ts") if isinstance(details, dict) else None

            if verify_mode == "api":
                slack_exec_ok = (status == "success") and (ok_field is True)
            else:
                # history mode: still accept success+ok, but mark as "needs scopes" for readback
                slack_exec_ok = (status == "success") and (ok_field is True)
                slack_exec_details["history_readback_note"] = (
                    "history readback not implemented here; requires channels:read + channels:history. "
                    "Run Instructions14 if you need browser+readback coverage."
                )

    steps.append(StepResult("approve_slack_action", slack_exec_ok, slack_exec_details))

    # Step 5: Audit trails (approvals/executions)
    code_a, approvals_body = http_json("GET", f"{api_base}/approvals")
    code_e, executions_body = http_json("GET", f"{api_base}/executions")
    approvals_n = len(approvals_body.get("approvals", [])) if isinstance(approvals_body, dict) else None
    executions_n = len(executions_body.get("executions", [])) if isinstance(executions_body, dict) else None
    steps.append(
        StepResult(
            "audit_trails",
            code_a == 200 and code_e == 200 and isinstance(approvals_n, int) and isinstance(executions_n, int),
            {"approvals_http": code_a, "executions_http": code_e, "approvals_count": approvals_n, "executions_count": executions_n},
        )
    )

    # Cleanup: if we auto-started API, leave it running (demo-friendly). We just note it.
    if api_proc is not None:
        steps.append(StepResult("note", True, {"api_autostart": True, "api_pid": api_proc.pid, "api_log": str(out_dir / "api.log")}))

    artifacts["steps"] = [s.__dict__ for s in steps]
    (out_dir / "verify_artifacts.json").write_text(json.dumps(artifacts, indent=2), encoding="utf-8")

    overall_ok = all(s.ok for s in steps if s.name not in ("note",))
    status_word = "PASS" if overall_ok else "FAIL"

    # Markdown report
    lines = [f"# Verify Report ({status_word})", ""]
    lines.append(f"- Run tag: `{artifacts['run_tag']}`")
    lines.append(f"- API base: `{api_base}`")
    lines.append(f"- Verify mode: `{verify_mode}`")
    lines.append(f"- Slack channel override: `{slack_channel_override}`")
    lines.append("")
    lines.append("## Steps")
    for s in steps:
        icon = "✅" if s.ok else "❌"
        lines.append(f"- {icon} **{s.name}** — {json.dumps(s.details, ensure_ascii=False)}")
    lines.append("")
    lines.append("## Notes")
    lines.append("- If Slack shows `channel_not_found`, create the channel and invite the bot: `/invite @aasbot`.")
    lines.append("- If you want strict readback verification, add Slack scopes `channels:read` + `channels:history` and reinstall the app.")

    (out_dir / "verify_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    return 0 if overall_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
