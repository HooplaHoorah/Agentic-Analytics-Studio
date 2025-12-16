from __future__ import annotations

import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any, Dict

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .agents.pipeline_leakage import PipelineLeakageAgent
from .agents.churn_rescue import ChurnRescueAgent
from .agents.spend_anomaly import SpendAnomalyAgent

# Optional: handle pandas.Timestamp cleanly if it ever leaks into responses
try:
    import pandas as pd  # type: ignore

    CUSTOM_ENCODERS = {pd.Timestamp: lambda v: v.isoformat()}
except Exception:
    CUSTOM_ENCODERS = {}

app = FastAPI(title="Agentic Analytics Studio API", version="0.1.0")

# Dev-friendly CORS (lock down later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

AGENTS = {
    "pipeline": PipelineLeakageAgent,
    "churn": ChurnRescueAgent,
    "spend": SpendAnomalyAgent,
}


class RunRequest(BaseModel):
    params: Dict[str, Any] = Field(default_factory=dict)


APPROVALS_DIR = Path.cwd() / "data"          # runtime output (and gitignored if you add /data to .gitignore)
APPROVALS_FILE = APPROVALS_DIR / "approvals.jsonl"


class ApproveRequest(BaseModel):
    actions: list[Dict[str, Any]] = Field(..., description="List of action dicts to approve")
    approver: str = Field(default="demo-user")
    run_id: str | None = None
    notes: str | None = None


def _append_approval_log(record: Dict[str, Any]) -> None:
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)
    with APPROVALS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/plays")
def plays():
    return {"plays": list(AGENTS.keys())}


@app.post("/run/{play}")
def run_play(play: str, req: RunRequest = RunRequest()):
    play = play.lower().strip()
    agent_cls = AGENTS.get(play)
    if not agent_cls:
        raise HTTPException(status_code=400, detail=f"Unknown play '{play}'. Try one of: {list(AGENTS.keys())}")

    agent = agent_cls()  # some agents don't accept constructor args yet

    # Attach params in a consistent way
    if hasattr(agent, "params") and isinstance(getattr(agent, "params"), dict):
        agent.params.update(req.params)
    else:
        agent.params = req.params
    result = agent.run()

    # Support both PlayResult (preferred) and raw dict (current)
    if hasattr(result, "to_dict"):
        payload = result.to_dict()
    elif isinstance(result, dict):
        payload = result
    else:
        payload = {"result": str(result)}

    return jsonable_encoder(payload, custom_encoder=CUSTOM_ENCODERS)


@app.post("/approve")
def approve(req: ApproveRequest):
    approval_id = str(uuid4())
    ts = datetime.now(timezone.utc).isoformat()

    # In MVP: record approvals (and later, actually execute via Slack/Salesforce clients)
    for action in req.actions:
        _append_approval_log(
            {
                "approval_id": approval_id,
                "timestamp": ts,
                "approver": req.approver,
                "run_id": req.run_id,
                "notes": req.notes,
                "action": action,
                "status": "approved",
            }
        )

    return {
        "approval_id": approval_id,
        "approved_count": len(req.actions),
        "message": "Approved actions recorded (execution is stubbed in this MVP).",
        "log_file": str(APPROVALS_FILE),
    }


@app.get("/approvals")
def approvals():
    if not APPROVALS_FILE.exists():
        return {"approvals": []}

    approvals = []
    with APPROVALS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                approvals.append(json.loads(line))

    return {"approvals": approvals[-50:]}  # last 50
