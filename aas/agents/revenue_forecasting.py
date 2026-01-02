"""Revenue Forecasting Agent - Predicts revenue shortfalls and suggests proactive actions."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd
from datetime import datetime, timedelta

from .base import AgentPlay
from ..models.action import Action
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RevenueForecastingAgent(AgentPlay):
    """Analyzes historical deal velocity and pipeline health to forecast revenue shortfalls.
    
    This agent:
    1. Loads historical deal data (close dates, amounts, stages)
    2. Calculates deal velocity and win rates by segment/region
    3. Forecasts expected revenue vs. target
    4. Identifies shortfalls and recommends proactive actions
    """

    def __init__(self):
        self.params = {}
        self.target_revenue = None
        self.forecast_period_days = 90  # Default 90-day forecast

    def load_data(self) -> pd.DataFrame:
        """Load historical deal data for forecasting."""
        # Try to load from params first (for testing), then fall back to CSV
        if "data" in self.params:
            return pd.DataFrame(self.params["data"])
        
        # Load from sample dataset
        data_path = Path(__file__).parent.parent / "sample_data" / "revenue_forecast_data.csv"
        
        if not data_path.exists():
            logger.warning(f"Revenue forecast data not found at {data_path}, using mock data")
            return self._generate_mock_data()
        
        try:
            df = pd.read_csv(data_path)
            logger.info(f"Loaded {len(df)} deals from {data_path}")
            return df
        except Exception as e:
            logger.error(f"Failed to load revenue data: {e}")
            return self._generate_mock_data()

    def _generate_mock_data(self) -> pd.DataFrame:
        """Generate realistic mock deal data for demo purposes."""
        import random
        from datetime import datetime, timedelta
        
        stages = ["Prospecting", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
        regions = ["North America", "EMEA", "APAC", "LATAM"]
        segments = ["Enterprise", "Mid-Market", "SMB"]
        
        deals = []
        base_date = datetime.now() - timedelta(days=180)
        
        for i in range(200):
            close_date = base_date + timedelta(days=random.randint(0, 270))
            stage = random.choice(stages)
            
            # Simulate realistic deal progression
            if close_date < datetime.now() - timedelta(days=90):
                stage = random.choice(["Closed Won", "Closed Lost"])
            
            deal = {
                "opportunity_id": f"OPP-{1000 + i}",
                "opportunity_name": f"Deal {i+1}",
                "amount": random.randint(10, 500) * 1000,
                "close_date": close_date.strftime("%Y-%m-%d"),
                "stage": stage,
                "probability": self._stage_to_probability(stage),
                "region": random.choice(regions),
                "segment": random.choice(segments),
                "owner": f"Rep {random.randint(1, 10)}",
                "created_date": (close_date - timedelta(days=random.randint(30, 120))).strftime("%Y-%m-%d"),
            }
            deals.append(deal)
        
        return pd.DataFrame(deals)

    def _stage_to_probability(self, stage: str) -> int:
        """Map stage to probability percentage."""
        stage_prob = {
            "Prospecting": 10,
            "Qualification": 25,
            "Proposal": 50,
            "Negotiation": 75,
            "Closed Won": 100,
            "Closed Lost": 0,
        }
        return stage_prob.get(stage, 50)

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze pipeline health and forecast revenue."""
        if data is None or len(data) == 0:
            return {"error": "No data available for analysis"}
        
        # Convert dates to datetime
        data["close_date"] = pd.to_datetime(data["close_date"])
        data["created_date"] = pd.to_datetime(data["created_date"])
        
        # Set forecast parameters
        today = datetime.now()
        forecast_end = today + timedelta(days=self.forecast_period_days)
        
        # Filter to relevant deals (open or recently closed)
        pipeline = data[
            (data["stage"].isin(["Prospecting", "Qualification", "Proposal", "Negotiation"])) |
            ((data["stage"] == "Closed Won") & (data["close_date"] >= today - timedelta(days=180)))
        ].copy()
        
        # Calculate weighted pipeline (amount * probability)
        pipeline["weighted_amount"] = pipeline["amount"] * pipeline["probability"] / 100
        
        # Forecast by segment
        forecast_by_segment = pipeline.groupby("segment").agg({
            "amount": "sum",
            "weighted_amount": "sum",
            "opportunity_id": "count"
        }).rename(columns={"opportunity_id": "deal_count"})
        
        # Calculate historical win rate
        historical = data[data["stage"].isin(["Closed Won", "Closed Lost"])]
        if len(historical) > 0:
            win_rate = len(historical[historical["stage"] == "Closed Won"]) / len(historical)
        else:
            win_rate = 0.5  # Default assumption
        
        # Calculate average deal velocity (days from created to close)
        closed_won = data[data["stage"] == "Closed Won"].copy()
        if len(closed_won) > 0:
            closed_won["days_to_close"] = (closed_won["close_date"] - closed_won["created_date"]).dt.days
            avg_velocity = closed_won["days_to_close"].mean()
        else:
            avg_velocity = 60  # Default assumption
        
        # Forecast revenue (weighted pipeline * historical win rate)
        forecasted_revenue = pipeline["weighted_amount"].sum() * win_rate
        
        # Get target from params or use default
        target_revenue = self.params.get("target_revenue", forecasted_revenue * 1.2)
        
        # Calculate shortfall
        shortfall = target_revenue - forecasted_revenue
        shortfall_pct = (shortfall / target_revenue * 100) if target_revenue > 0 else 0
        
        # Identify at-risk segments (below target)
        segment_targets = {
            "Enterprise": target_revenue * 0.5,
            "Mid-Market": target_revenue * 0.3,
            "SMB": target_revenue * 0.2,
        }
        
        at_risk_segments = []
        for segment, target in segment_targets.items():
            if segment in forecast_by_segment.index:
                actual = forecast_by_segment.loc[segment, "weighted_amount"] * win_rate
                if actual < target:
                    at_risk_segments.append({
                        "segment": segment,
                        "target": target,
                        "forecast": actual,
                        "gap": target - actual,
                    })
        
        return {
            "forecast_period_days": self.forecast_period_days,
            "target_revenue": target_revenue,
            "forecasted_revenue": forecasted_revenue,
            "shortfall": shortfall,
            "shortfall_pct": shortfall_pct,
            "win_rate": win_rate,
            "avg_deal_velocity_days": avg_velocity,
            "total_pipeline_value": pipeline["amount"].sum(),
            "weighted_pipeline_value": pipeline["weighted_amount"].sum(),
            "open_deals": len(pipeline),
            "at_risk_segments": at_risk_segments,
            "forecast_by_segment": forecast_by_segment.to_dict("index"),
        }

    def recommend_actions(self, analysis: Dict[str, Any]) -> List[Action]:
        """Generate recommended actions based on revenue forecast."""
        actions = []
        
        shortfall = analysis.get("shortfall", 0)
        shortfall_pct = analysis.get("shortfall_pct", 0)
        at_risk_segments = analysis.get("at_risk_segments", [])
        
        # Action 1: If significant shortfall, recommend budget reallocation
        if shortfall > 0 and shortfall_pct > 10:
            context = f"Revenue forecast shows ${shortfall:,.0f} shortfall ({shortfall_pct:.1f}% below target). " \
                     f"Win rate: {analysis.get('win_rate', 0):.1%}, Avg velocity: {analysis.get('avg_deal_velocity_days', 0):.0f} days."
            
            actions.append(Action(
                type="budget_reallocation",
                title=f"Reallocate Budget to Close ${shortfall:,.0f} Gap",
                description=f"Forecasted revenue is ${analysis.get('forecasted_revenue', 0):,.0f} vs. target of ${analysis.get('target_revenue', 0):,.0f}. "
                           f"Recommend increasing marketing spend or sales resources to accelerate pipeline.",
                priority="high",
                impact_score=int(shortfall / 1000),  # Impact in thousands
                metadata={
                    "shortfall": shortfall,
                    "shortfall_pct": shortfall_pct,
                    "target_revenue": analysis.get("target_revenue", 0),
                    "forecasted_revenue": analysis.get("forecasted_revenue", 0),
                },
                reasoning=self.generate_rationale(context),
            ))
        
        # Action 2: Targeted outreach for at-risk segments
        for segment_data in at_risk_segments[:3]:  # Top 3 at-risk segments
            segment = segment_data["segment"]
            gap = segment_data["gap"]
            
            context = f"{segment} segment is ${gap:,.0f} below target. " \
                     f"Current forecast: ${segment_data['forecast']:,.0f}, Target: ${segment_data['target']:,.0f}."
            
            actions.append(Action(
                type="targeted_outreach",
                title=f"Launch {segment} Outreach Campaign",
                description=f"{segment} segment is tracking ${gap:,.0f} below target. "
                           f"Recommend targeted campaign to accelerate deals in this segment.",
                priority="high" if gap > 100000 else "medium",
                impact_score=int(gap / 1000),
                metadata={
                    "segment": segment,
                    "gap": gap,
                    "target": segment_data["target"],
                    "forecast": segment_data["forecast"],
                },
                reasoning=self.generate_rationale(context),
            ))
        
        # Action 3: If velocity is slow, recommend process improvement
        avg_velocity = analysis.get("avg_deal_velocity_days", 60)
        if avg_velocity > 90:
            context = f"Average deal velocity is {avg_velocity:.0f} days, which is above industry benchmark. " \
                     f"Slow velocity impacts revenue realization."
            
            actions.append(Action(
                type="process_improvement",
                title="Accelerate Deal Velocity",
                description=f"Current average deal cycle is {avg_velocity:.0f} days. "
                           f"Recommend sales process review to identify bottlenecks and reduce time-to-close.",
                priority="medium",
                impact_score=int(analysis.get("total_pipeline_value", 0) * 0.1 / 1000),  # 10% of pipeline
                metadata={
                    "avg_velocity_days": avg_velocity,
                    "target_velocity_days": 60,
                },
                reasoning=self.generate_rationale(context),
            ))
        
        # Action 4: If win rate is low, recommend enablement
        win_rate = analysis.get("win_rate", 0.5)
        if win_rate < 0.4:
            context = f"Historical win rate is {win_rate:.1%}, below industry average. " \
                     f"Improving win rate by 10% could add ${analysis.get('weighted_pipeline_value', 0) * 0.1:,.0f} in revenue."
            
            actions.append(Action(
                type="sales_enablement",
                title="Launch Sales Enablement Program",
                description=f"Current win rate is {win_rate:.1%}. "
                           f"Recommend sales training and enablement to improve conversion rates.",
                priority="medium",
                impact_score=int(analysis.get("weighted_pipeline_value", 0) * 0.1 / 1000),
                metadata={
                    "current_win_rate": win_rate,
                    "target_win_rate": 0.5,
                    "potential_impact": analysis.get("weighted_pipeline_value", 0) * 0.1,
                },
                reasoning=self.generate_rationale(context),
            ))
        
        logger.info(f"Generated {len(actions)} revenue forecasting actions")
        return actions
