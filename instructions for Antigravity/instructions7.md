# instructions7.md — Tableau Hackathon “Real Mode” + Grand-Prize Upgrades (Antigravity)

This file packages:
- The **Fast Path** (Tableau embed → agent uses Tableau context → real Slack execution)
- The **next 1–5 upgrades** to lock “Grand Prize vibes” (Real Mode → real Pipeline Risk view → Tableau-driven payload → action→viz interaction → repo hygiene)

---

## 0) What’s already working (current state)
- **Decision Studio UI** runs at `http://localhost:3000` (viz surface + action list + Approve/Ignore)
- **API** runs at `http://localhost:8000` with:
  - `POST /run/{play}` (use `pipeline` for hero play)
  - `POST /approve`
  - `GET /approvals`, `GET /executions` (audit trails)
  - `GET /tableau/views` (Tableau view listing when configured)

---

## 1) Fast Path (judge-proof): Tableau-first + human approvals + one real execution

### Win #1 — Tableau renders in the center canvas
**Goal:** replace empty viz surface with a real Tableau view.

**Start with iframe (reliable).** Keep Embedding API v3 as an upgrade path (see §4).

**Quick test:**
- Load Decision Studio
- Confirm an iframe renders *some* Tableau content (Public fallback OK initially)

### Win #2 — Tableau-driven agent context
**Goal:** agent output references Tableau context so judges see “Tableau-native insight,” not a generic agent.

Minimum:
- agent adds `visual_context` containing:
  - `tableau_view_name`
  - `tableau_view_url` (or `embed_url`)
  - optional: `suggested_filters` (stage/owner/region)

UI:
- show “View context in Tableau” badge per action card using that URL

### Win #3 — One real execution (Slack)
**Goal:** Approve → Execute triggers a real Slack message (not demo-safe).

Use Slack App + Bot token:
- Create/manage Slack apps: https://api.slack.com/apps
- Method: `chat.postMessage`: https://api.slack.com/methods/chat.postMessage
- Scopes reference: https://api.slack.com/scopes

Prefer **channel IDs** over names.

---

## 2) Real Mode: where env vars need to go (THIS IS THE UNBLOCKER)

### Where to put the `.env`
Place a file named **`.env` at the repo root** (same level as `requirements.txt` and the `aas/` folder).

The backend reads configuration using `os.getenv(...)`:
- Tableau creds are read in `GET /tableau/views` (`TABLEAU_SERVER_URL`, `TABLEAU_SITE_ID`, `TABLEAU_TOKEN_NAME`, `TABLEAU_TOKEN_SECRET`).
- Slack token is read in the executor (`SLACK_BOT_TOKEN`).

### How to ensure `.env` is actually loaded into the running process
This repo includes `python-dotenv` as a dependency. You have two safe options:

**Option A (no code changes): run uvicorn with an env file**
```bash
uvicorn aas.api:app --reload --port 8000 --env-file .env
```

**Option B (tiny code change): load dotenv inside the API module**
At the top of `aas/api.py`, add:
```python
from dotenv import load_dotenv
load_dotenv()
```
Then run:
```bash
uvicorn aas.api:app --reload --port 8000
```

> Either way: keep `.env` out of git. Add `.env` to `.gitignore` if it isn’t already.

### Suggested `.env` template
```bash
# Tableau Cloud/Server PAT
TABLEAU_SERVER_URL="https://YOUR-TABLEAU-SERVER"
TABLEAU_SITE_ID="YOUR-SITE"              # can be blank for default site
TABLEAU_TOKEN_NAME="YOUR_PAT_NAME"
TABLEAU_TOKEN_SECRET="YOUR_PAT_SECRET"

# Slack
SLACK_BOT_TOKEN="xoxb-..."
SLACK_DEFAULT_CHANNEL="C0123456789"      # strongly prefer channel ID
```

### Smoke test (Tableau)
```bash
curl http://127.0.0.1:8000/tableau/views
```
Expect `status=success` with a non-empty views list.

---

## 3) Next upgrades (1–5), in order

### 1) Turn on Real Mode (Tableau + Slack) FIRST
- Populate `.env` (see §2)
- Start backend with `--env-file .env` (or `load_dotenv()`)
- Confirm:
  - `GET /tableau/views` returns success
  - Slack execution returns success (not demo-safe)

### 2) Replace Tableau Public fallback with a real “Pipeline Risk” view
Right now, a Public fallback is good for demo resiliency.
Next step is to make the UI choose a real view from `GET /tableau/views`.

Best practice:
- Return an `embed_url` from the backend (so the UI doesn’t guess URL formats)
- UI flow:
  - call `GET /tableau/views`
  - select “Pipeline Risk” by name or configured view ID
  - embed it (fallback to Public only if status != success)

### 3) Make the agent payload explicitly “Tableau-driven”
Add a small object such as:
```json
"visual_context": {
  "view_id": "...",
  "view_name": "Pipeline Risk",
  "embed_url": "https://...",
  "suggested_filters": {"stage":"...", "owner":"...", "region":"..."}
}
```
Then:
- Action cards use this for the “View context in Tableau” badge
- Demo narration becomes simple and credible (“the agent is grounding decisions in this view”)

### 4) Grand Prize “feel”: click action → filter/highlight the viz
Move from static iframe to Embedding API v3 interactions:
- Tableau Embedding API docs: https://help.tableau.com/current/api/embedding_api/en-us/index.html

MVP behavior:
- clicking an action card applies filters (owner/stage/deal id)
- optional: deep link to view with filter params

Keep iframe fallback if auth gets weird during judging.

### 5) Repo hygiene (optional but important)
If `instructions for Antigravity/` or any other local-note directories were ever committed:
- `.gitignore` won’t remove tracked files
- you must `git rm -r` those paths (and keep notes in Dropbox instead)

Also ensure:
- `.env` is gitignored
- runtime logs stay local (e.g., `data/*.jsonl`)

---

## 4) Local run commands (quick)

### Backend
```bash
pip install -r requirements.txt
uvicorn aas.api:app --reload --port 8000 --env-file .env
```
Open:
- Swagger: http://127.0.0.1:8000/docs

### Frontend
```bash
cd web
npm install
npm run dev
```
Open:
- http://localhost:3000

---

## 5) 60–90 second judge demo script (repeatable)
1) Open Decision Studio → **Tableau view is visible** (Pipeline Risk).
2) Click **Run Pipeline Audit** → agent returns recommended actions.
3) Click **Approve All** → at least one action triggers a **real Slack message**.
4) Open `/approvals` + `/executions` → show traceability.

---

## 6) Handy links (accounts likely already set, included for completeness)
- Devpost hackathon: https://tableau2025.devpost.com/
- Tableau Embedding API v3: https://help.tableau.com/current/api/embedding_api/en-us/index.html
- Tableau REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api.htm
- Tableau Server Client (Python): https://tableau.github.io/server-client-python/docs/
- Slack Apps: https://api.slack.com/apps
- Slack `chat.postMessage`: https://api.slack.com/methods/chat.postMessage
