You are implementing the next milestone for Agentic Analytics Studio (AAS) in repo HooplaHoorah/Agentic-Analytics-Studio.

Goal: Make Pipeline Leakage demo feel end-to-end: better risk logic + approve→execute with an audit trail.

A) Pipeline Leakage improvements (file: aas/agents/pipeline_leakage.py)
1) Replace the current “sort by stage_age/close_date and take top 5” with a risk scoring approach:
   - risk_score = weighted sum of:
     - stage_age (normalize)
     - days_since_last_touch (if last_touch_date exists)
     - close_date_slip (if close_date exists and is in the past or moved out)
   - For each at-risk deal, attach:
     - risk_score (0-100)
     - reasons: list[str] such as ["Stalled in stage 32 days", "No activity in 18 days", "Close date slipped"]
2) Add “drivers_of_slowdown” summary:
   - stage_distribution already exists; add top stages by avg stage_age
   - add top owners by count of high-risk deals (if owner exists)
3) Ensure analysis output includes:
   - at_risk_deals: list[dict] with reasons + risk_score
   - drivers_of_slowdown: dict
   - narrative: string

B) Action metadata improvements (file: aas/models/action.py and pipeline_leakage.py)
1) Extend Action to optionally include:
   - id (uuid string) OR generate in to_dict
   - title (short string)
   - priority ("low"|"medium"|"high")
2) For pipeline leakage, generate two action types:
   - "salesforce_task" with metadata: {opportunity_id, subject, owner, due_date}
   - "slack_message" with metadata: {channel, text, opportunity_id}
   (Keep descriptions human readable.)

C) Approve → Execute (file: aas/api.py + new file aas/executor.py)
1) Add aas/executor.py with a function execute_actions(actions: list[dict], run_id: str|None) -> list[dict]
   - Route by action["type"]:
     - salesforce_task: call SalesforceClient.create_task if configured, else write a demo execution record
     - slack_message: call SlackClient.send_message if configured, else write a demo execution record
   - Return execution_results with status per action.
2) In POST /approve:
   - keep writing approvals.jsonl
   - then call execute_actions()
   - write executions.jsonl (data/executions.jsonl)
   - return {approval_id, approved_count, executed_count, execution_results, log_file, executions_file}

D) Config / demo safety
- Use env vars for Slack/Salesforce config; if not present, do NOT error—fallback to demo execution logging.
- Never commit secrets.
- Keep everything runnable locally with: uvicorn aas.api:app --reload

Acceptance:
- POST /run/pipeline returns enriched analysis + actions
- POST /approve executes in demo mode and returns execution_results
- GET /approvals still works
