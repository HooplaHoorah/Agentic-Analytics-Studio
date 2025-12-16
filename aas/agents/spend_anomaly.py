"""Spend Anomaly hero play implementation (stub).

This module defines `SpendAnomalyAgent`, which currently returns a
placeholder message. Extend this class to ingest spending data, detect
anomalies and propose follow‑up actions.
"""

from __future__ import annotations

from typing import Any, Dict, List

from .base import AgentPlay
from ..models.action import Action


class SpendAnomalyAgent(AgentPlay):
    """Stub implementation of the Spend Anomaly play."""

    def analyze(self, data: Any) -> Dict[str, Any]:
        return {
            "message": "Spend Anomaly play not implemented yet."
        }

    def recommend_actions(self, analysis: Dict[str, Any]) -> List[Action]:
        return []