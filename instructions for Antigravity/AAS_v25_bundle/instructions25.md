# instructions25.md — Add Tableau Cloud “visual_context” Links (Non-Embed) + Frontend Wiring

## Context
We stabilized the demo by defaulting the embedded dashboard to **Tableau Public** (cookie‑free, iframe‑safe) and added cache‑busting (`?v=22`) to prevent stale `app.js` from loading.

Now we're extending the agent output to include **Tableau Cloud view URLs** as `visual_context` so that:

- API consumers can **open the relevant dashboard in a new tab**;
- The UI can optionally provide a **safe link‑out** even when in Public embed mode.

Important: Tableau Cloud URLs are **not** safe to iframe on localhost due to authentication requirements and security headers (`X‑Frame‑Options: SAMEORIGIN`). Treat these as **link‑out only**.

---

## Changes Introduced
1. **Agent Output**
   - Updated `aas/agents/pipeline_leakage.py` to return a `visual_context` dictionary alongside existing analysis keys.  The new object includes:
     ```json
     {
       "view_name": "Superstore Overview",
       "workbook": "Superstore",
       "url": "https://10ax.online.tableau.com/#/site/agenticanalyticsstudio/views/Superstore/Overview",
       "note": "Embedded Tableau context for this analysis"
     }
     ```
   - This provides a Tableau Cloud URL that consumers can use to open the dashboard in a new tab rather than iframing it.

2. **Frontend Wiring**
   - Updated the action rendering logic in `web/app.js` so that when an action contains a `visual_context` on its metadata, the UI will use `visual_context.url` and `visual_context.view_name` for the “View context in Tableau” link.
   - Added fallbacks: if `visual_context.url` is not available, the code falls back to `metadata.url` or `metadata.embed_url`.
   - The link opens in a new tab when pointing at `online.tableau.com`, preserving the default Public embed for the main dashboard.

3. **Patch Diff**
   - Provided a unified diff (`patch.diff`) showing exactly where to insert or modify code in `web/app.js` and `aas/agents/pipeline_leakage.py`.  This makes it easy to apply the changes with standard patch tools.

## Canonical Demo URL
To avoid browser cache issues, continue using the `?v=22` (or bump to `?v=25` if you change the script tag) on your index page:

```
http://localhost:8082/index.html?v=22
```

---

## Next Steps
To embed your own dashboards instead of the sample “Superstore” workbook, update the fields inside the `visual_context` dictionary (both the URL and names), and update the `TABLEAU_PUBLIC_DEFAULT_URL` and `TABLEAU_PUBLIC_VIEWS` constants in `web/app.js` as needed.
