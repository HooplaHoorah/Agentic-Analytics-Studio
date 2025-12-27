"""Churn Rescue hero play implementation (stub).

Reuse pipeline data for now to simulate customer health risks.
"""
from __future__ import annotations
import datetime as _dt
from typing import Any, Dict, List

from .pipeline_leakage import PipelineLeakageAgent
from ..models.action import Action
from ..utils.logger import get_logger

logger = get_logger(__name__)

class ChurnRescueAgent(PipelineLeakageAgent):
    """Agent that identifies customers at risk of churn."""

    def analyze(self, data: Any) -> Dict[str, Any]:
        result = super().analyze(data)
        
        # Override visual context for this play
        result["visual_context"] = {
            "view_name": "Churn Rescue",
            "workbook": "Superstore",
            "url": "https://10ax.online.tableau.com/#/site/agenticanalyticsstudio/views/Churn/Rescue", # Placeholder, updated via API logic
            "note": "Embedded Churn Rescue View"
        }
        return result

    def recommend_actions(self, analysis: Dict[str, Any]) -> List[Action]:
        actions: List[Action] = []
        for deal in analysis.get("at_risk_deals", []):
            opp_id = deal.get("opportunity_id") or "unknown"
            owner = deal.get("owner") or "account manager"
            score = deal.get("risk_score", 0)
            reasons = ", ".join(deal.get("reasons", []))
            region = deal.get("region")
            segment = deal.get("segment")
            stage = deal.get("stage")

            # 1) Retention Call Task
            actions.append(Action(
                type="salesforce_task",
                title=f"Retention Call: {opp_id}",
                description=f"Schedule urgent retention review with {owner}. Health score: {100-score} (Risk: {score}%).",
                priority="high" if score > 70 else "medium",
                metadata={
                    "opportunity_id": opp_id,
                    "subject": f"Retention Risk Review: {opp_id}",
                    "owner": owner,
                    "region": region,
                    "segment": segment,
                    "stage": stage,
                    "due_date": (_dt.date.today() + _dt.timedelta(days=1)).isoformat()
                }
            ))
            
            # 2) Slack Alert
            actions.append(Action(
                type="slack_message",
                title=f"Churn Risk: {opp_id}",
                description=f"Notify CS team of potential churn risk for {opp_id}.",
                priority="medium",
                metadata={
                    "channel": "customer-success",
                    "text": f"🚨 High Churn Risk detected for account {opp_id}. Risk Score: {score}. Factors: {reasons}",
                    "opportunity_id": opp_id,
                    "region": region,
                    "segment": segment,
                    "stage": stage,
                }
            ))
        return actions