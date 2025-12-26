# Instructions13 — Automated Browser Demo + Walkthrough Report (v13)
Generated: 2025-12-22

This bundle is for **Antigravity Agent Mode** to run a full demo in a real browser and produce a walkthrough report.

✅ What it does
- Starts (or connects to) the **backend API** (uvicorn).
- Starts (or connects to) a simple **frontend web server** that serves `web/index.html`.
- Runs an **automated browser walkthrough** using **Playwright (Chromium)**:
  1. Load the UI
  2. Click **Run**
  3. Verify Tableau embed appears
  4. (Optional) Click **Approve** for a Slack action
  5. Verify Slack delivery (best-effort via Slack API; otherwise instructs what to check)

📄 Outputs
- `instructions13/out/walkthrough_report.md`
- `instructions13/out/walkthrough_report.json`
- `instructions13/out/screenshots/*.png`

---

## 0) Unzip location
Unzip into either:
- `repo-root/instructions13/` (preferred), OR
- `repo-root/instructions for Antigravity/instructions13/`

Scripts auto-detect repo root.

---

## 1) Pre-reqs
- Python 3.10+ recommended
- A working `.env` in repo root with Real Mode credentials (NOT committed)

Required:
- `TABLEAU_SERVER_URL`
- `TABLEAU_TOKEN_NAME`
- `TABLEAU_TOKEN_SECRET`
- `SLACK_BOT_TOKEN`

Optional:
- `TABLEAU_SITE_ID` (blank for Default site)
- `AAS_SLACK_TEST_CHANNEL` (default `#aas-test`)
- `AAS_WEB_PORT` (default `5173`)
- `AAS_API_PORT` (default `8000`)
- `AAS_WALK_MODE` (`dry` or `execute`, default `dry`)
- `AAS_SKIP_BROWSER` (`1` to skip Playwright and only do API checks)

Template:
```bash
cp instructions13/env.example .env
```

---

## 2) One-command run (recommended)
### Mac/Linux
```bash
bash instructions13/scripts/2_run_walkthrough.sh
```

### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File instructions13\scripts\2_run_walkthrough.ps1
```

---

## 3) If you need to install Playwright manually
```bash
pip install playwright
python -m playwright install chromium
```

---

## 4) Slack channel requirement
If execute mode fails with `channel_not_found`:
- Create the channel named by `AAS_SLACK_TEST_CHANNEL` (default `#aas-test`) **or**
- Change `AAS_SLACK_TEST_CHANNEL` in `.env` to an existing channel
- Invite the bot to that channel: `/invite @AAS-Bot`

---

## 5) What to send back
- `instructions13/out/walkthrough_report.md`
- (optional) screenshots folder if you want visuals
