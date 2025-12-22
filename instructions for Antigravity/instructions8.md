# instructions8.md — Slack/Tableau Wiring Update (Antigravity Fix)

## Current status (Dec 21, 2025)
- The existing **Fast Path** Decision Studio works locally with fallback Tableau Public viz and demo‑safe Slack. It runs on `localhost:8000` for the API and `localhost:3000` for the UI.
- Real Slack and Tableau connections are still blocked when accessed from this environment. A Slack invite to the Tableau Community workspace shows `Your organization doesn’t allow you to view this site`【281934195117781†screenshot】. That means we can’t complete the sign‑in here, and there’s no way to retrieve a PAT or bot token from Slack or Tableau from within this environment.
- We need Antigravity to finish the wiring with valid credentials and network access, since the hackathon resources page lists Slack channels (#temp-tableau-hackathon-general and #temp-tableau-hackathon-question) and invites us to join the Tableau Community/DataDev Slack workspaces for support.

## Next steps for Antigravity

1. **Complete the `.env` file**
   - In the repo root, copy `.env.example` to `.env` if it doesn’t exist.
   - Fill in real credentials (do not commit them):
     ```env
     TABLEAU_SERVER_URL=<your Tableau Cloud/Server URL>
     TABLEAU_SITE_ID=<your site ID>
     TABLEAU_TOKEN_NAME=<your PAT name>
     TABLEAU_TOKEN_SECRET=<your PAT secret>

     SLACK_BOT_TOKEN=<your Slack bot token>
     SLACK_DEFAULT_CHANNEL=<channel ID for notifications>
     ```
   - Keep `.env` in `.gitignore` so secrets never reach the repo.

2. **Restore the full `TableauClient` implementation**
   - In `aas/services/tableau_client.py`, use `tableauserverclient` to sign in with PAT credentials (`TABLEAU_TOKEN_NAME` and `TABLEAU_TOKEN_SECRET`).
   - Implement `get_views()` to call `server.views.get()`, iterate through views, and return a JSON list with `id`, `name`, `workbook_id`, `content_url`, and a computed `embed_url`:
     ```python
     base = server_url.rstrip('/')
     if site_id:
         embed_url = f"{base}/t/{site_id}/views/{v.content_url}?:showVizHome=no"
     else:
         embed_url = f"{base}/views/{v.content_url}?:showVizHome=no"
     ```
   - Update `GET /tableau/views` in `aas/api.py` to return `{"status": "success", "views": views}` when credentials are present, or `{"status": "not_configured"}` otherwise. This endpoint should already exist but may be stubbed on your branch.

3. **Enable real Slack execution**
   - The code already uses `slack_sdk.WebClient` in `aas/services/slack_client.py`. Once you supply `SLACK_BOT_TOKEN` in `.env`, calls to `SlackClient.send_message()` will post to the provided channel instead of returning a demo result.
   - Test by running the agent: `POST /run/pipeline` followed by `POST /approve` on an action. Check the Slack channel to confirm that messages arrive. If Slack is still blocked in your corporate network, test from a personal network or ask your IT team.

4. **Update the frontend to load real Tableau views**
   - In the `web/` UI, call `GET /tableau/views` to fetch available views and allow the user to select one. If the list is empty, show the fallback Tableau Public dashboard.
   - When the Pipeline Leakage agent returns `analysis.visual_context`, include the chosen `embed_url` so the UI can display a **“View context in Tableau”** link on each recommended action.

5. **Verify end-to-end functionality**
   - Start the backend (`uvicorn aas.api:app`) and the frontend (e.g., `npm start` in `web/`).
   - Use the Decision Studio to run the Pipeline Audit: it should display the selected Tableau viz, show recommendations, and allow you to approve them.
   - Ensure approvals are logged in `data/approvals.jsonl` and executions in `data/executions.jsonl`. Slack messages should go out when `SLACK_BOT_TOKEN` is set.

6. **Optional enhancements**
   - Implement the currently stubbed hero plays (`Churn Rescue`, `Spend Anomaly`) to provide additional demos.
   - Consider replacing the iframe embed with Tableau Embedding API v3 to filter the viz based on the action selected.

## Important notes
- The Slack and Tableau sign-in steps must be performed outside of this constrained environment because our current organization blocks these sites. Use a personal network or a machine with access to Slack/Tableau to complete workspace sign-ups and retrieve the necessary tokens.
- Once you have valid tokens, continue development locally, and push the resulting code (sans secrets) back to the repository. This will allow the Decision Studio to run in “real mode” rather than falling back to demo.

