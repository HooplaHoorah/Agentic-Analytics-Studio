# instructions24.md — v22 Demo Stability Confirmed (Tableau Public Embed + Cache Bust)

## Context
We hit an iframe/auth reliability issue when embedding Tableau Cloud (`*.online.tableau.com`) from `localhost`:
- Fresh browser sessions (judges/automation) don’t have login cookies.
- Tableau Cloud can block iframe embeds via security headers (e.g., `X-Frame-Options: SAMEORIGIN`).

To make the demo “judge-proof,” we switched the default embed path to **Tableau Public**, and added a **cache-busting** script tag to prevent stale `app.js` from loading.

---

## Current Status (Verified: PASS)
Antigravity executed the full “golden path” dry run successfully.

### Dry Run Results
- **Cold Open:** PASS  
  `http://localhost:8082/index.html?v=22` loads with `API: ONLINE` and Tableau Public dashboard visible.
- **Run Audit:** PASS  
  ~10 actions populate with “Salesforce” and “Slack” tags.
- **Inspect Context:** PASS  
  “View context in Tableau” remains safe; iframe stays on Public URL and remains interactive.
- **Approve All:** PASS  
  Clears list and triggers success alert.
- **Audit Trail:** PASS  
  `/executions` shows logged approvals correctly.
- **Repeatability:** PASS  
  Reload → Run Audit again → actions repopulate.

### Artifact Created
- `c:\dev\Agentic-Analytics-Studio\README_DEMO.md`  
  Contains Canonical URL + runbook steps.

---

## What Changed (v22)
1) **`web/app.js`**
- Default behavior uses **Tableau Public** embed (no auth required).
- Optional dev toggle remains available if needed (`?tableau=cloud`), but **judge path stays Public**.

2) **`index.html`**
- Updated script tag to force reload of the patched JS:
  - `app.js?v=22`

---

## Canonical Demo URL (use this every time)
- `http://localhost:8082/index.html?v=22`

Reason: avoids stubborn browser caching that can silently revert behavior.

---

## “Done” Definition (for this hotfix)
✅ Demo is reliable locally  
✅ No Tableau login prompts  
✅ No “Refused to display” iframe errors  
✅ Approve-to-execute flow works  
✅ Audit trail proves governance loop  
✅ Repeatability confirmed  

---

## Next High-Impact Improvement (Deferred — requires user input)
### Replace the Placeholder Tableau Public Dashboard
Right now the embedded Public viz is the **Superstore_24** placeholder (used for stability). For maximum hackathon credibility, we should embed the **AAS-specific Tableau Public workbook/dashboard** by default.

#### What we need from the user to complete this
- Tableau Public **Share URL** for the AAS workbook (or the direct embed URL)
- The intended **sheet/dashboard name(s)** to map (e.g., `Overview`, `Pipeline`, `Risk`)

#### Implementation plan once provided
- Update `TABLEAU_PUBLIC_DEFAULT_URL` in `web/app.js`
- Update `TABLEAU_PUBLIC_VIEWS` mapping for named routes (optional)
- Re-verify `http://localhost:8082/index.html?v=22` still works and remains cookie-free

---

## Optional Hardening (only if time permits)
- Add an “Open in new tab” fallback link under the iframe (if not already present everywhere).
- Add a tiny “Embed failed → click to open Tableau” message if iframe load errors occur.

---

## Handoff Note
You are fully prepped for the live demo. Use the canonical `?v=22` URL and follow `README_DEMO.md`.
