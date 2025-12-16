"""Model for representing an action recommended by an agent."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Action:
    """Represents an action to be taken as a result of a play.

    Attributes:
        type: A short identifier for the action type (e.g. "salesforce_task", "slack_message").
        description: Human‑readable description of what to do.
        metadata: Additional parameters needed to execute the action (e.g. record IDs).
    """

    type: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON‑serialisable representation of the action."""
        return {
            "type": self.type,
            "description": self.description,
            "metadata": self.metadata,
        }