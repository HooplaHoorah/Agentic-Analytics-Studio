# Agentic Analytics Studio: Demo Runbook

This document outlines the **Golden Path** for the demo presentation.

## 1. Preparation (Canonical URL)

### Option A: Judge-Safe (Default)
**URL**: [http://localhost:8082/?v=23](http://localhost:8082/?v=23)  
*Use this if you are presenting to others who are NOT logged into your Tableau Cloud account.*
- **Backend**: Uses Tableau Public (Superstore placeholder)
- **Status**: ✅ **Verified Stable**

### Option B: Authenticated Presenter (Advanced)
**URL**: [http://localhost:8082/?v=23&tableau=cloud](http://localhost:8082/?v=23&tableau=cloud)  
*Use this ONLY if you have an active login to Tableau Cloud (`10ax.online.tableau.com`) in your browser.*
- **Backend**: Uses REAL Tableau Cloud views via API (`/tableau/views`)
- **Status**: ⚠️ **Requires Auth** (Will fail with `Refused to display` if not logged in)

> **Critically Important**: Always use the `?v=23` (or higher) parameter. This bypasses browser caching.

**Pre-flight Checklist**:
- API is running (`uvicorn aas.api:app --reload` on port 8000)
- Web server is running (`python -m http.server 8082` on port 8082)
- Browser: Top-right status says **"API: ONLINE"** (Green)

---

## 2. The Golden Path (Step-by-Step)

### A. Run Analysis (AI & Impact)
1. Click **"Run Pipeline Audit"**.
2. *Narrative*: "The agent analyzes 50,000+ records, identifies risks, and uses **Generative AI** to explain *why* each action is needed."
3. **Verify**:
   - Badge updates (e.g., "10 PENDING").
   - **Impact Scores**: High-value items are flagged (e.g. green "Impact: 0.98" badge).
   - **AI Rationale**: Each card shows unique reasoning (e.g. "Deal stalling at Proposal stage...").

### B. Inspect & Context (Trust)
1. Pick any action.
2. Click **"View context in Tableau"**.
3. *Narrative*: "The agent links the insight directly to the relevant dashboard view..."
4. **Verify**:
   - The Tableau dashboard refreshes/filters to the specific **Region/Segment**.

### C. Execution & Governance (Closed Loop)
1. Click **"Approve All"**.
2. Wait for the success alert.
3. *Narrative*: 
   - "If Salesforce/Slack are connected, real tasks are created."
   - "If not, the system runs in **Mock Mode**, simulating the API calls for demo reliability."
4. **Verify**:
   - List clears.
   - `data/actions_feedback_log.csv` is updated (backend evidence).

### D. Repeatability
1. Use the **Play Selector** (top left) to switch to "Churn Rescue".
2. Run again to show multi-agent capability.

---

## 3. Trouble Spots & Mitigations

| Issue | Mitigation |
|-------|------------|
| **Tableau loads blank** | Confirm you are using `?v=23`. Check if `tableau.embedding.3.latest.min.js` loaded (network tab). |
| **"Refused to display..."** | You are likely in `?tableau=cloud` mode without an active session. Switch to standard URL (Option A) or log in to Tableau Cloud in another tab. |
| **"API: OFFLINE"** | Check the terminal running `uvicorn`. Restart it if needed. |

---
*Runbook generated: 2025-12-23*
