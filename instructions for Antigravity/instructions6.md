# instructions5.md — Tableau Hackathon “Fast Path” (AAS Decision Studio + Tableau + Slack)

This is the fastest path to a **judge-proof** “Golden Path” demo for the Tableau Hackathon using **Agentic Analytics Studio (AAS)**.

---

## 1) Hackathon snapshot (from Devpost page)

- Hackathon: **Tableau Hackathon**
- Theme: **“The Future of Analytics is Here. Start Building.”**
- Deadline: **Jan 12, 2026 @ 2:00pm CST** (shows “24 more days to deadline” at time of capture)
- Format: **Online**, **Public**
- Prizes: **$45,000 in cash**
- Tags shown: **Databases**, **Enterprise**, **Machine Learning/AI**
- Devpost page: https://tableau2025.devpost.com/

**What this implies for our submission (optimize for judging):**
- Lead with **Tableau-native insight** (embedded viz + metadata context).
- Prove **enterprise readiness**: human-in-the-loop approvals + audit trails.
- Show **AI/ML value** via agent reasoning + recommendations (not just a dashboard).

---

## 2) Current AAS “judge-proof” assets (what to lean on)

AAS already supports a tight enterprise demo story:
- **Play runs**: `POST /run/{play}` (use `play=pipeline` for the Pipeline Leakage hero play)
- **Human approvals**: `POST /approve`
- **Auditability**: `GET /approvals` and `GET /executions` (JSONL audit trails)
- **Decision Studio UI** (served on `localhost:3000`) showing:
  - Tableau visualization surface
  - Recommended actions list
  - Approve/ignore flows

**Demo-safe mode is fine** while wiring real integrations—but for Grand Prize vibes we should wire at least one real execution (Slack).

---

## 3) Fast Path = 3 wins (in this order)

### Win #1 — Tableau renders in the center canvas (first “wow”)
Goal: replace the empty “Tableau Visualization Surface” with a real Tableau Cloud view.

#### A) Back-end: verify Tableau credentials + list views
1) Create / confirm Tableau Personal Access Token (PAT)
2) Export env vars (names may vary; use what the repo expects):
- `TABLEAU_SERVER_URL`
- `TABLEAU_SITE_ID` (optional for default site; otherwise the site content URL)
- `TABLEAU_TOKEN_NAME`
- `TABLEAU_TOKEN_SECRET`

3) Smoke test (expect list of views/metadata):
```bash
curl http://127.0.0.1:8000/tableau/views
```

> If `/tableau/views` doesn’t exist yet, add it (returning a list of views with `name`, `id`, and `content_url`).

#### B) Front-end: embed a view (start with iframe; upgrade later)
**Tier A (fastest + reliable): iframe**
- Take a known view URL (or compute it) and embed it in an `<iframe>`.

**Tier B (upgrade): Embedding API v3**
- Once iframe works, switch to Embedding API v3 to enable richer interactions and better demo polish.

Recommended: keep iframe as fallback in case auth gets finicky during a live demo.

---

### Win #2 — The agent references Tableau context (the “Tableau-driven insights” claim)
Goal: when the pipeline agent produces recommendations, include Tableau context links.

Minimum viable:
- Agent output includes:
  - `tableau_view_name`
  - `tableau_view_url` (or `embed_url`)
  - Optional: `filters_to_apply` / `highlight_targets` (for future polish)

**Simple integration approach**
- Call `GET /tableau/views`
- Choose the “Pipeline Risk” view (by name or env-configured ID)
- Attach URL into the run response and/or each action metadata payload.

---

### Win #3 — One real execution integration (Slack ping)
Goal: Approve → Execute triggers a real Slack message (not demo-safe).

#### Slack setup (quick)
- Create a Slack App: https://api.slack.com/apps
- Add a Bot user
- Install app to workspace
- Grab `SLACK_BOT_TOKEN`

Required API method:
- `chat.postMessage`: https://api.slack.com/methods/chat.postMessage

Common scopes:
- `chat:write`
- (optional) `channels:read`, `groups:read` if you want to resolve channel names to IDs

#### Configure
- Set env var: `SLACK_BOT_TOKEN`
- (recommended) set `SLACK_CHANNEL_ID` (IDs are more reliable than channel names)

#### Verify end-to-end
1) Run Pipeline Leakage:
```bash
curl -X POST http://127.0.0.1:8000/run/pipeline -H "Content-Type: application/json" -d "{"params":{}}"
```
2) Approve a Slack action (example payload):
```bash
curl -X POST http://127.0.0.1:8000/approve   -H "Content-Type: application/json"   -d '{
    "actions":[{
      "type":"slack_message",
      "description":"pipeline risk ping",
      "metadata":{"channel":"#revops","text":"AAS: pipeline risk detected — review high-risk deals in Decision Studio."}
    }],
    "approver":"hackathon-demo"
  }'
```
3) Confirm logs:
```bash
curl http://127.0.0.1:8000/approvals
curl http://127.0.0.1:8000/executions
```

---

## 4) Implementation notes (keep it demo-resilient)

### A) Add `embed_url` server-side so the UI doesn’t guess
When returning Tableau views, include a ready-to-use `embed_url` (for iframe or Embedding API):
- With site:
  `https://<server>/t/<site_id>/views/<content_url>?:showVizHome=no`
- Without site:
  `https://<server>/views/<content_url>?:showVizHome=no`

### B) If Tableau/Slack clients are still stubs
Locate:
- `aas/services/tableau_client.py`
- `aas/services/slack_client.py`

If you see `raise NotImplementedError`, implement the minimum needed:
- Tableau: list views / create embed URL helper
- Slack: `chat.postMessage` call using `slack_sdk.WebClient`

---

## 5) Local run commands (typical)

### Backend
```bash
pip install -r requirements.txt
uvicorn aas.api:app --reload --port 8000
```
Open:
- Swagger: http://127.0.0.1:8000/docs

### Frontend
From `web/` (or whatever UI folder exists):
```bash
npm install
npm run dev
```
Open:
- http://localhost:3000

---

## 6) “Hero Play” demo script (60–90 seconds)

1) **Show Tableau viz** in Decision Studio (Pipeline Risk dashboard).
2) Click **Run Pipeline Audit** → agent returns:
   - risk scoring + reasons
   - recommended actions
3) Approve an action → **Slack ping** sends in real time.
4) Open audit panel / endpoints to prove:
   - approvals and executions are logged.

---

## 7) Handy links (even if accounts are already set)

### Devpost
- Hackathon home: https://tableau2025.devpost.com/

### Tableau
- Tableau Embedding API (v3): https://help.tableau.com/current/api/embedding_api/en-us/index.html
- Tableau REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api.htm
- Tableau Server Client (Python SDK): https://tableau.github.io/server-client-python/docs/

### Slack
- Create/manage apps: https://api.slack.com/apps
- `chat.postMessage`: https://api.slack.com/methods/chat.postMessage
- OAuth scopes reference: https://api.slack.com/scopes

---

## 8) Definition of Done (Fast Path)

- [ ] A real Tableau view renders inside Decision Studio
- [ ] Pipeline hero play produces recommendations with Tableau context link(s)
- [ ] Approve → Execute triggers **one real Slack message**
- [ ] Audit trails visible via `/approvals` and `/executions`
- [ ] Demo is repeatable end-to-end in < 2 minutes
