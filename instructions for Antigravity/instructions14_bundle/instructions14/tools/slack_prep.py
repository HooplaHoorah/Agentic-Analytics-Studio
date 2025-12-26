#!/usr/bin/env python3
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from env_utils import parse_env, redact

KEYS = ["SLACK_BOT_TOKEN", "AAS_SLACK_TEST_CHANNEL"]

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

def main() -> int:
    root = locate_root(Path(__file__).resolve())
    out_dir = root / "instructions14" / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    env_file = parse_env(root / ".env")
    for k, v in env_file.items():
        if os.getenv(k) in (None, ""):
            os.environ[k] = v

    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    token = os.getenv("SLACK_BOT_TOKEN", "")
    chan = os.getenv("AAS_SLACK_TEST_CHANNEL", "#sales-alerts").strip()
    chan_name = chan.lstrip("#")

    report: Dict[str, Any] = {
        "timestamp_utc": ts,
        "channel": chan,
        "env_status_redacted": {k: redact(k, os.getenv(k, "")) for k in KEYS},
        "auth_test": None,
        "channel_found": False,
        "channel_id": None,
        "create_attempted": False,
        "create_result": None,
        "join_attempted": False,
        "join_result": None,
        "notes": [],
    }

    if not token:
        report["notes"].append("Missing SLACK_BOT_TOKEN.")
        (out_dir / "slack_prep.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        (out_dir / "slack_prep.md").write_text("SLACK_BOT_TOKEN missing.\n", encoding="utf-8")
        return 1

    try:
        from slack_sdk import WebClient  # type: ignore
        client = WebClient(token=token)
        at = client.auth_test()
        report["auth_test"] = {k: at.get(k) for k in ["ok","team","team_id","user","user_id","bot_id"] if k in at}
    except Exception as e:
        report["notes"].append(f"auth_test failed: {type(e).__name__}: {e}")
        (out_dir / "slack_prep.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        (out_dir / "slack_prep.md").write_text("auth_test failed.\n", encoding="utf-8")
        return 1

    chan_id: Optional[str] = None
    try:
        cursor = None
        for _ in range(6):
            resp = client.conversations_list(limit=200, cursor=cursor, types="public_channel,private_channel")
            for c in resp.get("channels", []):
                if c.get("name") == chan_name:
                    chan_id = c.get("id")
                    break
            if chan_id:
                break
            cursor = resp.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
    except Exception as e:
        report["notes"].append(f"conversations_list failed: {type(e).__name__}: {e}")

    if chan_id:
        report["channel_found"] = True
        report["channel_id"] = chan_id
    else:
        report["notes"].append(f"Channel '{chan}' not found via conversations_list.")
        try:
            report["create_attempted"] = True
            cr = client.conversations_create(name=chan_name)
            report["create_result"] = {"ok": cr.get("ok"), "channel": {"id": cr.get("channel", {}).get("id"), "name": cr.get("channel", {}).get("name")}}
            if cr.get("ok") and cr.get("channel", {}).get("id"):
                chan_id = cr["channel"]["id"]
                report["channel_found"] = True
                report["channel_id"] = chan_id
                report["notes"].append("Channel created successfully.")
        except Exception as e:
            report["create_result"] = {"error": type(e).__name__, "message": str(e)}
            report["notes"].append("Could not create channel (likely missing scopes). Create it manually in Slack.")

    if chan_id:
        try:
            report["join_attempted"] = True
            jr = client.conversations_join(channel=chan_id)
            report["join_result"] = {"ok": jr.get("ok"), "channel": {"id": jr.get("channel", {}).get("id"), "name": jr.get("channel", {}).get("name")}}
            if jr.get("ok"):
                report["notes"].append("Bot joined the channel (or was already a member).")
        except Exception as e:
            report["join_result"] = {"error": type(e).__name__, "message": str(e)}
            report["notes"].append("Could not auto-join channel. Invite bot manually: /invite @AAS-Bot")

    (out_dir / "slack_prep.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    md = []
    md.append("# Slack Prep Report (instructions14)")
    md.append(f"- Timestamp (UTC): `{ts}`")
    md.append(f"- Target channel: `{chan}`")
    md.append("")
    md.append("## Env status (redacted)")
    for k, v in report["env_status_redacted"].items():
        md.append(f"- `{k}`: **{v}**")
    md.append("")
    md.append("## Auth test")
    md.append("```json")
    md.append(json.dumps(report["auth_test"], indent=2))
    md.append("```")
    md.append("")
    md.append("## Channel readiness")
    md.append(f"- found: `{report['channel_found']}`")
    md.append(f"- channel_id: `{report.get('channel_id')}`")
    md.append(f"- create_attempted: `{report.get('create_attempted')}`")
    if report.get("create_result") is not None:
        md.append("```json")
        md.append(json.dumps(report["create_result"], indent=2))
        md.append("```")
    md.append(f"- join_attempted: `{report.get('join_attempted')}`")
    if report.get("join_result") is not None:
        md.append("```json")
        md.append(json.dumps(report["join_result"], indent=2))
        md.append("```")
    md.append("")
    md.append("## Notes / Next steps")
    for n in report["notes"]:
        md.append(f"- {n}")
    md.append("")
    md.append("If channel is missing, create it and invite the bot: `/invite @AAS-Bot`.")
    (out_dir / "slack_prep.md").write_text("\n".join(md), encoding="utf-8")

    print("Wrote: instructions14/out/slack_prep.md")
    return 0 if report["channel_found"] else 1

if __name__ == "__main__":
    raise SystemExit(main())
