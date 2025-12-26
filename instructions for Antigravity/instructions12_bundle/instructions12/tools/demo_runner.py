#!/usr/bin/env python3
"""Phase 2 Demo Runner: PASS/FAIL report + optional approve→execute.

Usage:
  python instructions12/tools/demo_runner.py --mode dry
  python instructions12/tools/demo_runner.py --mode execute

Outputs:
  instructions12/out/demo_report.md
  instructions12/out/demo_report.json
"""

import argparse
import hashlib
import json
import os
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

KEYS = [
  "TABLEAU_SERVER_URL","TABLEAU_SITE_ID","TABLEAU_TOKEN_NAME","TABLEAU_TOKEN_SECRET",
  "SLACK_BOT_TOKEN","AAS_SLACK_TEST_CHANNEL"
]

def short_fp(v: str) -> str:
    return hashlib.sha256(v.encode('utf-8')).hexdigest()[:10]

def redact(k: str, v: str) -> str:
    if not v:
        return "MISSING"
    if "TOKEN" in k or "SECRET" in k:
        return f"SET len={len(v)} sha256[:10]={short_fp(v)}"
    return f"SET len={len(v)}"

def parse_env(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    out: Dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out

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

def slack_auth_test(token: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"configured": bool(token)}
    if not token:
        return out
    try:
        from slack_sdk import WebClient  # type: ignore
        resp = WebClient(token=token).auth_test()
        out["auth_test_ok"] = True
        for k in ["url","team","team_id","user","user_id","bot_id"]:
            if k in resp:
                out[k] = resp[k]
        return out
    except Exception as e:
        out["auth_test_ok"] = False
        out["error"] = type(e).__name__
        out["message"] = str(e)
        return out

def tableau_probe(server_url: str, token_name: str, token_secret: str, site_id: str) -> Dict[str, Any]:
    out: Dict[str, Any] = {"configured": bool(server_url and token_name and token_secret)}
    if not out["configured"]:
        return out
    try:
        import tableauserverclient as TSC  # type: ignore
        server = TSC.Server(server_url, use_server_version=True)
        auth = TSC.PersonalAccessTokenAuth(token_name, token_secret, site_id=site_id or "")
        with server.auth.sign_in(auth):
            wbs, _ = server.workbooks.get()
            views, _ = server.views.get()
            out["signed_in"] = True
            out["workbooks_count"] = len(wbs)
            out["views_count"] = len(views)
            out["workbooks_sample"] = [{"name": wb.name, "id": wb.id} for wb in wbs[:5]]
            out["views_sample"] = [{"name": v.name, "content_url": getattr(v,"content_url",None), "id": v.id} for v in views[:10]]
        return out
    except Exception as e:
        out["signed_in"] = False
        out["error"] = type(e).__name__
        out["message"] = str(e)
        return out

def recommended_embed_url(server_url: str, site_id: str, content_url: str) -> str:
    server_url = server_url.rstrip("/")
    content_url = content_url.lstrip("/")
    if site_id:
        return f"{server_url}/t/{site_id}/views/{content_url}?:showVizHome=no"
    return f"{server_url}/views/{content_url}?:showVizHome=no"

def pick_slack_action(run_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    actions = run_payload.get("actions")
    if not isinstance(actions, list):
        return None
    for a in actions:
        if isinstance(a, dict) and a.get("type") == "slack_message":
            return a
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["dry","execute"], default="dry")
    args = ap.parse_args()

    root = locate_root(Path(__file__).resolve())
    out_dir = root / "instructions12" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    env_file = parse_env(root / ".env")
    for k, v in env_file.items():
        if os.getenv(k) in (None, ""):
            os.environ[k] = v

    api_base = os.getenv("API_BASE", "http://127.0.0.1:8000").rstrip("/")
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    env_status_file = {k: redact(k, env_file.get(k, "")) for k in KEYS}
    env_status_proc = {k: redact(k, os.getenv(k, "")) for k in KEYS}

    api_health = http_json(f"{api_base}/health")
    api_views  = http_json(f"{api_base}/tableau/views")
    run_pipe   = http_json(f"{api_base}/run/pipeline", method="POST", payload={"params":{}}, timeout_s=60)

    views_count = None
    embed_present = False
    embed_reco = None
    if api_views.get("ok") and isinstance(api_views.get("json"), dict):
        j = api_views["json"]
        if j.get("status") == "success" and isinstance(j.get("views"), list):
            views_count = len(j["views"])
            if views_count and isinstance(j["views"][0], dict):
                embed_present = "embed_url" in j["views"][0]
                if not embed_present:
                    server_url = os.getenv("TABLEAU_SERVER_URL","")
                    site_id = os.getenv("TABLEAU_SITE_ID","")
                    content_url = str(j["views"][0].get("content_url",""))
                    if server_url and content_url:
                        embed_reco = recommended_embed_url(server_url, site_id, content_url)

    direct_slack = slack_auth_test(os.getenv("SLACK_BOT_TOKEN",""))
    direct_tableau = tableau_probe(
        os.getenv("TABLEAU_SERVER_URL",""),
        os.getenv("TABLEAU_TOKEN_NAME",""),
        os.getenv("TABLEAU_TOKEN_SECRET",""),
        os.getenv("TABLEAU_SITE_ID",""),
    )

    picked = None
    approve = None
    if run_pipe.get("ok") and isinstance(run_pipe.get("json"), dict):
        picked = pick_slack_action(run_pipe["json"])

    if picked and isinstance(picked, dict):
        channel = os.getenv("AAS_SLACK_TEST_CHANNEL", "#aas-test")
        meta = picked.get("metadata") if isinstance(picked.get("metadata"), dict) else {}
        meta = dict(meta)
        meta["channel"] = channel
        meta["text"] = f"[AAS demo-runner {ts}] " + str(meta.get("text") or "Slack test message from demo-runner.")
        picked["metadata"] = meta

        if args.mode == "execute":
            approve = http_json(f"{api_base}/approve", method="POST",
                                payload={"actions":[picked], "approver":"antigravity-instructions12"},
                                timeout_s=30)

    pass_reasons = []
    fail_reasons = []

    if api_health.get("ok"):
        pass_reasons.append("/health ok")
    else:
        fail_reasons.append("/health failed")

    if not api_views.get("ok"):
        fail_reasons.append("/tableau/views failed (http/transport)")
    else:
        if views_count is None:
            fail_reasons.append("/tableau/views unparsable")
        elif views_count == 0:
            fail_reasons.append("/tableau/views returned 0 views")
        else:
            pass_reasons.append(f"/tableau/views returned {views_count} views")

    if not run_pipe.get("ok"):
        fail_reasons.append("/run/pipeline failed")
    else:
        pass_reasons.append("/run/pipeline ok")
        if not picked:
            fail_reasons.append("No slack_message action in pipeline output")
        else:
            pass_reasons.append("Found slack_message action candidate")

    if args.mode == "execute":
        if approve is None:
            fail_reasons.append("Execute: approve not run (no action)")
        elif not approve.get("ok"):
            fail_reasons.append("Execute: /approve failed (http/transport)")
        else:
            j = approve.get("json", {})
            status = j.get("status") if isinstance(j, dict) else None
            if status == "success":
                pass_reasons.append("Execute: /approve returned success")
            elif status == "demo_success":
                fail_reasons.append("Execute: Slack still not configured (demo_success)")
            else:
                fail_reasons.append(f"Execute: /approve returned status={status}")

    overall = "PASS" if not fail_reasons else "FAIL"

    report = {
        "timestamp_utc": ts,
        "mode": args.mode,
        "overall": overall,
        "repo_root": str(root),
        "api_base": api_base,
        "env_status_from_file": env_status_file,
        "env_status_in_process": env_status_proc,
        "api": {"health": api_health, "tableau_views": api_views, "run_pipeline": run_pipe, "approve": approve},
        "analysis": {
            "views_count": views_count,
            "embed_url_field_present": embed_present,
            "embed_url_recommendation_sample": embed_reco,
            "picked_slack_action": picked,
            "pass_reasons": pass_reasons,
            "fail_reasons": fail_reasons,
        },
        "direct": {"slack": direct_slack, "tableau": direct_tableau},
    }

    (out_dir / "demo_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = []
    md.append("# AAS Phase 2 Demo Runner Report (instructions12)")
    md.append(f"- Timestamp (UTC): `{ts}`")
    md.append(f"- Mode: `{args.mode}`")
    md.append(f"- Overall: **{overall}**")
    md.append(f"- API base: `{api_base}`")
    md.append("")
    md.append("## Env status (redacted)")
    md.append("### From .env file")
    for k,v in env_status_file.items():
        md.append(f"- `{k}`: **{v}**")
    md.append("")
    md.append("### In demo-runner process env")
    for k,v in env_status_proc.items():
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
    md.append("## Tableau embed URL check")
    md.append(f"- embed_url field present in /tableau/views items: `{embed_present}`")
    if (not embed_present) and embed_reco:
        md.append(f"- Recommended embed_url sample to add server-side: `{embed_reco}`")
    md.append("")
    md.append("## Direct probes (bypass backend)")
    md.append("### Slack auth.test")
    md.append("```json")
    md.append(json.dumps(direct_slack, indent=2))
    md.append("```")
    md.append("")
    md.append("### Tableau sign-in + counts")
    md.append("```json")
    md.append(json.dumps(direct_tableau, indent=2))
    md.append("```")
    md.append("")

    def md_api(title: str, resp: Dict[str, Any]):
        md.append(f"## {title}")
        md.append(f"- ok: `{resp.get('ok')}`  status: `{resp.get('status')}`")
        if "json" in resp:
            md.append("```json")
            md.append(json.dumps(resp["json"], indent=2)[:8000])
            md.append("```")
        else:
            md.append("```")
            md.append(str(resp.get("raw") or resp.get("message") or "")[:8000])
            md.append("```")
        md.append("")

    md_api("GET /health", api_health)
    md_api("GET /tableau/views", api_views)
    md_api("POST /run/pipeline", run_pipe)
    if approve is not None:
        md_api("POST /approve (execute mode)", approve)

    (out_dir / "demo_report.md").write_text("\n".join(md), encoding="utf-8")

    print("Wrote: instructions12/out/demo_report.md")
    print("Wrote: instructions12/out/demo_report.json")
    print("Overall:", overall)

if __name__ == "__main__":
    main()
