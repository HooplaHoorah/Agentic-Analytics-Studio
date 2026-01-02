"""
Play Registry for Agentic Analytics Studio

This module provides a centralized registry for hero plays, making it easy to:
- Register new plays with metadata
- List available plays
- Get play instances dynamically
- Support extensibility for third-party plays
"""

from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass, field
from ..agents.base import AgentPlay


@dataclass
class PlaySpec:
    """Specification for a registered play."""
    
    id: str
    label: str
    description: str
    agent_class: Type[AgentPlay]
    tags: List[str] = field(default_factory=list)
    inputs_schema: Dict[str, Any] = field(default_factory=dict)
    demo_seed: Optional[str] = None
    icon: str = "🎯"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "id": self.id,
            "label": self.label,
            "description": self.description,
            "tags": self.tags,
            "inputs_schema": self.inputs_schema,
            "demo_seed": self.demo_seed,
            "icon": self.icon,
        }


class PlayRegistry:
    """Central registry for all hero plays."""
    
    def __init__(self):
        self._plays: Dict[str, PlaySpec] = {}
    
    def register(self, spec: PlaySpec) -> None:
        """Register a new play."""
        if spec.id in self._plays:
            raise ValueError(f"Play '{spec.id}' is already registered")
        self._plays[spec.id] = spec
    
    def get_play(self, play_id: str) -> Optional[PlaySpec]:
        """Get a play specification by ID."""
        return self._plays.get(play_id)
    
    def get_agent(self, play_id: str) -> Optional[AgentPlay]:
        """Get an instantiated agent for a play."""
        spec = self.get_play(play_id)
        if spec is None:
            return None
        return spec.agent_class()
    
    def list_plays(self) -> List[Dict[str, Any]]:
        """List all registered plays."""
        return [spec.to_dict() for spec in self._plays.values()]
    
    def get_play_ids(self) -> List[str]:
        """Get list of all play IDs."""
        return list(self._plays.keys())
    
    def unregister(self, play_id: str) -> bool:
        """Unregister a play (useful for testing)."""
        if play_id in self._plays:
            del self._plays[play_id]
            return True
        return False


# Global registry instance
_registry = PlayRegistry()


def register_play(
    id: str,
    label: str,
    description: str,
    agent_class: Type[AgentPlay],
    tags: Optional[List[str]] = None,
    inputs_schema: Optional[Dict[str, Any]] = None,
    demo_seed: Optional[str] = None,
    icon: str = "🎯"
) -> None:
    """
    Register a play in the global registry.
    
    Args:
        id: Unique identifier for the play (e.g., "pipeline", "churn")
        label: Human-readable label (e.g., "Pipeline Leakage")
        description: Brief description of what the play does
        agent_class: The AgentPlay subclass that implements this play
        tags: Optional list of tags for categorization
        inputs_schema: Optional schema for play inputs (for validation)
        demo_seed: Optional demo scenario identifier
        icon: Optional emoji icon for UI display
    
    Example:
        register_play(
            id="pipeline",
            label="Pipeline Leakage",
            description="Identify at-risk deals in your sales pipeline",
            agent_class=PipelineLeakageAgent,
            tags=["sales", "revenue"],
            icon="💰"
        )
    """
    spec = PlaySpec(
        id=id,
        label=label,
        description=description,
        agent_class=agent_class,
        tags=tags or [],
        inputs_schema=inputs_schema or {},
        demo_seed=demo_seed,
        icon=icon
    )
    _registry.register(spec)


def get_play(play_id: str) -> Optional[PlaySpec]:
    """Get a play specification by ID."""
    return _registry.get_play(play_id)


def get_agent(play_id: str) -> Optional[AgentPlay]:
    """Get an instantiated agent for a play."""
    return _registry.get_agent(play_id)


def list_plays() -> List[Dict[str, Any]]:
    """List all registered plays."""
    return _registry.list_plays()


def get_registry() -> PlayRegistry:
    """Get the global registry instance (for advanced usage)."""
    return _registry
