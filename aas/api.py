from __future__ import annotations

import os
import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any, Dict

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .agents.pipeline_leakage import PipelineLeakageAgent
from .agents.churn_rescue import ChurnRescueAgent
from .agents.spend_anomaly import SpendAnomalyAgent
from .executor import execute_actions

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

    run_id = str(uuid4())
    generated_at = datetime.now(timezone.utc).isoformat()

    result = agent.run()

    # Support both PlayResult (preferred) and raw dict (current)
    if hasattr(result, "to_dict"):
        payload = result.to_dict()
    elif isinstance(result, dict):
        payload = result
    else:
        payload = {"result": str(result)}

    # Add run metadata to the top-level response (keeps $res.actions working)
    if isinstance(payload, dict):
        payload = {
            "run_id": run_id,
            "play": play,
            "generated_at": generated_at,
            **payload,
        }

    return jsonable_encoder(payload, custom_encoder=CUSTOM_ENCODERS)



EXECUTIONS_FILE = APPROVALS_DIR / "executions.jsonl"


def _append_execution_log(record: Dict[str, Any]) -> None:
    APPROVALS_DIR.mkdir(parents=True, exist_ok=True)
    with EXECUTIONS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, default=str) + "\n")


@app.post("/approve")
def approve(req: ApproveRequest):
    approval_id = str(uuid4())
    ts = datetime.now(timezone.utc).isoformat()

    # 1) Log Approvals
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

    # 2) Execute Actions
    execution_results = execute_actions(req.actions, run_id=req.run_id)

    # 3) Log Executions
    for result in execution_results:
        _append_execution_log({
            "approval_id": approval_id,
            "run_id": req.run_id,
            "timestamp": ts,
            **result
        })

    return {
        "approval_id": approval_id,
        "approved_count": len(req.actions),
        "executed_count": len(execution_results),
        "execution_results": execution_results,
        "log_file": str(APPROVALS_FILE),
        "executions_file": str(EXECUTIONS_FILE),
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


@app.get("/executions")
def executions():
    if not EXECUTIONS_FILE.exists():
        return {"executions": []}

    executions = []
    with EXECUTIONS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                executions.append(json.loads(line))

    return {"executions": executions[-50:]}  # last 50
@app.get("/tableau/views")
def get_tableau_views():
    """List available Tableau views if credentials are set in environment."""
    server_url = os.getenv("TABLEAU_SERVER_URL")
    site_id = os.getenv("TABLEAU_SITE_ID", "")
    token_name = os.getenv("TABLEAU_TOKEN_NAME")
    token_secret = os.getenv("TABLEAU_TOKEN_SECRET")

    if not all([server_url, token_name, token_secret]):
        return {
            "status": "not_configured",
            "message": "Tableau credentials not fully set in environment (TABLEAU_SERVER_URL, TABLEAU_TOKEN_NAME, TABLEAU_TOKEN_SECRET)",
            "views": []
        }

    try:
        from .services.tableau_client import TableauClient
        client = TableauClient(
            server_url=server_url,
            site_id=site_id,
            token_name=token_name,
            token_secret=token_secret
        )
        views = client.get_views()
        # Simplify view objects for response
        result = []
        for v in views:
            # Construct embed URL (standard Tableau format)
            # With site: https://<server>/t/<site_id>/views/<content_url>?:showVizHome=no
            # Without site: https://<server>/views/<content_url>?:showVizHome=no
            base_url = server_url.rstrip("/")
            if site_id:
                embed_url = f"{base_url}/t/{site_id}/views/{v.content_url}?:showVizHome=no"
            else:
                embed_url = f"{base_url}/views/{v.content_url}?:showVizHome=no"

            result.append({
                "id": v.id,
                "name": v.name,
                "workbook_id": v.workbook_id,
                "content_url": v.content_url,
                "embed_url": embed_url
            })
        return {"status": "success", "views": result}
    except Exception as e:
        return {"status": "error", "message": str(e), "views": []}
