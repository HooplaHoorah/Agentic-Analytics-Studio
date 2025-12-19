"""Main entry point for the Agentic Analytics Studio skeleton.

This script allows you to run a stubbed hero play from the command line. It
parses a `--play` argument to choose between the available plays and then
instantiates the corresponding agent. Each agent returns a structured result
containing analysis, recommendations and actions. For now the logic is
minimal – it simply loads the sample dataset (where applicable) and
produces placeholder outputs. Use this as a starting point to wire in your
actual analytics and integrations.
"""

from __future__ import annotations

import argparse
import json
from typing import Dict


def run_play(play: str) -> Dict:
    """Dispatch to the appropriate agent class based on the play name.

    Args:
        play: One of "pipeline", "churn" or "spend".

    Returns:
        A dict representing the result of the play.
    """
    play = play.lower()
    if play == "pipeline":
        from .agents.pipeline_leakage import PipelineLeakageAgent

        agent = PipelineLeakageAgent()
    elif play == "churn":
        from .agents.churn_rescue import ChurnRescueAgent

        agent = ChurnRescueAgent()
    elif play == "spend":
        from .agents.spend_anomaly import SpendAnomalyAgent

        agent = SpendAnomalyAgent()
    else:
        raise ValueError(f"Unknown play '{play}'. Expected one of: pipeline, churn, spend.")

    return agent.run()


def main() -> None:
    """Parse command‑line arguments and run the selected play."""
    parser = argparse.ArgumentParser(description="Run an AAS hero play")
    parser.add_argument(
        "--play",
        choices=["pipeline", "churn", "spend"],
        default="pipeline",
        help="Which hero play to run: pipeline (default), churn or spend",
    )
    args = parser.parse_args()

    result = run_play(args.play)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()