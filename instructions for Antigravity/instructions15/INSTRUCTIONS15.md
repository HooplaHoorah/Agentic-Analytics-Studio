# Instructions 15 — “Execute Verification (No Slack Read Scopes Needed)”

Purpose: **fix the false-negative** you saw in Instructions 14, where the walkthrough marked FAIL only because the Slack bot token lacks read scopes (`channels:read` / `channels:history`).  
This bundle verifies Slack delivery using the **Chat.PostMessage API response** returned by AAS (i.e., if Slack says `ok: true`, we treat it as PASS).

## What this verifies
- Backend is reachable (`GET /health`)
- Tableau is configured (`GET /tableau/views` non-empty)
- Pipeline play runs (`POST /run/pipeline` returns `analysis` + `actions`)
- A Slack action executes successfully (`POST /approve`) and returns Slack’s `ok: true` response
- Audit trails persist (`GET /approvals`, `GET /executions`)

## Prereqs
- Repo is checked out (recommended): `feat/pipeline-risk-and-execution`
- `.env` exists in repo root and contains working Tableau + Slack credentials
- Python deps installed (repo `requirements.txt` is fine)

## Quick run (Windows PowerShell)
From repo root:
```powershell
cd "instructions15"
.\scripts_setup.ps1
.\scripts_run_verify.ps1
```

## Quick run (Mac/Linux)
From repo root:
```bash
cd instructions15
bash scripts/1_setup.sh
bash scripts/2_run_verify.sh
```

## Config (optional)
Environment variables you can set before running `2_run_verify`:

- `AAS_API_BASE` (default `http://127.0.0.1:8000`)
- `AAS_AUTO_START_API` (`1` default) — tries to start uvicorn if /health is down
- `AAS_SLACK_CHANNEL` (default `#aas-test`) — forces Slack action to this channel for the verification run
- `AAS_VERIFY_MODE` (`api` default) — `api` uses postMessage response as proof. `history` attempts readback (will be SKIPPED if missing scopes).

## Outputs
- `instructions15/out/verify_report.md`
- `instructions15/out/verify_artifacts.json` (machine-readable)
- `instructions15/out/api.log` (only if auto-start was used)

## If you *want* strict Slack readback
Update the Slack app scopes to include (public channels):
- `channels:read`
- `channels:history`  
Then re-install the app to the workspace and mint a new token.  
After that, run with: `AAS_VERIFY_MODE=history`.
