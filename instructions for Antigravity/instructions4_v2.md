# instructions4.md — AAS Pipeline Leakage Demo (Browser + API)

This doc is for **Google Antigravity** to run a clean end-to-end demo of **Agentic Analytics Studio (AAS)** using a **web browser** (Swagger UI), with optional `curl.exe` fallbacks.

---

## 0) Prereqs

- Repo checked out locally
- Branch:

```bash
git checkout feat/pipeline-risk-and-execution
```

- Python installed (3.10+ recommended)

---

## 1) Install & run the API (with auto-reload)

From the repo root:

```bash
pip install -r requirements.txt
uvicorn aas.api:app --reload
```

Server should be live at: `http://127.0.0.1:8000`

---

## 2) Browser demo path (recommended)

Open Swagger UI:

- `http://127.0.0.1:8000/docs`

Optional OpenAPI JSON:

- `http://127.0.0.1:8000/openapi.json`

---

## 3) Golden-path scenario (Analytics → Actions → Approval → Execution audit trail)

### Step A — Run Pipeline Leakage analysis (IMPORTANT: request body must be valid JSON)

1. In Swagger UI, expand:
   - `POST /run/{play}` (Run Play)
2. Click **Try it out**
3. Set `play` to exactly:
   - `pipeline`
4. In the request body, use **one JSON object**.

✅ Recommended body (matches the OpenAPI default):

```json
{
  "params": {}
}
```

> If you paste `{}` that *can* work too, but the safest approach in Swagger UI is to keep the single-object shape above.
> **Do not leave extra lines like:**
> ```
> {}
> "params": {}
> ```
> That causes a 422 “JSON decode error / Extra data”.

5. Click **Execute**

✅ Expected response highlights:
- `run_id`
- `analysis.at_risk_deals[*].risk_score` and `analysis.at_risk_deals[*].reasons`
- `analysis.drivers_of_slowdown`
- `actions` list returned

**If you see `/run/pipelinepipeline` in the Request URL:**  
Click **Reset**, then re-enter `play = pipeline` (it must be exactly one `pipeline`).

---

### Step B — Approve & execute one action (demo-safe)

1. Expand:
   - `POST /approve`
2. Click **Try it out**
3. Use this request body:

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
- `approved_count` and `executed_count` increment
- `execution_results` includes a success status (demo-mode fallback is OK)
- Logs written to:
  - `data/approvals.jsonl`
  - `data/executions.jsonl`

> `data/` and `*.jsonl` should remain gitignored/untracked.

---

### Step C — View approvals history

1. Expand:
   - `GET /approvals`
2. Click **Try it out** → **Execute**

✅ Expected: recent approval record present.

---

### Step D — View execution audit trail

1. Expand:
   - `GET /executions`
2. Click **Try it out** → **Execute**

✅ Expected: recent execution record present with timestamps/status.

---

## 4) Optional: Terminal fallbacks (Windows-friendly)

### A) Run pipeline
```powershell
curl.exe -X POST http://127.0.0.1:8000/run/pipeline `
  -H "Content-Type: application/json" `
  -d "{\"params\":{}}"
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
- “AAS recommends actions, but **nothing executes without approval**.”
- “Once approved, actions execute (demo-safe) and AAS writes a complete **audit trail** (approvals + executions).”

---

## 6) Troubleshooting

- 422 “JSON decode error / Extra data” on `/run/{play}`:
  - Your request body is not valid JSON (usually two JSON fragments). Use **exactly**:
    - `{"params": {}}`
- 404 or wrong URL:
  - Use `POST /run/{play}` and set `play=pipeline`
- Logs not writing:
  - Confirm process has write permission in repo folder

---

## 7) Demo completion checklist

- [ ] Swagger UI loads at `/docs`
- [ ] `POST /run/{play}` with `play=pipeline` returns `risk_score` + `reasons`
- [ ] `POST /approve` returns `approval_id` and `executed_count > 0`
- [ ] `GET /approvals` shows the new approval
- [ ] `GET /executions` shows the new execution record
