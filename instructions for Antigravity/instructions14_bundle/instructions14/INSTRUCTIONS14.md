# Instructions14 — Slack Channel Prep + Execute Walkthrough (v14)
Generated: 2025-12-22

You are **ready** for the next step: run the browser walkthrough in **execute mode** and **verify the Slack post**.

This v14 bundle adds:
- Slack channel discovery / (optional) create+join
- Execute-mode walkthrough that approves ONE Slack action and verifies the message appeared (by reading channel history)

## Outputs
- `instructions14/out/slack_prep.md`
- `instructions14/out/slack_prep.json`
- `instructions14/out/walkthrough_execute.md`
- `instructions14/out/walkthrough_execute.json`
- `instructions14/out/screenshots/*.png`

## Unzip location
Unzip into either:
- `repo-root/instructions14/` (preferred), OR
- `repo-root/instructions for Antigravity/instructions14/`

Scripts auto-detect repo root.

## Run
1) (Optional one-time) Setup Playwright
- mac/linux: `bash instructions14/scripts/1_setup.sh`
- windows: `powershell -ExecutionPolicy Bypass -File instructions14\scripts\1_setup.ps1`

2) Slack channel prep
- mac/linux: `bash instructions14/scripts/2_slack_prep.sh`
- windows: `powershell -ExecutionPolicy Bypass -File instructions14\scripts\2_slack_prep.ps1`

3) Execute walkthrough (posts ONE message)
- mac/linux: `bash instructions14/scripts/3_walkthrough_execute.sh`
- windows: `powershell -ExecutionPolicy Bypass -File instructions14\scripts\3_walkthrough_execute.ps1`

## What to send back
- `instructions14/out/slack_prep.md`
- `instructions14/out/walkthrough_execute.md`

## Demo checklist (what I want verified)
1) UI loads, and **Run** works
2) Tableau iframe appears
3) Actions list renders (at least Slack + Salesforce Task)
4) Approve Slack action → returns `success`
5) Slack message visible in chosen channel
