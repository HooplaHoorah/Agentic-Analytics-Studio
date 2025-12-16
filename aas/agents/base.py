"""Base classes and utilities for AAS agents."""

from __future__ import annotations

import abc
from typing import Any, Dict, Iterable, List, Optional

from ..models.action import Action
from ..models.play import PlayResult
from ..utils.logger import get_logger


logger = get_logger(__name__)


class AgentPlay(abc.ABC):
    """Abstract base class for all hero play agents.

    Subclasses should override `load_data`, `analyze` and `recommend_actions` to
    implement the specifics of their play. The `run()` method orchestrates
    these steps and returns a `PlayResult`. You can override `run()` if your
    play requires a different flow.
    """

    def load_data(self) -> Any:
        """Load or fetch the data needed for this play.

        This base implementation returns `None`. Plays without data can
        override this to return something meaningful.
        """

        return None

    def analyze(self, data: Any) -> Dict[str, Any]:
        """Perform analysis on the loaded data and return findings.

        Subclasses should override this method. The returned dictionary will
        be stored in `PlayResult.analysis`.
        """

        raise NotImplementedError("analyze() must be implemented in subclasses")

    def recommend_actions(self, analysis: Dict[str, Any]) -> List[Action]:
        """Generate recommended actions based on analysis.

        Subclasses should override this method to produce a list of
        `Action` objects. The default implementation returns an empty list.
        """

        return []

    def run(self) -> Dict[str, Any]:
        """Execute the play: load data, analyze it and propose actions.

        Returns a dictionary that can be serialised as JSON. The dictionary
        contains two keys: `analysis` (the findings) and `actions` (a list
        of actions encoded as dictionaries). This wrapper avoids making
        consumers import our dataclasses.
        """

        logger.info(f"Running play: {self.__class__.__name__}")
        data = self.load_data()
        logger.debug("Data loaded: %s", type(data))
        analysis = self.analyze(data)
        logger.debug("Analysis complete: %s", analysis.keys() if isinstance(analysis, dict) else analysis)
        actions = self.recommend_actions(analysis)
        logger.debug("Generated %d actions", len(actions))

        # Convert actions to plain dicts for JSON serialisation
        actions_serialisable = [action.to_dict() for action in actions]
        return {
            "analysis": analysis,
            "actions": actions_serialisable,
        }