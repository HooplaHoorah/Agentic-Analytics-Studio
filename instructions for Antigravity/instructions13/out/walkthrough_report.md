# AAS Browser Walkthrough Report (instructions13)
- Timestamp (UTC): `20251222_083010`
- Mode: `dry`
- Overall: **PASS**
- API: `http://127.0.0.1:8000`
- Web: `http://127.0.0.1:5173/index.html`

## Env status (redacted)
- `TABLEAU_SERVER_URL`: **SET len=31**
- `TABLEAU_SITE_ID`: **SET len=22**
- `TABLEAU_TOKEN_NAME`: **SET len=13 sha256[:10]=1792e90614**
- `TABLEAU_TOKEN_SECRET`: **SET len=57 sha256[:10]=c886778195**
- `SLACK_BOT_TOKEN`: **SET len=59 sha256[:10]=da327410d8**
- `AAS_SLACK_TEST_CHANNEL`: **SET len=9**
- `AAS_WEB_PORT`: **MISSING**
- `AAS_API_PORT`: **MISSING**
- `AAS_WALK_MODE`: **MISSING**
- `AAS_SKIP_BROWSER`: **MISSING**

## PASS reasons
- ✅ API /health ok
- ✅ Tableau views detected: 26
- ✅ Pipeline ran successfully via API
- ✅ embed_url present in /tableau/views items
- ✅ Browser walkthrough ran (Playwright)

## FAIL reasons
- (none)

## Browser walkthrough steps
- ✅ Load UI: Loaded http://127.0.0.1:5173/index.html  (screenshot: `screenshots/01_home.png`)
- ✅ Click Run: Clicked Run button. Waiting for results...
- ✅ After Run: Captured post-run state  (screenshot: `screenshots/03_after_run.png`)
- ✅ Tableau embed present: Found iframe element (likely Tableau)

## Key API results (abbrev)
### GET /health
- ok: `True` status: `200`
```json
{
  "status": "ok"
}
```

### GET /tableau/views (counts)
- views_count: `26`
- embed_url_present: `True`
- embed_url_sample: `https://10ax.online.tableau.com/t/agenticanalyticsstudio/views/Superstore/sheets/Overview?:showVizHome=no`

### POST /run/pipeline (status)
- ok: `True` status: `200`

