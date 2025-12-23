# Instructions 19 — Tableau Iframe Guard+ (X-Frame-Options Safe)

## Why this exists
Some runs can accidentally set the Tableau iframe `src` to the Tableau *site root* (e.g. `https://10ax.online.tableau.com/`).
That root page is **not embeddable** and triggers the console error:

- `Refused to display ... in a frame because it set 'X-Frame-Options' to 'sameorigin'.`

This happens most often when the API is offline (e.g. backend not running on `127.0.0.1:8000`), so the UI falls back.

## What this patch does
- Adds a **client-side guard** that watches the Tableau iframe `src`.
- If the iframe is pointed at a Tableau URL that **does not look like a view** (missing `/views/`),
  it immediately resets the iframe to `about:blank` and shows a banner with:
  - Open in new tab (so you can re-auth if needed)
  - Retry
  - Dismiss
- Does **not** attempt to read inside the iframe (avoids cross-origin `SecurityError`).

## Apply
Unzip into repo root, creating `instructions19/`.

### Windows
```powershell
powershell -ExecutionPolicy Bypass -File instructions19/scripts/1_apply_v19.ps1
```

### Mac/Linux
```bash
bash instructions19/scripts/1_apply_v19.sh
```

## Verify (quick)
1. Start backend (must be running): `uvicorn aas.api:app --reload`
2. Open the UI.
3. Click **Run Pipeline Audit**.
4. Confirm:
   - No `X-Frame-Options` iframe refusal errors.
   - If the API is offline, you see the banner and the iframe stays blank.
