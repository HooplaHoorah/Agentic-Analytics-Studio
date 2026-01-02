"""
Plays module for Agentic Analytics Studio

This module provides the play registry and utilities for managing hero plays.
"""

from .registry import (
    PlayRegistry,
    PlaySpec,
    register_play,
    get_play,
    get_agent,
    list_plays,
    get_registry,
)

__all__ = [
    "PlayRegistry",
    "PlaySpec",
    "register_play",
    "get_play",
    "get_agent",
    "list_plays",
    "get_registry",
]
