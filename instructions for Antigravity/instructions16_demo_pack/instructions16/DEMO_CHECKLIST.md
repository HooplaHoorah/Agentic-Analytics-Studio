# Demo Checklist

## Before the judges arrive
- [ ] Repo on `feat/pipeline-risk-and-execution`
- [ ] `.env` present in repo root
- [ ] Slack channel exists: `#aas-test`
- [ ] Bot is in channel: `/invite @aasbot`
- [ ] Run `instructions16/scripts/2_launch_demo` and confirm:
  - [ ] API responds: `/health`
  - [ ] Web loads: `/index.html`
- [ ] Open Slack channel in a visible tab/window
- [ ] Keep Tableau embed visible on screen (if possible)

## During the demo
- [ ] Start at the app homepage
- [ ] Click **Run**
- [ ] Wait for Tableau iframe + actions to render
- [ ] Click **Approve** on a Slack action
- [ ] Switch to Slack immediately to show the message

## If anything goes sideways
- [ ] Refresh the page and click Run again
- [ ] Confirm API is alive: `http://127.0.0.1:8000/health`
- [ ] Confirm Slack channel exists + bot is a member
