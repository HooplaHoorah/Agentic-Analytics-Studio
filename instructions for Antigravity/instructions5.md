# instructions5.md — Phase 2 Wrap + Tableau Hackathon “Golden Path” Kickoff

Context: We’ve wrapped Phase 2 and are transitioning into the Tableau Hackathon phase. Current working directory contains Phase 2 updates (API endpoints, real Tableau/Slack clients, JSON-safe dates, audit trails) and is ready to be committed.

---

## 0) Phase 2 Status Recap (What’s ready in working dir)

Phase 2 updates staged for commit include:
- `aas/api.py`: new endpoints:
  - `GET /approvals`
  - `GET /executions`
  - `GET /tableau/views` (Tableau views integration)
- `aas/executor.py` + `aas/services/`:
  - implemented real client logic for Tableau (`tableau_client.py`)
  - implemented real client logic for Slack (`slack_client.py`)
- `aas/agents/pipeline_leakage.py`:
  - converts date columns (`close_date`, `last_touch_date`) to strings for clean JSON output
- Audit trails:
  - logs human approvals and action executions to:
    - `data/approvals.jsonl`
    - `data/executions.jsonl`

---

## 1) Immediate Cleanup — Keep repo clean with `.gitignore`

Goal: ensure local Antigravity notes + runtime logs don’t get committed.

### Recommended `.gitignore` additions
(keeps room for future sample data/docs under `data/`, but ignores runtime jsonl logs)

```gitignore
# Local Antigravity notes (do not commit)
instructions\ for\ Antigravity/

# Local runtime audit logs (do not commit)
data/*.jsonl

# Usual suspects
.env
.venv/
__pycache__/
*.pyc
.DS_Store
