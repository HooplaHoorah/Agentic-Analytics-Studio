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

### A. Run Analysis
1. Click **"Run Pipeline Audit"**.
2. *Narrative*: "The agent analyzes 50,000+ Salesforce records and recent Slack chatter..."
3. **Verify**:
   - ~10 Recommended Actions appear in the right panel.
   - Badge says "10 PENDING".

### B. Inspect & Context (Trust)
1. Pick any action (preferably one labeled "Salesforce").
2. Click **"View context in Tableau"**.
3. *Narrative*: "The agent links the insight directly to the relevant dashboard view..."
4. **Verify**:
   - The Tableau dashboard refreshes/filters.
   - **Crucial**: The iframe stays visible.

### C. Execution & Governance
1. Click **"Approve All"**.
2. Wait for the success alert: "Successfully executed 10 actions!"
3. **Verify**:
   - List clears ("0 PENDING").
   - Audit trail is updated (backend).

### D. Repeatability (Optional)
1. Refresh the page (Cmd+R / F5).
2. Click **"Run Pipeline Audit"** again.
3. Verify actions repopulate immediately.

---

## 3. Trouble Spots & Mitigations

| Issue | Mitigation |
|-------|------------|
| **Tableau loads blank** | Confirm you are using `?v=23`. Check if `tableau.embedding.3.latest.min.js` loaded (network tab). |
| **"Refused to display..."** | You are likely in `?tableau=cloud` mode without an active session. Switch to standard URL (Option A) or log in to Tableau Cloud in another tab. |
| **"API: OFFLINE"** | Check the terminal running `uvicorn`. Restart it if needed. |

---
*Runbook generated: 2025-12-23*
