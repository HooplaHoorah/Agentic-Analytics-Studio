# instructions7.md — AAS Tableau Hackathon “Fast Path” (Antigravity)

This is the **fastest, judge-proof path** to run the current Agentic Analytics Studio (AAS) demo and wire up **real Tableau Cloud** + **real Slack** (optional) without breaking the demo when creds aren’t present.

---

## 0) TL;DR checklist (copy/paste order)

1. **Get latest code**
   - `git pull`
   - `git checkout feat/pipeline-risk-and-execution` (branch referenced in README_DEMO.md)

2. **Create `.env` at repo root** (same folder as `requirements.txt`)
   - Copy `.env.example` → `.env`
   - Fill in Tableau + Slack fields (Salesforce is optional)

3. **Run backend**
   - `pip install -r requirements.txt`
   - `uvicorn aas.api:app --reload`

4. **Verify Tableau auth**
   - Open `http://127.0.0.1:8000/docs`
   - Call **GET `/tableau/views`**
     - Expect `status=success` if Tableau env vars are valid
     - Expect `status=not_configured` if missing (demo-safe)

5. **Verify Slack execution (optional)**
   - Use Swagger: **POST `/approve`** with a `slack_message` action

---

## 1) Hackathon context (Devpost)

You’re entering Tableau’s Devpost event (URL visible in the browser screenshot):
- **Devpost:** https://tableau2025.devpost.com/
- **Deadline shown:** **Jan 12, 2026 @ 2:00pm CST**
- **Prize pool shown:** **$45,000 cash**
- Tags shown: **Databases**, **Enterprise**, **Machine Learning / AI**

### What to optimize for (practical interpretation)
- **Tableau-first storytelling:** The product should feel like “Tableau + actions,” not “an agent with a dashboard.”
- **Human-in-the-loop control:** clear approvals and auditable execution.
- **Credible “real mode”** but **fails-safe** in demo mode when credentials aren’t present.

---

## 2) What is already implemented in the backend (Phase 2 complete)

These are already present in the repo (no need to re-build):

- **Audit trails** written locally:
  - `data/approvals.jsonl`
  - `data/executions.jsonl`
- **Approval + Execution APIs**
  - `POST /approve`
  - `GET /approvals`
  - `GET /executions`
- **Tableau list-views API**
  - `GET /tableau/views`
- **Slack “real mode” ready**
  - Uses `slack_sdk` when `SLACK_BOT_TOKEN` exists
  - Demo-safe fallback when not configured

---

## 3) Environment variables (where to put them)

### 3.1 Put them here
Create a file named **`.env` in the repo root** (same folder as `requirements.txt`).

✅ Recommended: start from `.env.example` included in this zip.

### 3.2 Important note about `.env` loading
The repo includes `python-dotenv`, but **the code currently reads from `os.getenv()`**.  
That means **your `.env` must be loaded into the environment** by one of these methods:

**Option A — Export env vars in your shell**
- macOS/Linux:
```bash
set -a
source .env
set +a
```
- Windows PowerShell:
```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match "^(\w+)=(.*)$") { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2]) }
}
```

**Option B — Add dotenv auto-load (recommended for teammates)**
Add the following near the top of `aas/api.py` (right after `import os`):

```python
from dotenv import load_dotenv
load_dotenv()
```

This makes `uvicorn aas.api:app --reload` pick up `.env` automatically.

---

## 4) Required vars for “Real Tableau” and “Real Slack”

### Tableau (Personal Access Token)
- `TABLEAU_SERVER_URL`  
  Example format: `https://<your-pod>.online.tableau.com`
- `TABLEAU_SITE_ID`  
  The **site content URL** (often the string after `#/site/` in Tableau Cloud URLs).  
  If you use the Default site, this is often empty.
- `TABLEAU_TOKEN_NAME`
- `TABLEAU_TOKEN_SECRET`

### Slack
- `SLACK_BOT_TOKEN`  
  Bot token with permission to post to your demo channel (e.g., `#revops`).

### Salesforce (optional for demo)
- `SALESFORCE_USERNAME` (used only as a config “on/off” check right now)

---

## 5) Tableau wiring: the recommended path

### 5.1 First: verify backend connectivity
In Swagger (`/docs`), run:
- **GET `/tableau/views`**

If configured, it should return a list of views including:
- `id`
- `name`
- `workbook_id`
- `content_url`

If not configured, it returns `status: not_configured` (this is correct and demo-safe).

### 5.2 Then: embed a “hero” view in the UI
You can embed Tableau as either:
- **iframe** (fastest, stable)
- **Embedding API v3** (best “Grand Prize vibes”: programmatic filtering + highlighting)

**Fast iframe path**
1. Open the target view in Tableau Cloud
2. Use Tableau’s **Share** dialog to copy the embed URL
3. Drop that URL into the Decision Studio viz panel

**Embedding API v3 path**
1. Use the Share dialog to grab the v3 embed snippet
2. Enable “action → filter” behaviors, so clicking an action card filters/highlights the deal in Tableau

> If you’re blocked on v3, ship iframe first. Judges value a working end-to-end story.

---

## 6) Frontend status (important)
The backend is in GitHub. **If your local Decision Studio UI exists, make sure it’s committed and pushed.**  
A quick sanity check is that the repo contains a frontend folder with a `package.json`.

If the UI is not in GitHub yet:
- commit the local UI folder (commonly `web/`)
- push it to the same branch you’re demoing (recommended: `feat/pipeline-risk-and-execution`)

---

## 7) Demo script (tight narrative)
1. “Here’s our Tableau dashboard: it shows pipeline performance and risk indicators.”  
2. “AAS runs the Pipeline Leakage play and explains risk with **reasons + scores**.”  
3. “The agent proposes actions, but nothing executes without **human approval**.”  
4. “Once approved, we execute (Slack) and persist a complete audit trail: approvals + executions.”

---

## 8) Common Tableau gotchas (90% of failures)
- **Wrong SERVER_URL** (should be base host, not a long /#/site/... URL)
- **Wrong SITE_ID** (needs site content URL, not display name)
- **Token is not PAT** / token doesn’t have permission for the workbook
- **Network / SSO** (Tableau Cloud behind SSO can block PAT-based scripts depending on org settings)

---

## 9) Next “Grand Prize” upgrades (after wiring works)
- Click action card → automatically filter/highlight the deal in Tableau (Embedding API v3)
- Add “visual_context” deep links per action card (already partially implemented conceptually)
- Make Slack messages include a direct link back to the exact Tableau view / filtered state

---

## Appendix: minimal test payload (Slack)
Use Swagger: **POST `/approve`**

```json
{
  "actions": [
    {
      "type": "slack_message",
      "description": "demo slack ping",
      "metadata": {
        "channel": "#revops",
        "text": "AAS demo: pipeline risk detected — please review high-risk deals."
      }
    }
  ],
  "approver": "antigravity-demo"
}
```
