# Data models for AAS

"""
The `models` package defines simple data structures used by agents to
represent analysis results and actions. Using dataclasses makes it easy
to convert between Python objects and JSON/dict representations.
"""

from .play import PlayResult  # noqa: F401
from .action import Action  # noqa: F401

__all__ = ["PlayResult", "Action"]