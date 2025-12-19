"""Model for representing an action recommended by an agent."""

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Action:
    """Represents an action to be taken as a result of a play.

    Attributes:
        type: A short identifier for the action type (e.g. "salesforce_task", "slack_message").
        description: Human‑readable description of what to do.
        metadata: Additional parameters needed to execute the action (e.g. record IDs).
        id: Unique identifier for the action.
        title: Short descriptive title.
        priority: Action priority ("low"|"medium"|"high").
    """

    type: str
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    priority: str = "medium"

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON‑serialisable representation of the action."""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "metadata": self.metadata,
        }