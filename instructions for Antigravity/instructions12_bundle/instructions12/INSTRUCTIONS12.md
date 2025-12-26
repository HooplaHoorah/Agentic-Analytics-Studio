# Instructions12 — Phase 2 “Real Mode” Demo-Runner + PASS/FAIL Report
Generated: 2025-12-22

This v12 bundle creates a **PASS/FAIL demo report** and can optionally do a **real approve→execute** test.

Unzip into either:
- `repo-root/instructions12/` (preferred), or
- `repo-root/instructions for Antigravity/instructions12/`

All scripts auto-detect the repo root.

## Safety
- Do **not** commit `.env`.
- Reports go to `instructions12/out/`.

Suggested `.gitignore`:
```
.env
*.env
instructions12/out/
instructions for Antigravity/**/out/
data/
*.jsonl
```

## Run order
1) Start API (with env loaded):
- Mac/Linux: `bash instructions12/scripts/2_run_api.sh`
- Windows: `powershell -ExecutionPolicy Bypass -File instructions12\scripts\2_run_api.ps1`

2) DRY run (no Slack post):
- Mac/Linux: `bash instructions12/scripts/3_demo_runner_dry.sh`
- Windows: `powershell -ExecutionPolicy Bypass -File instructions12\scripts\3_demo_runner_dry.ps1`

3) EXECUTE run (posts ONE Slack message to test channel):
- Mac/Linux: `bash instructions12/scripts/4_demo_runner_execute.sh`
- Windows: `powershell -ExecutionPolicy Bypass -File instructions12\scripts\4_demo_runner_execute.ps1`

Send back:
- `instructions12/out/demo_report.md`
