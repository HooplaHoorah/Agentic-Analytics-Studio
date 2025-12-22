# NEXT PHASE (Tableau Hackathon) — Tableau Implementation Links + Build Plan (for Antigravity)

> **Context:** Phase 1/2 handoff is complete (AAS v2 snapshot + UPDATED DevPost/hackathon docs are committed to `main`).  
> **Objective:** Pivot to **Tableau Next–aligned** implementation while keeping a **Tableau Cloud fallback** ready, and deliver a **Grand Prize–caliber** golden-path demo.

---

## 0) What “done” looks like (Grand Prize golden path)

**Question → Semantic context → Tableau-powered insight + viz → ActionPlan → Human approval → Execute (Slack/Salesforce) → Audit log → Outcome shown in Tableau**

Minimum “judge-wow” requirements:
- Tableau is **not optional**: the insight is driven by Tableau assets (views/datasources/semantic model) and is **visible in a Tableau surface**.
- The experience feels like a **Decision Studio**: conversation + viz + actions + history in one place.
- At least **one real integration** executes (Slack or Salesforce). Everything else can be demo-safe.

---

## 1) Immediate next steps (do these first)

1) **Confirm hackathon-provided access** (Tableau Next / Salesforce org / Slack / Agentforce / data tooling).
2) **Pick the integration path**:
   - **Primary:** Tableau Next (semantic-first)  
   - **Fallback:** Tableau Cloud (API + embedding) — keeps the demo shippable even if Next access is bumpy.
3) Implement a **single hero play** end-to-end (Pipeline Leakage) before adding more plays.

---

## 2) Where to implement in the repo (suggested)

- `app/services/tableau_client.py`  
  Replace the current stub with real calls (Cloud now; Next when org resources are confirmed).
- `app/api.py`  
  Add endpoints that return “InsightCard + Viz reference” objects (AAP-lite).
- `app/executors/`  
  Keep the approvals/executions/audit loop; wire at least one real action channel.
- `web/` or `ui/` (new)  
  Decision Studio MVP UI: embed Tableau + show actions/history + run/approve.

---

## 3) Links — start here (stable entry points)

### Hackathon / DevPost
- Tableau Hackathon page: https://tableau2025.devpost.com/
- Devpost “Resources” tab: https://tableau2025.devpost.com/resources
- Devpost “Rules” tab: https://tableau2025.devpost.com/rules

### Tableau Developer Portal (Cloud + Embedding + APIs)
- Tableau Developers home: https://www.tableau.com/developer
- Tableau Developer docs hub: https://help.tableau.com/current/api/
- Tableau REST API: https://help.tableau.com/current/api/rest_api/en-us/REST/rest_api.htm
- Tableau Metadata API: https://help.tableau.com/current/api/metadata_api/en-us/index.html
- Tableau Webhooks: https://help.tableau.com/current/api/webhooks/en-us/index.html

### Tableau Embedding
- Tableau Embedding API (overview): https://help.tableau.com/current/api/embedding_api/en-us/index.html
- Embedding API reference / examples: https://tableau.github.io/embedding-api/

### Python + Tableau Cloud
- Tableau Server Client (TSC) library (Python):  
  Docs: https://tableau.github.io/server-client-python/  
  GitHub: https://github.com/tableau/server-client-python
- Personal Access Tokens (PATs) (auth concept):  
  Tableau Help search entry point: https://help.tableau.com/  *(search “Personal Access Token Tableau Cloud”)*

### Tableau Data / Hyper (optional, but useful for outcome writeback)
- Hyper API: https://help.tableau.com/current/api/hyper_api/en-us/index.html

---

## 4) Tableau Next / Salesforce ecosystem links (semantic-first route)

> **Note:** Tableau Next + Salesforce docs URLs sometimes move between releases. If a link 404s, use the provided search phrase on Salesforce Help or the Tableau Developer site.

### Salesforce Help (Tableau + Next entry points)
- Salesforce Help main: https://help.salesforce.com/
  - Search phrases:
    - **“Tableau Next”**
    - **“Tableau Semantics”**
    - **“Semantic Model Builder Tableau”**
    - **“Agentforce Tableau”**
    - **“Embedded analytics Tableau in Salesforce”**

### Agentforce
- Agentforce overview entry point: https://www.salesforce.com/artificial-intelligence/agentforce/
  - Search phrases on Salesforce Help:
    - **“Agentforce Developer Guide”**
    - **“Agentforce actions”**
    - **“Agentforce prompt templates”**

### Data Cloud / semantic governance (if required by the Next path)
- Data Cloud overview: https://www.salesforce.com/data/cloud/
  - Search phrases on Salesforce Help:
    - **“Data Cloud semantic model”**
    - **“Data Cloud permissions data spaces”**
    - **“Data Cloud data streams”**

---

## 5) Implementation plan (Tableau Cloud-first, Next-ready)

### A) Cloud-first “make it real” (fastest to working demo)
1) **Auth**
   - Use PAT or OAuth (Connected App) to sign in.
2) **Pull Tableau-driven context**
   - Choose ONE workbook/view as the canonical “Pipeline Risk” view.
   - Use REST API / TSC to:
     - list workbooks/views
     - get view details
     - (optional) query view data / underlying data
3) **Embed the viz**
   - Decision Studio UI embeds the view (Embedding API).
4) **Generate AAP-lite InsightCard**
   - Include:
     - link to viz
     - key metric values used for scoring
     - reason codes
5) **Approve → execute**
   - Make Slack real first (fast). Keep Salesforce demo-safe unless time allows.
6) **Outcome writeback**
   - Post-execution, append an “Outcome” record and publish back:
     - simplest: a CSV/JSON outcome file that Tableau reads
     - better: Hyper extract publish/update
   - Show “before/after” in a Tableau view.

### B) Next pivot when access is confirmed
Replace “datasource/view query” with “semantic model query” and ensure the InsightCard references governed semantic entities.
Deliverable: the agent’s explanation uses the same field/metric names as the semantic model.

---

## 6) Concrete tasks to file as issues (suggested)

### Must-have (Week 1)
- [ ] Implement Tableau sign-in + list sites/workbooks/views (TableauClient real)
- [ ] Embed 1 Tableau view in a minimal UI page
- [ ] Produce InsightCard with a working viz link + top 10 risky deals + reasons
- [ ] Slack integration: send message for 1 approved action (real)

### Should-have (Week 2)
- [ ] Add “Outcome” logging + Tableau view that visualizes executed actions/outcomes
- [ ] Add semantic mapping layer (Next-ready naming + IDs)

### Nice-to-have (Week 3)
- [ ] Salesforce task creation (real)
- [ ] Webhooks: refresh insight when Tableau data changes
- [ ] Second play end-to-end (only if hero play is rock-solid)

---

## 7) Guardrails (don’t lose time)

- Do **not** build 3 plays. Build **1** play to perfection.
- Do **not** spend cycles on packaging/build zips unless it fixes demo friction.
- Treat Tableau Next as the “innovation multiplier,” but keep the Cloud path shippable.

---

## 8) Quick command-line reminders (for humans)

- Keep secrets out of repo:
  - Use `.env` / secret manager
  - Provide `.env.example` with placeholders only
- Ensure a judge can run:
  - `pip install -r requirements.txt`
  - `uvicorn app.api:app --reload`
  - open UI + run the golden path

---

## 9) If links move (fast recovery plan)

If any docs link 404s, use:
- Tableau: https://help.tableau.com/ (search the doc title)
- Salesforce: https://help.salesforce.com/ (search phrases listed above)
- GitHub: search `tableau embedding api v3`, `server-client-python`, `tableau rest api query view data`

---

**Owner:** Antigravity (browser-enabled agent)  
**Priority:** Tableau Next pivot with Cloud fallback, golden path demo first.
