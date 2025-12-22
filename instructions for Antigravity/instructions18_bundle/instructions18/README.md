# Instructions 18 — Tableau Session-Expired Banner (Demo Guard)

## Goal
If Tableau fails to render inside the embedded panel (often due to an expired Tableau session causing a redirect),
show a **friendly banner** with:
- **Open in new tab** (authenticate)
- **Retry**
- **Dismiss**

## What it does
- Injects a small JS guard into `index.html` (any AAS demo page it finds)
- The guard:
  - watches the Tableau `<iframe>` for `src` changes
  - starts a load timer (default 8s)
  - if the iframe never loads, shows the banner
  - if `src` looks like a login route (`/signin`, `/login`, `auth`, `sso`) it shows the banner immediately
  - on successful `load`, hides the banner

## Apply (Windows / PowerShell)
From repo root:
```powershell
powershell -ExecutionPolicy Bypass -File instructions18/scripts/1_apply_v18.ps1
```

## Apply (macOS/Linux)
From repo root:
```bash
bash instructions18/scripts/1_apply_v18.sh
```

## Verify
1) Start demo UI
2) Click **Run**
3) If Tableau loads: banner should not appear.
4) To simulate session expiry: open an incognito window and run the demo — you should see the banner.
   Click **Open in new tab**, sign in, then hit **Retry**.
