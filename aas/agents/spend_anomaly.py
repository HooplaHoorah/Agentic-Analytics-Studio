"""Spend Anomaly hero play implementation (stub).

Reuse pipeline data for now to simulate vendor/spend anomalies.
"""
from __future__ import annotations
import datetime as _dt
from typing import Any, Dict, List

from .pipeline_leakage import PipelineLeakageAgent
from ..models.action import Action
from ..utils.logger import get_logger

logger = get_logger(__name__)

class SpendAnomalyAgent(PipelineLeakageAgent):
    """Agent that identifies unusual spend patterns."""

    def analyze(self, data: Any) -> Dict[str, Any]:
        result = super().analyze(data)
        
        # Override visual context for this play
        result["visual_context"] = {
            "view_name": "Spend Anomaly",
            "workbook": "Superstore",
            "url": "https://10ax.online.tableau.com/#/site/agenticanalyticsstudio/views/Spend/Anomaly", # Placeholder
            "note": "Embedded Spend Anomaly View"
        }
        return result

    def recommend_actions(self, analysis: Dict[str, Any]) -> List[Action]:
        actions: List[Action] = []
        for deal in analysis.get("at_risk_deals", []):
            opp_id = deal.get("opportunity_id") or "unknown"
            owner = deal.get("owner") or "finance manager"
            score = deal.get("risk_score", 0)
            amount = deal.get("amount") or 0
            
            # Simulate "Anomaly" by treating high risk deals as high variance spend
            reasons = ", ".join(deal.get("reasons", []))
            region = deal.get("region")
            segment = deal.get("segment")
            stage = deal.get("stage")

            # 1) Contract Review Task
            actions.append(Action(
                type="salesforce_task",
                title=f"Review Vendor Contract: {opp_id}",
                description=f"Investigate spend variance for vendor {opp_id}. Amount: ${amount}. Score: {score}.",
                priority="high" if score > 80 else "medium",
                metadata={
                    "opportunity_id": opp_id,
                    "subject": f"Vendor Spend Review: {opp_id}",
                    "owner": owner,
                    "region": region,
                    "segment": segment,
                    "stage": stage,
                    "due_date": (_dt.date.today() + _dt.timedelta(days=3)).isoformat()
                }
            ))
            
            # 2) Slack Alert
            actions.append(Action(
                type="slack_message",
                title=f"Spend Alert: {opp_id}",
                description=f"Automated alert for unusual spend pattern on {opp_id}.",
                priority="medium",
                metadata={
                    "channel": "finance-alerts",
                    "text": f"💸 Spend Anomaly detected for {opp_id}. Amount: ${amount}. Variance Score: {score}. Please investigate.",
                    "opportunity_id": opp_id,
                    "region": region,
                    "segment": segment,
                    "stage": stage,
                }
            ))
        return actions