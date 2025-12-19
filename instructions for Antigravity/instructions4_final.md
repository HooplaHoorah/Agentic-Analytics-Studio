# instructions4_final.md — AAS Golden-Path Demo (Swagger UI / Browser)

This is the **copy/paste demo runbook** for Google Antigravity to execute the full AAS “analytics → approval → execution audit trail” flow using a **browser** (Swagger UI). Includes Windows `curl.exe` fallbacks.

---

## 0) Prereqs

From repo root:

```bash
git checkout feat/pipeline-risk-and-execution
pip install -r requirements.txt
uvicorn aas.api:app --reload
```

API should be live at:

- `http://127.0.0.1:8000`

---

## 1) Open Swagger UI

Open in your browser:

- `http://127.0.0.1:8000/docs`

(Optional OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`)

---

## 2) Golden path (Browser)

### Step A — Run Pipeline Leakage (POST /run/{play})

1. Expand **POST /run/{play}** (Run Play)
2. Click **Try it out**
3. Set `play` to:

```
pipeline
```

4. In the request body, paste **exactly one JSON object**:

```json
{
  "params": {}
}
```

5. Click **Execute**

✅ Expected output highlights:
- `run_id`
- `analysis.at_risk_deals[*].risk_score`
- `analysis.at_risk_deals[*].reasons`
- `analysis.drivers_of_slowdown`
- `actions` array

#### If you get 422 “JSON decode error / Extra data”
This means the body contains **two JSON fragments**, e.g.:
```json
{"params": {}}{ "params": {} }
```
Fix:
- Click **Reset**
- Click **Clear**
- Paste ONLY:
  - `{"params": {}}`

#### If the Request URL looks like `/run/pipelinepipeline`
Fix:
- Click **Reset**
- Re-enter `play = pipeline` (exactly once)

---

### Step B — Approve + Execute one action (POST /approve)

1. Expand **POST /approve**
2. Click **Try it out**
3. Paste this request body:

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

✅ Expected:
- `approval_id`
- `approved_count` increments
- `executed_count` increments (demo-safe execution is OK)
- `execution_results` shows success (demo mode fallback if no Slack token)
- Logs written locally:
  - `data/approvals.jsonl`
  - `data/executions.jsonl`

> Ensure `data/` and `*.jsonl` remain **gitignored/untracked**.

---

### Step C — Verify approvals history (GET /approvals)

1. Expand **GET /approvals**
2. Click **Try it out** → **Execute**

✅ Expected:
- Recent approval record present.

---

### Step D — Verify execution audit trail (GET /executions)

1. Expand **GET /executions**
2. Click **Try it out** → **Execute**

✅ Expected:
- Recent execution record present with timestamp/status/metadata.

---

## 3) “What to say” demo narration (tight)

- “Pipeline Leakage flags at-risk deals with a **weighted risk_score** and explicit **reasons**.”
- “AAS recommends actions, but nothing runs without **human approval**.”
- “Once approved, actions execute (demo-safe) and we get a complete **audit trail**: approvals + executions.”

---

## 4) Optional Windows terminal fallbacks (curl.exe)

### A) Run pipeline
```powershell
curl.exe -X POST http://127.0.0.1:8000/run/pipeline `
  -H "Content-Type: application/json" `
  -d "{\"params\":{}}"
```

### B) Approve + execute demo action
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

## 5) Demo completion checklist

- [ ] Swagger UI loads at `/docs`
- [ ] `POST /run/{play}` with `play=pipeline` returns `risk_score` + `reasons`
- [ ] `POST /approve` returns `approval_id` and `executed_count > 0`
- [ ] `GET /approvals` shows the new approval
- [ ] `GET /executions` shows the new execution record
