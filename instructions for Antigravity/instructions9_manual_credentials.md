# instructions9.md — Manual Credential Setup (Tableau Cloud + Slack) for AAS “Real Mode”

**Goal:** Populate the repo’s `.env` so the Decision Studio switches from demo fallback to *Real Mode*:
- Tableau: list/pick real views and generate embed URLs
- Slack: post approved actions to your workspace

> **Security note:** Token *secrets* are shown **only once** (Tableau PAT secret; Slack bot token). Store them in a password manager. Do **not** commit `.env`.

---

## 0) Where `.env` goes (and how it’s loaded)

Put the `.env` file at the **repo root** (same folder that contains `aas/` and `web/`):

```
Agentic-Analytics-Studio/
  .env              <-- here
  .env.example
  aas/
  web/
```

After editing `.env`, **restart the backend** (and the frontend if needed).

If your backend isn’t auto-loading `.env` in your environment, use one of these:

**Windows PowerShell (session-only):**
```powershell
Get-Content .env | ForEach-Object {
  if ($_ -match '^(\w+)=(.*)$') { [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') }
}
uvicorn aas.api:app --reload --port 8000
```

**macOS/Linux (session-only):**
```bash
set -a
source .env
set +a
uvicorn aas.api:app --reload --port 8000
```

---

## 1) Tableau Cloud: confirm you have a *site* (and what “Site ID” means)

AAS needs **four** Tableau values:

```env
TABLEAU_SERVER_URL=https://<your-pod>.online.tableau.com
TABLEAU_SITE_ID=<your-site-content-url>
TABLEAU_TOKEN_NAME=<your-pat-name>
TABLEAU_TOKEN_SECRET=<your-pat-secret>
```

### 1.1 Find your `TABLEAU_SERVER_URL` (the “pod”)
In Tableau Cloud, your URL looks like:

```
https://<pod>.online.tableau.com/#/site/<site-id>/...
```

Example: if you see `https://10ax.online.tableau.com/...`, then:
- `TABLEAU_SERVER_URL=https://10ax.online.tableau.com`

### 1.2 Find your `TABLEAU_SITE_ID` (aka “Site content URL”)
The `TABLEAU_SITE_ID` is the **content URL** portion shown in the Tableau Cloud URL:

```
.../#/site/<site-id>/...
```

Example: `.../#/site/agenticanalyticsstudio/...` => `TABLEAU_SITE_ID=agenticanalyticsstudio`

> If you’re on the “Default” site, the site content URL can be empty. (In that case, set `TABLEAU_SITE_ID=` blank.)

### 1.3 If you get “Tell us where to sign in” / Site URI prompt
That screen is asking for the **Site URI / Site content URL** (the same value you’ll use for `TABLEAU_SITE_ID`).

- If you don’t know it, use **Forgot URI** on that page to have Tableau email you the site info.
- If you requested a code and didn’t get one: check spam and wait a few minutes before retrying (providers throttle codes).

---

## 2) Tableau Cloud: create a Personal Access Token (PAT)

You must be signed into Tableau Cloud.

1. Click your **avatar / profile** (top-right).
2. Go to **My Account Settings** (or **Account Settings**).
3. Find **Personal Access Tokens**.
4. Click **Create new token**.
5. Enter a token name (example: `AAS-Hackathon-Token`) and create it.
6. **Copy the token secret immediately** (it’s displayed once).

Fill `.env`:
```env
TABLEAU_TOKEN_NAME=AAS-Hackathon-Token
TABLEAU_TOKEN_SECRET=<paste secret>
```

---

## 3) Tableau: publish at least one view (otherwise AAS will show `views: []`)

AAS can authenticate and still return `views: []` if your site has **no published workbooks/views** yet.

**Fastest path (web authoring):**
1. In Tableau Cloud, click **New** → **Workbook**.
2. Choose a data source (upload a CSV like `demo_pipeline_data.csv`, or use any existing data source).
3. Create a simple sheet and a dashboard.
4. Click **File → Save** (or **Publish**) to your site/project.

**Alternate (Tableau Desktop):**
- Open a workbook in Tableau Desktop → **Server → Sign In** → **Tableau Cloud** → Publish workbook.

Once you have at least one published view, call the backend endpoint again:
- `GET http://localhost:8000/tableau/views`

You should now see a non-empty list.

---

## 4) Slack: create a Bot token (xoxb-…) and install the app

AAS needs:
```env
SLACK_BOT_TOKEN=xoxb-...
```

Steps:
1. Go to Slack API: **Your Apps** → **Create New App**.
2. Choose **From scratch**, name it (example: `AAS-Bot`), select your workspace.
3. In **OAuth & Permissions**, add **Bot Token Scopes**:
   - `chat:write`
   - `chat:write.public` (lets the bot post to public channels without being invited, depending on workspace policy)
4. Click **Install to Workspace** (or **Reinstall**) to generate the **Bot User OAuth Token** (`xoxb-...`).
5. Copy the token and set it in `.env` as `SLACK_BOT_TOKEN`.

**Channel note:** If your code posts to `#general` but that channel doesn’t exist or the bot can’t post there, either:
- invite the bot to the channel: `/invite @AAS-Bot`, or
- update the default channel in the backend code (or add a `SLACK_DEFAULT_CHANNEL` env var and read it).

---

## 5) Verify end-to-end “Real Mode”

1. Backend:
   - Start: `uvicorn aas.api:app --reload --port 8000`
   - Confirm: `GET /health` is OK
   - Confirm Tableau: `GET /tableau/views` returns `status: success`
2. Frontend:
   - Start the web UI as your project does (e.g., `npm start` in `web/` or open the static page)
   - Click **Run Pipeline Audit**
3. Approve an action that routes to Slack and confirm the message arrives.

---

## 6) Troubleshooting quick hits

**Tableau shows “Unable to verify site URI”**
- Your Site URI is wrong (it must match the *site content URL* used in the Tableau Cloud URL).
- If you created a new site, use that site’s URI.

**No Tableau verification code arrives**
- Wait a few minutes and retry (email providers throttle).
- Check spam/junk.
- Confirm you’re using the correct Tableau Cloud account email.

**Slack messages fail**
- Confirm the token starts with `xoxb-` (Bot token).
- Confirm the app is installed to the workspace.
- Confirm the channel exists and the bot has permission to post.

---

## 7) What to paste into `.env` (template)

```env
# Tableau Cloud
TABLEAU_SERVER_URL=https://<pod>.online.tableau.com
TABLEAU_SITE_ID=<site-content-url>
TABLEAU_TOKEN_NAME=<pat-name>
TABLEAU_TOKEN_SECRET=<pat-secret>

# Slack
SLACK_BOT_TOKEN=xoxb-...
```
