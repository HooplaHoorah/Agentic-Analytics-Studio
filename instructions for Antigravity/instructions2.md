1) Open a PR (UI is simplest)

In GitHub:

Compare & pull request

Base: main

Compare: feat/pipeline-risk-and-execution

PR title (suggested):
feat: pipeline risk scoring + approve-to-execute audit trail

PR body (paste this):

Pipeline Leakage: adds weighted risk scoring (risk_score) + per-deal reasons and a drivers_of_slowdown summary.

Actions: extends Action metadata (id/title/priority) to support downstream execution.

Approve → Execute: /approve now executes actions via executor and logs an audit trail to data/approvals.jsonl + data/executions.jsonl (demo-safe).

Test commands
curl.exe -X POST http://127.0.0.1:8000/run/pipeline -H "Content-Type: application/json" -d "{}"
curl.exe -X POST http://127.0.0.1:8000/approve -H "Content-Type: application/json" -d "{\"actions\":[{\"type\":\"slack_message\",\"description\":\"demo\",\"metadata\":{\"channel\":\"#revops\",\"text\":\"hello\"}}],\"approver\":\"demo-user\"}"
curl.exe http://127.0.0.1:8000/approvals

2) Add/confirm ignore rules (important)

Right now api.py assumes data/ is gitignored (“if you add /data to .gitignore”). 

So after PR opens (or as a quick follow-up PR), add a .gitignore at repo root with at least:
data/
*.jsonl

(so approvals/executions never get committed by accident)

3) Small product polish (high value for the hackathon demo)

Two quick wins I’d do immediately after merge:

Add GET /executions (symmetry with GET /approvals)

Ensure routing is consistent: main currently exposes POST /run/{play} 

api

 while Antigravity tested POST /run/pipeline. If the branch introduced /run/pipeline, either:

keep both (alias), or

update docs + demo script to match /run/{play}.