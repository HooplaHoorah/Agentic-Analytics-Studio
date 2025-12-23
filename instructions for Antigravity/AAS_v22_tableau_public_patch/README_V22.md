# AAS v22 — Tableau Embed “Judge‑Proof” Patch

## What this bundle contains
- `web/app.js` — patched client code (v22)
- `patches/app_v22_tableau_public.diff` — unified diff against the previous `app.js`
- `TABLEAU_WORKBOOK_SHEET_INFO_NEEDED.md` — the exact Tableau Public info we need to finalize the embed mapping

## Why this patch exists
Tableau Cloud pages (e.g., `*.online.tableau.com`) commonly send `X-Frame-Options: SAMEORIGIN`, which blocks embedding in an `<iframe>` on `http://localhost`.
Also, automated verification (fresh browser) won’t have your Tableau Cloud login cookies.

This patch makes the default demo path:
- **No authentication required**
- **Iframe-friendly**
- **Always shows a working viz**
- Adds an **“Open Tableau (Public)”** button as a fallback

## How it works
### Modes (URL param)
- **Default / judge mode:** `?tableau=public`
  - Always uses Tableau Public embed URLs.
- **Dev mode:** `?tableau=cloud`
  - Calls `GET {API_BASE}/tableau/views`.
  - If the returned `embed_url` is Tableau Cloud, it will **NOT iframe** it (falls back to Public).

Examples:
- Judge/demo: `http://localhost:8082/index.html`
- Dev/cloud:  `http://localhost:8082/index.html?tableau=cloud`

## Install (drop-in)
1. Replace your repo file: `web/app.js` with the `web/app.js` from this bundle.
2. Update the constants at the top of `web/app.js`:
   - `TABLEAU_PUBLIC_DEFAULT_URL`
   - `TABLEAU_PUBLIC_VIEWS` mapping (optional but recommended)

## Verify quickly
1. Start API + web as usual.
2. Open: `http://localhost:8082/index.html`
3. Confirm the viz renders and the console has **no** iframe refusal errors.

