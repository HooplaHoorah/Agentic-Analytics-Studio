# Instructions 16 — Demo Pack (Launcher + Safe Evidence Report)
Generated: 2025-12-22

This pack is optimized for a **hackathon / judge demo**: fast startup, predictable flow, and sharable evidence output.

## What you get
1) **One-command launcher** (starts backend + serves frontend + opens the demo URL)
2) **Safe evidence report** (redacts secrets, captures API snapshots, optional screenshots)
3) **Talk track + checklist** for a clean “wow” run

---

## Unzip location
Unzip into repo root so the folder exists at:
- `repo-root/instructions16/`

---

## Prereqs
- You’re on the branch with Real Mode wired: `feat/pipeline-risk-and-execution`
- `.env` exists in repo root and has working Tableau + Slack credentials
- Python 3.10+ recommended

---

## 1) Setup (one-time)
### Windows (PowerShell)
```powershell
cd instructions16
.\scripts_setup.ps1
```

### Mac/Linux
```bash
cd instructions16
bash scripts/1_setup.sh
```

---

## 2) Launch the demo (one command)
This starts:
- API at `http://127.0.0.1:8000`
- Web at `http://localhost:5173/index.html`
and opens your browser.

### Windows (PowerShell)
```powershell
cd instructions16
.\scripts_launch_demo.ps1
```

### Mac/Linux
```bash
cd instructions16
bash scripts/2_launch_demo.sh
```

Stop with **Ctrl+C** in the terminal window.

---

## 3) Generate a safe evidence report (for submission)
Default is **DRY** (no Slack post). It will:
- `/health`
- `/tableau/views` (count + embed_url presence)
- `/run/pipeline` (action counts)
- optional Playwright screenshots if installed

### Windows (PowerShell)
```powershell
cd instructions16
.\scripts_generate_evidence.ps1
```

### Mac/Linux
```bash
cd instructions16
bash scripts/3_generate_evidence.sh
```

Outputs:
- `instructions16/out/evidence_report.md`
- `instructions16/out/evidence_artifacts.json`
- `instructions16/out/screenshots/*.png` (if Playwright available)

---

## Optional: include a real Slack post in the evidence run
Set:
- `AAS_EVIDENCE_EXECUTE_SLACK=1`
- `AAS_SLACK_CHANNEL=#aas-test` (or another channel)

Example (PowerShell):
```powershell
$env:AAS_EVIDENCE_EXECUTE_SLACK="1"
$env:AAS_SLACK_CHANNEL="#aas-test"
.\scripts_generate_evidence.ps1
```

---

## Demo URL
- `http://localhost:5173/index.html`

---

## What to send back (if needed)
- `instructions16/out/evidence_report.md`
