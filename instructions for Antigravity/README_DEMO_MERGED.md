# Agentic Analytics Studio (AAS) — Demo Quickstart + DevPost Technical Summary

Drop this file into the repo (recommended name: `DEMO.md` or `README_DEMO.md`) for a judge-proof, copy/paste-able demo runbook.

---

## 1) Quickstart (run the API)

From the repo root:

```bash
git checkout feat/pipeline-risk-and-execution
pip install -r requirements.txt
uvicorn aas.api:app --reload
```

API will be available at:

- `http://127.0.0.1:8000`

---

## 2) Browser demo (Swagger UI)

Open:

- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON (optional): `http://127.0.0.1:8000/openapi.json`

### Step A — Run Pipeline Leakage (POST /run/{play})

1. Expand **POST /run/{play}** → **Try it out**
2. Set `play` to:

```
pipeline
```

3. Request body (paste exactly ONE JSON object):

```json
{
  "params": {}
}
```

4. Click **Execute**

✅ Expected response highlights:
- `run_id`
- `analysis.at_risk_deals[*].risk_score`
- `analysis.at_risk_deals[*].reasons`
- `analysis.drivers_of_slowdown`
- `actions` array

#### Common error: 422 “JSON decode error / Extra data”
Cause: you pasted two JSON fragments, e.g. `{"params": {}}{ "params": {} }`.

Fix:
- Click **Reset**
- Click **Clear**
- Paste ONLY: `{"params": {}}`

#### Common error: Request URL shows `/run/pipelinepipeline`
Fix:
- Click **Reset**
- Re-enter `play = pipeline` (exactly once)

---

### Step B — Approve + Execute one action (POST /approve)

1. Expand **POST /approve** → **Try it out**
2. Paste:

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

3. Click **Execute**

✅ Expected:
- `approval_id`
- `approved_count` increments
- `executed_count` increments (demo-safe fallback is OK if no Slack token)
- `execution_results` shows success
- Local audit logs written:
  - `data/approvals.jsonl`
  - `data/executions.jsonl`

> Ensure `data/` and `*.jsonl` remain **gitignored/untracked**.

---

### Step C — Verify audit trails

- **Approvals history:** `GET /approvals`
- **Executions history:** `GET /executions`

---

## 3) Optional: Windows terminal fallbacks (curl.exe)

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

## 4) “What to say” (tight narration)

- “Pipeline Leakage flags at-risk deals with a **weighted risk_score** and explicit **reasons**.”
- “AAS recommends actions, but nothing runs without **human approval**.”
- “Once approved, actions execute (demo-safe) and we get a complete **audit trail**: approvals + executions.”

---

## 5) DevPost-ready technical summary (verified)

### What was verified in the live demo
- **Risk detection:** weighted scoring explains *why* deals are at risk, plus a macro **drivers_of_slowdown** summary.
- **Human-in-the-loop:** recommended actions require explicit approval.
- **Closed-loop auditability:** approvals + execution attempts are persisted and viewable via history endpoints.

### Technical summary table

| Feature | Implementation | Status |
|---|---|---|
| Risk Scoring | Weighted linear score (normalized 0–100) | ✅ Verified |
| Action Metadata | Extended with UUIDs, Title, and Priority | ✅ Verified |
| Execution Engine | `aas/executor.py` with multi-client routing | ✅ Verified |
| Audit Trails | JSONL persistent logs (auto-managed) | ✅ Verified |
| Demo Mode | Safe fallback for unconfigured integrations | ✅ Verified |

---

## 6) Demo completion checklist

- [ ] Swagger UI loads at `/docs`
- [ ] `POST /run/{play}` with `play=pipeline` returns `risk_score` + `reasons`
- [ ] `POST /approve` returns `approval_id` and `executed_count > 0`
- [ ] `GET /approvals` shows the new approval
- [ ] `GET /executions` shows the new execution record
