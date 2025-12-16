# Agents package

"""
The `agents` package contains definitions for each hero play in the Agentic
Analytics Studio. Each module defines a class that inherits from
`AgentPlay` (defined in `base.py`) and implements three key methods:

* `load_data()` – load the required data for the play (e.g. read from sample CSV).
* `analyze(data)` – perform analysis and return a structured representation of
  findings (drivers, insights, etc.).
* `recommend_actions(analysis)` – generate actionable recommendations based on
  the analysis (e.g. tasks, notifications).

The `run()` method provided by the base class orchestrates these steps and
returns a dictionary with analysis and actions. Concrete agents can override
the orchestrator if they need a custom flow.
"""

from .base import AgentPlay  # noqa: F401 re‑export