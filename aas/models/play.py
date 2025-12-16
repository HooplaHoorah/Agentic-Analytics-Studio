"""Data structures for representing the result of a play."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .action import Action


@dataclass
class PlayResult:
    """Container for the outcome of running a hero play.

    Attributes:
        analysis: A dictionary containing findings, charts, drivers, etc.
        actions: A list of `Action` objects recommending next steps.
    """

    analysis: Dict[str, Any] = field(default_factory=dict)
    actions: List[Action] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Serialise the result to a JSON‑serialisable dictionary."""
        return {
            "analysis": self.analysis,
            "actions": [action.to_dict() for action in self.actions],
        }