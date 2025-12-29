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

    def generate_rationale(self, context: str) -> str:
        """Use LLM to generate rationale for an action."""
        import os
        import httpx
        
        provider = os.getenv("LLM_PROVIDER", "none").lower()
        api_key = os.getenv("OPENAI_API_KEY")
        
        # 1. OpenAI Provider
        if provider == "openai" and api_key:
            try:
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                    "messages": [
                        {"role": "system", "content": "You are an expert sales analyst. Briefly explain (1 sentence) why this action is critical based on the data provided."},
                        {"role": "user", "content": context}
                    ],
                    "max_tokens": 60,
                    "temperature": 0.7
                }
                # Use sync call with timeout
                resp = httpx.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers, timeout=5.0)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"].strip()
                else:
                    logger.warning(f"OpenAI Error {resp.status_code}: {resp.text}")
                    return "AI Rationale: Optimization opportunity detected (OpenAI unavailable)."
            except Exception as e:
                logger.error(f"OpenAI Call failed: {e}")
                return "AI Rationale: Optimization opportunity detected (OpenAI connection error)."

        # 2. Ollama Provider
        elif provider == "ollama":
            base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/api")
            model = os.getenv("OLLAMA_MODEL", "llama3")
            try:
                payload = {
                    "model": model,
                    "prompt": f"You are an expert sales analyst. Briefly explain (1 sentence) why this action is critical based on the data provided: {context}",
                    "stream": False
                }
                resp = httpx.post(f"{base_url}/generate", json=payload, timeout=10.0)
                if resp.status_code == 200:
                    return resp.json().get("response", "").strip()
                else:
                    logger.warning(f"Ollama Error {resp.status_code}: {resp.text}")
                    return "AI Rationale: Optimization opportunity detected (Ollama unavailable)."
            except Exception as e:
                logger.error(f"Ollama Call failed: {e}")
                return "AI Rationale: Optimization opportunity detected (Ollama connection error)."

        # 3. Fallback / None
        else:
            # Deterministic fallback based on context keywords
            if "stage" in context.lower():
                 return "AI Rationale: Deal stalling at current stage warrants immediate intervention."
            elif "churn" in context.lower():
                 return "AI Rationale: High churn risk detected based on usage patterns."
            elif "spend" in context.lower():
                 return "AI Rationale: Unusual spend velocity requires budget review."
            return "AI Rationale: High impact opportunity identified based on current metrics."