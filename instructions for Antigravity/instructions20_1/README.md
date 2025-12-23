# Instructions 20 — file:// Guard (Prevent "Origin null" Demo Breakage)

## Problem
If someone opens `web/index.html` directly from disk (URL begins with `file:///...`), Chrome treats the page origin as `null`.
This causes:
- fetch/CORS errors when the page tries to load `app.js`
- Tableau embed `postMessage` origin mismatch errors
- noisy cross-origin iframe access errors

## Fix
Inject a small UI guard that detects `window.location.protocol === 'file:'` and shows a clear banner:
- "You must serve the app over http://localhost"
- button to open `http://localhost:5173/index.html`
- reminder to run the one-command launcher

## Apply (Windows / PowerShell)
From repo root:
```powershell
powershell -ExecutionPolicy Bypass -File instructions20/scripts/1_apply_v20.ps1
```

## Apply (macOS/Linux)
From repo root:
```bash
bash instructions20/scripts/1_apply_v20.sh
```

## Verify
1) Double-click `web/index.html` (file://) → banner appears.
2) Start demo normally (http://) → banner does not appear.
