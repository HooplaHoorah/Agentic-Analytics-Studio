# Hero Play Specifications

This document outlines the three high‑level “hero plays” envisioned for the Agentic Analytics Studio (AAS). Each play takes a common pain point and turns it into a repeatable analytics‑to‑action workflow. These specs are intentionally light on implementation details – they exist to guide the design of agents, data models and UI flows.

## 1. Pipeline Leakage (Primary Hero)

**Problem:** Revenue slips because deals quietly die in the sales pipeline. Leaders ask, “Why are we behind and what should we do?” Analysts produce reports but the follow‑through is manual and often lost.

**Inputs:**
* Opportunity data – stage, amount, close date, owner, age in stage
* Activity signals – last touch date, meeting counts, emails sent (can be mocked)

**Agent Steps:**
1. Load pipeline data and basic activity metrics.
2. Identify at‑risk deals (e.g. stalled stage, no recent activity, slipped close date).
3. Surface top drivers of pipeline slowdown (segments, reps, stages, products).
4. Generate a prioritised list of at‑risk deals with reasons.
5. Recommend actions (e.g. schedule a follow‑up, involve manager, adjust forecast) and prepare Salesforce tasks / notifications.

**Outputs:**
* “Top X at‑risk deals” with explanatory text.
* “Top drivers of slowdown” in plain language and optionally as charts.
* Suggested actions for each deal.

**Actions:**
* Create Salesforce tasks for deal owners (with specific next steps).
* Escalate certain deals via Slack or email to managers.
* Post a summary to a channel for awareness.

## 2. Churn Rescue

**Problem:** Customers churn because early warning signals are missed and no one coordinates the response. Teams see “churn up” on dashboards but the root causes and follow‑ups are unclear.

**Inputs:**
* Customer health data – usage metrics, NPS scores, support tickets
* Subscription metadata – tenure, plan type, renewal date

**Agent Steps:**
1. Segment customers by usage and health indicators.
2. Identify churn‑risk segments and quantify impact.
3. Explain drivers (e.g. drop in usage, negative feedback, unresolved issues).
4. Generate personalised retention actions (offers, outreach campaigns, CSM playbooks).

**Outputs:**
* List of at‑risk customers by segment.
* Narrative explanation of churn drivers.
* Retention play suggestions.

**Actions:**
* Queue customer success tasks for high‑risk accounts.
* Trigger marketing emails or offers.
* Escalate severe cases to account managers.

## 3. Spend Anomaly

**Problem:** Surprise spikes in spend (cloud, marketing, procurement) are discovered too late, causing budget overruns. Anomalies may be hidden across departments or vendors.

**Inputs:**
* Transaction or billing data – timestamps, categories, vendors, amounts
* Budget/forecast baselines (optional)

**Agent Steps:**
1. Ingest spend data and establish normal patterns (seasonality, average spend by category).
2. Detect anomalies (spikes or drops) across categories or vendors.
3. Attribute root causes (e.g. new user acquisition campaign, unexpected usage, fraudulent charges).
4. Summarise the financial impact and urgency.
5. Propose remedial actions (hold budget, negotiate discounts, investigate fraud, adjust forecast).

**Outputs:**
* Table of anomalies with magnitude and explanation.
* Visual charts highlighting spikes.
* Recommended next steps.

**Actions:**
* Open tickets with Finance/Procurement.
* Notify budget owners.
* Pause or adjust spend in the system (where supported).

---

These specifications should be considered living documents. As you implement the plays, refine the steps, inputs and outputs. Keep the hero flows concise – they should fit within a 5‑minute demo and clearly show how AAS turns insight into action.