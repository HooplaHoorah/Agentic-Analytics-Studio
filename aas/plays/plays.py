"""
Play Registration - Register all hero plays with the global registry

This module should be imported early in the application lifecycle to ensure
all plays are registered before the API starts serving requests.
"""

from .registry import register_play
from ..agents.pipeline_leakage import PipelineLeakageAgent
from ..agents.churn_rescue import ChurnRescueAgent
from ..agents.spend_anomaly import SpendAnomalyAgent
from ..agents.revenue_forecasting import RevenueForecastingAgent


def register_all_plays():
    """Register all built-in hero plays."""
    
    # Pipeline Leakage
    register_play(
        id="pipeline",
        label="Pipeline Leakage",
        description="Identify at-risk deals in your sales pipeline and prevent revenue slippage",
        agent_class=PipelineLeakageAgent,
        tags=["sales", "revenue", "pipeline"],
        inputs_schema={
            "min_stage_age_days": {
                "type": "integer",
                "description": "Minimum days in stage to flag as stalled",
                "default": 14
            }
        },
        demo_seed="pipeline_demo_1",
        icon="💰"
    )
    
    # Churn Rescue
    register_play(
        id="churn",
        label="Churn Rescue",
        description="Detect churn-risk customers and queue retention outreach",
        agent_class=ChurnRescueAgent,
        tags=["customer-success", "retention", "churn"],
        inputs_schema={},
        demo_seed="churn_demo_1",
        icon="🛟"
    )
    
    # Spend Anomaly
    register_play(
        id="spend",
        label="Spend Anomaly",
        description="Detect unusual spending patterns and trigger budget reviews",
        agent_class=SpendAnomalyAgent,
        tags=["finance", "budget", "anomaly"],
        inputs_schema={},
        demo_seed="spend_demo_1",
        icon="📊"
    )
    
    # Revenue Forecasting
    register_play(
        id="revenue",
        label="Revenue Forecasting",
        description="Forecast revenue shortfalls and recommend proactive interventions",
        agent_class=RevenueForecastingAgent,
        tags=["revenue", "forecasting", "planning"],
        inputs_schema={
            "target_revenue": {
                "type": "number",
                "description": "Target revenue for the forecast period",
                "optional": True
            },
            "forecast_period_days": {
                "type": "integer",
                "description": "Number of days to forecast",
                "default": 90
            }
        },
        demo_seed="revenue_demo_1",
        icon="📈"
    )


# Auto-register on module import
register_all_plays()
