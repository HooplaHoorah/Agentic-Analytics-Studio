# instructions4.md — AAS Pipeline Leakage Demo (Browser + API)

This doc is for **Google Antigravity** to run a clean end-to-end demo of **Agentic Analytics Studio (AAS)** using a **web browser** (Swagger UI), with optional `curl.exe` fallbacks.

---

## 0) Prereqs

- You have the repo checked out locally.
- You are on the branch that contains the demo work:

```bash
git checkout feat/pipeline-risk-and-execution
```

- Python is installed (3.10+ recommended).

---

## 1) Install & run the API (with auto-reload)

From the repo root:

```bash
pip install -r requirements.txt
uvicorn aas.api:app --reload
```

Expected: server starts and listens on `http://127.0.0.1:8000`.

---

## 2) Browser demo path (recommended)

### 2.1 Open Swagger UI

In your browser, open:

- **Swagger UI:** `http://127.0.0.1:8000/docs`
- (Optional) **OpenAPI JSON:** `http://127.0.0.1:8000/openapi.json`

---

## 3) Golden-path scenario (Analytics → Actions → Approval → Execution audit trail)

### Step A — Run Pipeline Leakage analysis

1. In Swagger UI, find:
   - `POST /run/{play}`
2. Click **Try it out**
3. For `play`, enter:
   - `pipeline`
4. For request body, use `{}` (empty JSON)
5. Click **Execute**

✅ Expected response highlights:
- A `run_id`
- `analysis` includes:
  - `at_risk_deals` where each deal has:
    - `risk_score` (0–100)
    - `reasons` (list of strings explaining the score)
  - `drivers_of_slowdown` summary
- `actions` array exists (recommended actions)

---

### Step B — Approve & execute one action

1. In Swagger UI, find:
   - `POST /approve`
2. Click **Try it out**
3. Paste a minimal demo-safe approval body like this:

```json
{
  "actions": [
    {
      "type": "slack_message",
      "description": "demo slack ping",
      "metadata": {
        "channel": "#revops",
        "text": "AAS demo: pipeline risk detected, please review high-risk deals."
      }
    }
  ],
  "approver": "antigravity-demo"
}
```

4. Click **Execute**

✅ Expected response highlights:
- `approval_id`
- `approved_count` and `executed_count` both increment
- `execution_results` contains a success record (demo mode is OK)
- Logs written to:
  - `data/approvals.jsonl`
  - `data/executions.jsonl`

> Note: `data/` and `*.jsonl` should remain **ignored/untracked** by git.

---

### Step C — View approvals history

1. In Swagger UI, find:
   - `GET /approvals`
2. Click **Try it out** → **Execute**

✅ Expected:
- Most recent approval record is present.

---

### Step D — View execution audit trail

1. In Swagger UI, find:
   - `GET /executions`
2. Click **Try it out** → **Execute**

✅ Expected:
- Records showing executed actions, statuses, timestamps, and metadata.

---

## 4) Optional: Terminal fallbacks (Windows-friendly)

If you can’t / don’t want to use Swagger UI, use these commands:

### A) Run pipeline
```powershell
curl.exe -X POST http://127.0.0.1:8000/run/pipeline `
  -H "Content-Type: application/json" `
  -d "{}"
```

### B) Approve + execute a demo Slack action
```powershell
curl.exe -X POST http://127.0.0.1:8000/approve `
  -H "Content-Type: application/json" `
  -d "{\"actions\":[{\"type\":\"slack_message\",\"description\":\"demo slack ping\",\"metadata\":{\"channel\":\"#revops\",\"text\":\"AAS demo: pipeline risk detected, please review high-risk deals.\"}}],\"approver\":\"antigravity-demo\"}"
```

### C) View audit trails
```powershell
curl.exe http://127.0.0.1:8000/approvals
curl.exe http://127.0.0.1:8000/executions
```

---

## 5) What to say while demoing (30-second narration)

- “We run the **Pipeline Leakage** play to detect at-risk deals.”
- “Each flagged deal has a **weighted risk score** and explicit **reasons**.”
- “The system recommends actions, but **nothing executes without approval**.”
- “When approved, actions execute (demo-safe) and AAS writes an **audit trail** to approvals + executions history.”

---

## 6) Troubleshooting

- If `/docs` doesn’t load:
  - confirm server is running and port `8000` isn’t in use
- If you get 404 for `/run/pipeline`:
  - use `POST /run/{play}` with `play = pipeline`
- If logs aren’t writing:
  - confirm the process has write permission in the repo directory
  - confirm `data/` directory exists or can be created

---

## 7) Demo completion checklist

- [ ] Swagger UI loads at `/docs`
- [ ] `/run/{play}` with `pipeline` returns `risk_score` + `reasons`
- [ ] `/approve` returns `approval_id` and `executed_count > 0`
- [ ] `/approvals` shows the new approval
- [ ] `/executions` shows the new execution record
