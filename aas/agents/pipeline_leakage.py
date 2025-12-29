"""Pipeline Leakage hero play implementation (stub).

This module defines `PipelineLeakageAgent`, a concrete subclass of
`AgentPlay` that demonstrates how to load a dataset, perform simple
analysis and generate follow‑up actions. The logic here is intentionally
rudimentary; replace it with more sophisticated analytics as you build
out the MVP.
"""

from __future__ import annotations

import datetime as _dt
import os
from importlib import resources
from typing import Any, Dict, List

import pandas as pd  # type: ignore

from .base import AgentPlay
from ..db import get_conn
from ..models.action import Action
from ..utils.logger import get_logger
from ..services.salesforce_client import SalesforceClient

logger = get_logger(__name__)


class PipelineLeakageAgent(AgentPlay):
    """Agent that identifies at‑risk deals and proposes follow‑ups."""

    def __init__(self):
        super().__init__()
        self.sf = SalesforceClient()

    def load_data(self) -> pd.DataFrame:
        """Load pipeline data.

        Preference order:
        1) Postgres ("live" demo) via DATABASE_URL + `aas_opportunities`.
        2) Packaged CSV fallback (static demo).
        """

        # 1) Live demo path: Postgres
        if os.getenv("DATABASE_URL"):
            try:
                conn = get_conn()
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT opportunity_id, owner, region, segment, stage, amount,
                               close_date, last_touch_date, stage_age_days
                        FROM aas_opportunities
                        WHERE stage NOT IN ('Closed Won','Closed Lost');
                        """
                    )
                    rows = cur.fetchall()
                conn.close()

                if rows:
                    df = pd.DataFrame(
                        rows,
                        columns=[
                            "opportunity_id",
                            "owner",
                            "region",
                            "segment",
                            "stage",
                            "amount",
                            "close_date",
                            "last_touch_date",
                            "stage_age",
                        ],
                    )
                    return df
            except Exception as e:
                logger.warning("Failed to load live data from Postgres; falling back to CSV. Error=%s", e)

        # 2) Static demo path: packaged CSV
        try:
            with resources.open_text("aas.data", "demo_pipeline_data.csv") as f:
                return pd.read_csv(f)
        except FileNotFoundError:
            logger.warning("demo_pipeline_data.csv not found; returning empty DataFrame")
            return pd.DataFrame()

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Identify at‑risk deals and basic pipeline statistics.

        Args:
            data: A DataFrame of opportunity records.

        Returns:
            A dict with keys:
            * `at_risk_deals`: list of deals flagged for attention.
            * `stage_distribution`: distribution of deals by stage.
            * `drivers_of_slowdown`: key insights into pipeline bottlenecks.
            * `narrative`: human‑readable summary of findings.
            * `metrics`: quantified impact metrics.
        """
        if data.empty:
            return {
                "at_risk_deals": [],
                "stage_distribution": {},
                "narrative": "No data available."
            }

        # Convert date columns for calculation
        today = _dt.date.today()
        for col in ["close_date", "last_touch_date"]:
            if col in data.columns:
                data[col] = pd.to_datetime(data[col], errors="coerce")

        if "amount" not in data.columns:
            data["amount"] = 0.0
        else:
            data["amount"] = data["amount"].astype(float)

        # 1) Calculate Risk Score (0-100) and Reasons
        data["risk_score"] = 0.0
        data["reasons"] = [[] for _ in range(len(data))]

        if "stage_age" in data.columns:
            # stage_age component: 1 point per day, capped at 40
            age_points = (data["stage_age"].fillna(0)).clip(0, 40)
            data["risk_score"] += age_points
            for idx, age in data["stage_age"].items():
                if age > 30:
                    data.at[idx, "reasons"].append(f"Stalled in stage {int(age)} days")

        if "last_touch_date" in data.columns:
            # days since last touch component: 2 points per day over 7 days, max 30
            days_since = (pd.Timestamp(today) - data["last_touch_date"]).dt.days.fillna(30)
            touch_points = ((days_since - 7).clip(0) * 2).clip(0, 30)
            data["risk_score"] += touch_points
            for idx, d in days_since.items():
                if d > 14:
                    data.at[idx, "reasons"].append(f"No activity in {int(d)} days")

        if "close_date" in data.columns:
            # close date slipped component: 30 points
            is_past = data["close_date"].dt.date < today
            data.loc[is_past, "risk_score"] += 30
            for idx, past in is_past.items():
                if past:
                    data.at[idx, "reasons"].append("Close date slipped")

        data["risk_score"] = data["risk_score"].clip(0, 100)

        # Filter out low risk (< 20 say) for impact analysis? Or just use "at risk" definition (score > 50)?
        # Let's say highly stalled = score > 50
        stalled_mask = data["risk_score"] > 50
        stalled_df = data[stalled_mask]

        # Impact Metrics
        num_stalled = len(stalled_df)
        value_at_risk = stalled_df["amount"].sum()
        avg_days_stalled = stalled_df["stage_age"].mean() if "stage_age" in stalled_df.columns and not stalled_df.empty else 0
        expected_recovered = value_at_risk * 0.7  # Assumption: can save 70%

        metrics = {
            "num_stalled_opportunities": int(num_stalled),
            "value_at_risk": float(value_at_risk),
            "avg_days_stalled": float(round(avg_days_stalled, 1)),
            "expected_revenue_recovered": float(expected_recovered)
        }

        # 2) Drivers of slowdown summary
        drivers = {}
        if "stage" in data.columns and "stage_age" in data.columns:
            drivers["slowest_stages"] = data.groupby("stage")["stage_age"].mean().sort_values(ascending=False).head(3).to_dict()
        
        if "owner" in data.columns:
            high_risk_df = data[data["risk_score"] > 50]
            drivers["top_high_risk_owners"] = high_risk_df["owner"].value_counts().head(3).to_dict()

        # 3) Stage distribution (existing)
        if "stage" in data.columns:
            stage_counts = data["stage"].value_counts().to_dict()
        else:
            stage_counts = {}

        # 4) Select top 5 at-risk deals
        at_risk_df = data.sort_values("risk_score", ascending=False).head(5).copy()
        
        # Convert dates to strings for JSON serialisation
        for col in ["close_date", "last_touch_date"]:
            if col in at_risk_df.columns:
                at_risk_df[col] = at_risk_df[col].dt.strftime('%Y-%m-%d')

        # Select a subset of fields to include in the result
        cols = [c for c in [
            "opportunity_id",
            "segment",
            "region",
            "stage",
            "owner",
            "stage_age",
            "amount",
            "close_date",
            "risk_score",
            "reasons",
        ] if c in at_risk_df.columns]
        at_risk_list = at_risk_df[cols].to_dict(orient="records")

        narrative = (
            f"Identified {len(at_risk_list)} deals at risk seeking attention. "
            f"Total value at risk is ${value_at_risk:,.0f} across {num_stalled} stalled opportunities. "
            f"Top drivers include stages: {', '.join(drivers.get('slowest_stages', {}).keys())}."
        )

        return {
            "at_risk_deals": at_risk_list,
            "stage_distribution": stage_counts,
            "drivers_of_slowdown": drivers,
            "narrative": narrative,
            "metrics": metrics,
            "visual_context": {
                "view_name": "Superstore Overview",
                "workbook": "Superstore",
                "url": "https://10ax.online.tableau.com/#/site/agenticanalyticsstudio/views/Superstore/Overview",
                "note": "Embedded Tableau context for this analysis"
            }
        }

    def recommend_actions(self, analysis: Dict[str, Any]) -> List[Action]:
        """Generate follow‑up actions for each at‑risk deal."""
        actions: List[Action] = []
        for deal in analysis.get("at_risk_deals", []):
            opp_id = deal.get("opportunity_id") or "unknown"
            owner = deal.get("owner") or "the owner"
            region = deal.get("region")
            segment = deal.get("segment")
            stage = deal.get("stage")
            score = deal.get("risk_score", 0)
            amount = deal.get("amount", 0)
            reasons = ", ".join(deal.get("reasons", []))

            # Trigger Salesforce Task Creation (REAL execution as requested per instruction)
            sf_res = self.sf.create_task(
                subject=f"Unblock Opportunity {opp_id}",
                description=f"Risk Score: {score}. Reasons: {reasons}. Please investigate.",
                owner_id=owner,  # In real life, convert Name -> ID or use current user
                what_id=opp_id
            )
            created_task_id = sf_res.get("id")

            # Generate AI Rationale
            context = f"Opportunity {opp_id}: Stage {stage}, Age {deal.get('stage_age')} days, Amount ${amount}, Risk Score {score}. Reasons: {reasons}."
            rationale = self.generate_rationale(context)
            
            # 1) Salesforce Task Action
            actions.append(Action(
                type="salesforce_task",
                title=f"Unblock Opportunity {opp_id} (${amount:,.0f})",
                description=f"Salesforce Task {created_task_id} created. Follow up with {owner}. Risk: {reasons}",
                priority="high" if score > 70 else "medium",
                impact_score=float(amount),
                reasoning=rationale,
                metadata={
                    "opportunity_id": opp_id,
                    "task_id": created_task_id,
                    "subject": f"Unstuck Deal: {opp_id}",
                    "owner": owner,
                    "region": region,
                    "segment": segment,
                    "stage": stage,
                    "due_date": (_dt.date.today() + _dt.timedelta(days=2)).isoformat()
                }
            ))
            
            # 2) Slack Message
            actions.append(Action(
                type="slack_message",
                title=f"Risk Alert: {opp_id}",
                description=f"Alert sales-ops regarding high risk deal {opp_id} ({score}% risk).",
                priority="medium",
                impact_score=float(amount * 0.1), # Heuristic: notification value? 
                reasoning=rationale,
                metadata={
                    "channel": "sales-alerts",
                    "text": f"⚠️ High risk deal {opp_id} (${amount:,.0f}) is stalled. Score: {score}%. Factors: {reasons}. Salesforce Task already created.",
                    "opportunity_id": opp_id,
                    "region": region,
                    "segment": segment,
                    "stage": stage,
                }
            ))

        # Sort actions by impact score descending
        actions.sort(key=lambda x: x.impact_score, reverse=True)
        return actions