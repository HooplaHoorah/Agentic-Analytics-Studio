"""Pipeline Leakage hero play implementation (stub).

This module defines `PipelineLeakageAgent`, a concrete subclass of
`AgentPlay` that demonstrates how to load a dataset, perform simple
analysis and generate follow‑up actions. The logic here is intentionally
rudimentary; replace it with more sophisticated analytics as you build
out the MVP.
"""

from __future__ import annotations

import datetime as _dt
from importlib import resources
from typing import Any, Dict, List

import pandas as pd  # type: ignore

from .base import AgentPlay
from ..models.action import Action
from ..utils.logger import get_logger


logger = get_logger(__name__)


class PipelineLeakageAgent(AgentPlay):
    """Agent that identifies at‑risk deals and proposes follow‑ups."""

    def load_data(self) -> pd.DataFrame:
        """Load the sample pipeline dataset from the package."""
        try:
            with resources.open_text("aas.data", "demo_pipeline_data.csv") as f:
                df = pd.read_csv(f)
        except FileNotFoundError:
            logger.warning("demo_pipeline_data.csv not found; returning empty DataFrame")
            return pd.DataFrame()
        return df

    def analyze(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Identify at‑risk deals and basic pipeline statistics.

        Args:
            data: A DataFrame of opportunity records.

        Returns:
            A dict with keys:
            * `at_risk_deals`: list of deals flagged for attention.
            * `stage_distribution`: distribution of deals by stage.
            * `narrative`: human‑readable summary of findings.
        """
        if data.empty:
            return {
                "at_risk_deals": [],
                "stage_distribution": {},
                "narrative": "No data available."
            }

        # Convert date columns to datetime for sorting; ignore errors
        for col in ["close_date", "last_touch_date"]:
            if col in data.columns:
                data[col] = pd.to_datetime(data[col], errors="coerce")

        # Stage distribution
        if "stage" in data.columns:
            stage_counts = data["stage"].value_counts().to_dict()
        else:
            stage_counts = {}

        # Determine at‑risk deals: sort by stage age descending and then by upcoming close date
        sort_cols = []
        if "stage_age" in data.columns:
            sort_cols.append("stage_age")
        if "close_date" in data.columns:
            sort_cols.append("close_date")
        if sort_cols:
            at_risk_df = data.sort_values(sort_cols, ascending=[False] * len(sort_cols)).head(5)
        else:
            at_risk_df = data.head(5)

        # Make a copy to avoid SettingWithCopyWarning on the slice
        at_risk_df = at_risk_df.copy()
        for col in ("close_date", "last_touch_date"):
            if col in at_risk_df.columns:
                at_risk_df[col] = at_risk_df[col].astype(str)

        # Select a subset of fields to include in the result
        cols = [c for c in ["opportunity_id", "stage", "owner", "stage_age", "amount", "close_date"] if c in at_risk_df.columns]
        at_risk_list = at_risk_df[cols].to_dict(orient="records")

        narrative = (
            f"Identified {len(at_risk_list)} deals at risk based on stage age "
            f"and closing dates. Focus follow‑up on these opportunities to reduce leakage."
        )

        return {
            "at_risk_deals": at_risk_list,
            "stage_distribution": stage_counts,
            "narrative": narrative,
        }

    def recommend_actions(self, analysis: Dict[str, Any]) -> List[Action]:
        """Generate a Salesforce task for each at‑risk deal (placeholder).

        Args:
            analysis: The analysis dict returned by `analyze()`.

        Returns:
            A list of `Action` objects representing follow‑ups.
        """
        actions: List[Action] = []
        for deal in analysis.get("at_risk_deals", []):
            opp_id = deal.get("opportunity_id") or "unknown"
            owner = deal.get("owner") or "the owner"
            stage = deal.get("stage") or ""
            description = (
                f"Reach out to {owner} to unblock deal {opp_id} (stage: {stage}). "
                f"Discuss next steps and update the close date if needed."
            )
            actions.append(
                Action(
                    type="salesforce_task",
                    description=description,
                    metadata={"opportunity_id": opp_id},
                )
            )
        return actions