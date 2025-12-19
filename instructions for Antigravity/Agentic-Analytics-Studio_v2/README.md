# Agentic Analytics Studio (AAS)

Agentic Analytics Studio (AAS) is an experimental “analytics‑to‑action” workspace.  
The goal of the studio is to take business questions or problems and transform them into actionable insights and operational tasks – all orchestrated by intelligent agents.  

This repository contains a **skeleton** implementation for the AAS hackathon project. It does not yet include any working integrations; rather it establishes a clear structure around which to build.  

For the hackathon demo runbook, see [README_DEMO.md](README_DEMO.md).

## Vision

AAS enables business users to ask questions like **“Why are my deals slipping?”** and receive:

1. **Analysis** – the agent clarifies assumptions, loads relevant data and generates metrics, charts and narratives.
2. **Recommendations** – suggested root causes and prioritised lists (e.g. at‑risk opportunities) based on the analysis.
3. **Actions** – concrete follow‑ups such as creating tasks in Salesforce, sending alerts to Slack or updating records.  

Unlike a dashboard, the Studio keeps context (datasets, decisions, actions) and provides guardrails (approvals, audit trails).  

## Hero Plays

To anchor the MVP, the project focuses on three “hero” use cases that directly impact the bottom line:

| Bullseye | Pain Point (Problem) | Example Outcome |
| --- | --- | --- |
| **Pipeline Leakage** (primary hero) | Deals quietly die in the pipeline and revenue slips without explanation. | Identify at‑risk deals and automatically generate follow‑up tasks in Salesforce. |
| **Churn Rescue** | Customers churn because signals are missed and no one coordinates a response. | Detect churn‑risk segments, surface drivers and queue retention outreach. |
| **Spend Anomaly** | Surprise spikes in spend are discovered too late to act. | Detect anomalies, attribute the root cause and trigger budget holds or notifications. |

Pick one hero play to demo end‑to‑end (e.g. **Pipeline Leakage**) and treat the others as “next plays” to show platform potential.

## Repository Structure

```
Agentic-Analytics-Studio/
├─ README.md           # high‑level project overview (this file)
├─ requirements.txt    # Python dependencies
├─ .gitignore          # common ignores for Python projects
├─ docs/               # documentation (specs, diagrams, etc.)
│   └─ HeroPlaySpec.md # description of hero plays and demo flows
├─ aas/                # application source code
│   ├─ __init__.py
│   ├─ main.py         # entry point to run the application/agent
│   ├─ agents/         # definitions of agent workflows
│   │   ├─ __init__.py
│   │   ├─ base.py     # base class for all agents
│   │   ├─ pipeline_leakage.py  # stub for the Pipeline Leakage play
│   │   ├─ churn_rescue.py      # stub for the Churn Rescue play
│   │   └─ spend_anomaly.py     # stub for the Spend Anomaly play
│   ├─ services/       # clients to external systems (Tableau, Salesforce, Slack)
│   │   ├─ __init__.py
│   │   ├─ tableau_client.py
│   │   ├─ salesforce_client.py
│   │   └─ slack_client.py
│   ├─ models/         # data models and play definitions
│   │   ├─ __init__.py
│   │   ├─ play.py
│   │   └─ action.py
│   ├─ utils/
│   │   ├─ __init__.py
│   │   └─ logger.py   # simple logging utility
│   └─ data/
│       ├─ __init__.py
│       └─ demo_pipeline_data.csv  # sample dataset for the pipeline leakage play
└─ tests/              # unit tests (empty for now)
```

To get started, clone this repository and install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

You can then explore the stubbed plays in `aas/agents` and run the application via the `main.py` script.  
Each agent returns structured results for analysis and actions, but you’ll need to implement the logic and integrate with your data sources (e.g. Tableau, Salesforce) to make it fully functional.

## Contributing

Feel free to open issues or pull requests as you flesh out features. Use the `docs/` folder to capture additional specifications, diagrams or design notes.
