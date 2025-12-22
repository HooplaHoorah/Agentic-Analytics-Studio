# Slack Prep Report (instructions14)
- Timestamp (UTC): `20251222_085932`
- Target channel: `#aas-test`

## Env status (redacted)
- `SLACK_BOT_TOKEN`: **SET len=59 sha256[:10]=da327410d8**
- `AAS_SLACK_TEST_CHANNEL`: **SET len=9**

## Auth test
```json
{
  "ok": true,
  "team": "Hoopla Hoorah",
  "team_id": "T0A4Y5BV0KB",
  "user": "aasbot",
  "user_id": "U0A4SQ7J79B",
  "bot_id": "B0A4W7AKBDY"
}
```

## Channel readiness
- found: `False`
- channel_id: `None`
- create_attempted: `True`
```json
{
  "error": "SlackApiError",
  "message": "The request to the Slack API failed. (url: https://slack.com/api/conversations.create)\nThe server responded with: {'ok': False, 'error': 'missing_scope', 'needed': 'channels:write,groups:write,mpim:write,im:write', 'provided': 'chat:write,chat:write.public'}"
}
```
- join_attempted: `False`

## Notes / Next steps
- conversations_list failed: SlackApiError: The request to the Slack API failed. (url: https://slack.com/api/conversations.list)
The server responded with: {'ok': False, 'error': 'missing_scope', 'needed': 'channels:read,groups:read,mpim:read,im:read', 'provided': 'chat:write,chat:write.public'}
- Channel '#aas-test' not found via conversations_list.
- Could not create channel (likely missing scopes). Create it manually in Slack.

If channel is missing, create it and invite the bot: `/invite @AAS-Bot`.