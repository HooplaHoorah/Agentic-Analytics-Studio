# Instructions 21 — Demo Console Cleanup + Safe DOM Wrapper (v21)

## Goal
Make the demo experience calm and deterministic for judges:
- Reduce scary-but-harmless console noise caused by cross-origin iframe protections.
- Prevent optional/debug DOM inspection helpers from throwing cross-origin errors.
- Add an inline SVG favicon to eliminate 404 noise.

This does **not** change backend logic. It is demo UX polish only.

## What it does
Patches `index.html` (AAS UI pages) by injecting:
1) **A safe wrapper** around any `buildDomTree`-style helper that may throw when touching cross-origin iframes.
2) **A console sanitizer** that filters a short allowlist of known-benign errors.
3) **Inline favicon** to avoid `favicon.ico` 404.

## Apply (Windows / PowerShell)
From repo root:
```powershell
powershell -ExecutionPolicy Bypass -File instructions21/scripts/1_apply_v21.ps1
```

## Apply (macOS/Linux)
From repo root:
```bash
bash instructions21/scripts/1_apply_v21.sh
```

## Verify
1) Start demo normally over HTTP (use your launcher).
2) Open DevTools console.
3) Click **Run Pipeline Audit**.
Expected:
- No repeating scary "Blocked a frame…" spam.
- Tableau failures are handled by the user-facing banner (v18/v19), not console chaos.
