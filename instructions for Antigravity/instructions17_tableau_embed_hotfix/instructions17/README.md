# Instructions 17 — Tableau Embed Hotfix (Demo Stability)

## Why this exists
Some demo runs show Tableau not rendering in the embedded panel and Chrome console logs:
- `Refused to display 'https://10ax.online.tableau.com/' in a frame because it set 'X-Frame-Options' to 'sameorigin'.`
- `Failed to load resource: net::ERR_NAME_NOT_RESOLVED tableau.embedding.3.latest.min.js`

This hotfix makes the demo deterministic by:
1) Ensuring the backend returns a **proper view embed URL** (not the Tableau Cloud home page).
2) Fixing the common **bad script URL** and **bad default iframe src** in the demo UI.

## What it changes
- Patches `aas/api.py` to include `embed_url` in `/tableau/views`
- Patches any demo `index.html` it finds (common locations: `web/`, `instructions*/web/`)
  - Removes default iframe src that points to the Tableau Cloud root
  - Fixes the Tableau Embedding API script src if it’s malformed

## Apply (Windows / PowerShell)
From repo root:
```powershell
powershell -ExecutionPolicy Bypass -File instructions17/scripts/1_apply_hotfix.ps1
```

## Apply (macOS/Linux)
From repo root:
```bash
bash instructions17/scripts/1_apply_hotfix.sh
```

## Verify
1) Restart backend (whatever you normally do)
2) Hit: `http://127.0.0.1:8000/tableau/views`

Expected:
- `status: "success"`
- each `views[*]` has a non-empty `embed_url` containing `/views/`

If Tableau still doesn’t render in-app:
- Open any `embed_url` in a separate tab, sign in if prompted, then refresh the demo page.
