# Verify Report (PASS)

- Run tag: `20251222_033135`
- API base: `http://127.0.0.1:8000`
- Verify mode: `api`
- Slack channel override: `#aas-test`

## Steps
- ✅ **api_health** — {"checked": "http://127.0.0.1:8000/health"}
- ✅ **tableau_views** — {"http": 200, "status": "success", "view_count": 26}
- ✅ **run_pipeline** — {"http": 200, "run_id": "e0675934-e100-41b5-8264-2bb6b48fb57f", "actions_count": 10, "analysis_keys": ["at_risk_deals", "drivers_of_slowdown", "narrative", "stage_distribution", "visual_context"]}
- ✅ **approve_slack_action** — {"http": 200, "approval_id": "55bc321b-3ece-4028-b3d6-8f0ce2e5c35c", "executed_count": 1, "execution_results_count": 1, "slack_result": {"action_id": "16580a69-6aa2-42f2-a005-c78666ae4faa", "type": "slack_message", "status": "success", "timestamp": "2025-12-22T09:31:37.649010+00:00", "details": {"ok": true, "channel": "C0A4U0KQFKM", "ts": "1766395896.233189", "message": {"user": "U0A4SQ7J79B", "type": "message", "ts": "1766395896.233189", "bot_id": "B0A4W7AKBDY", "app_id": "A0A4U5VM5QW", "text": ":warning: High risk deal OPP4 is stalled. Score: 55.0%. Factors: No activity in 68 days", "team": "T0A4Y5BV0KB", "bot_profile": {"id": "B0A4W7AKBDY", "app_id": "A0A4U5VM5QW", "user_id": "U0A4SQ7J79B", "name": "AAS-Bot", "icons": {"image_36": "https://a.slack-edge.com/80588/img/plugins/app/bot_36.png", "image_48": "https://a.slack-edge.com/80588/img/plugins/app/bot_48.png", "image_72": "https://a.slack-edge.com/80588/img/plugins/app/service_72.png"}, "deleted": false, "updated": 1766308281, "team_id": "T0A4Y5BV0KB"}, "blocks": [{"type": "rich_text", "block_id": "qG3RR", "elements": [{"type": "rich_text_section", "elements": [{"type": "emoji", "name": "warning", "unicode": "26a0-fe0f"}, {"type": "text", "text": " High risk deal OPP4 is stalled. Score: 55.0%. Factors: No activity in 68 days"}]}]}]}}}, "slack_status": "success", "slack_ok": true, "slack_channel_id": "C0A4U0KQFKM", "slack_ts": "1766395896.233189"}
- ✅ **audit_trails** — {"approvals_http": 200, "executions_http": 200, "approvals_count": 25, "executions_count": 23}

## Notes
- If Slack shows `channel_not_found`, create the channel and invite the bot: `/invite @aasbot`.
- If you want strict readback verification, add Slack scopes `channels:read` + `channels:history` and reinstall the app.
