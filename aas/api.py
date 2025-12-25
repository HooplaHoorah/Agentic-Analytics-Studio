from __future__ import annotations

import os
import json
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any, Dict
from urllib.parse import quote
import jwt

from .db import get_conn

from dotenv import load_dotenv

# Load .env from project root
_env_path = Path(__file__).parent.parent / ".env"
load_dotenv(_env_path)

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

    # Enrich actions with Tableau embed URLs if possible
    if "actions" in payload and isinstance(payload["actions"], list):
        try:
            from .services.tableau_client import TableauClient
            server_url = os.getenv("TABLEAU_SERVER_URL")
            if server_url:
                client = TableauClient(
                    server_url=server_url,
                    site_id=os.getenv("TABLEAU_SITE_ID", ""),
                    token_name=os.getenv("TABLEAU_TOKEN_NAME", ""),
                    token_secret=os.getenv("TABLEAU_TOKEN_SECRET", "")
                )
                views = client.get_views()
                if views:
                    # Default to first view if not specified, 
                    # or try to match view_name from visual_context
                    pref_view = views[0]
                    viz_ctx = payload.get("visual_context", {})
                    if viz_ctx.get("view_name"):
                        match = next((v for v in views if viz_ctx["view_name"].lower() in v["name"].lower()), None)
                        if match:
                            pref_view = match
                    
                    for action in payload["actions"]:
                        if "metadata" not in action:
                            action["metadata"] = {}
                        if "embed_url" not in action["metadata"]:
                            action["metadata"]["embed_url"] = pref_view["embed_url"]
        except Exception as e:
            # Silent fail for enrichment
            pass

    # Add run metadata to the top-level response
    if isinstance(payload, dict):
        payload = {
            "run_id": run_id,
            "play": play,
            "generated_at": generated_at,
            **payload,
        }

    # --- DB PERSISTENCE START ---
    try:
        conn = get_conn()
        if conn:
            run_ts = datetime.fromisoformat(generated_at)
            
            # 1. Insert Run
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO aas_pipeline_runs (run_id, run_ts, play, notes) VALUES (%s, %s, %s, %s)",
                    (run_id, run_ts, play, "api run"),
                )

                # 2. Insert Actions
                # We expect 'actions' in payload to be a list of dicts
                actions = payload.get("actions", [])
                if actions:
                    for a in actions:
                        action_id = str(uuid4())
                        # Enrich the in-memory action payload with ID so frontend has it immediately
                        # (The frontend usually relies on index, but having ID is better)
                        a["action_id"] = action_id
                        
                        cur.execute(
                            """
                            INSERT INTO aas_actions (
                              action_id, run_id, created_at, status,
                              action_type, title, description, priority,
                              owner, region, stage, opportunity_id, payload
                            ) VALUES (%s, %s, %s, 'pending', %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            """,
                            (
                                action_id, run_id, run_ts,
                                a.get("type"),
                                a.get("title"),
                                a.get("description", ""),
                                int(a.get("priority", 3)),
                                a.get("owner"),
                                a.get("metadata", {}).get("region") or a.get("region"),
                                a.get("metadata", {}).get("stage") or a.get("stage"),
                                a.get("opportunity_id"),
                                json.dumps(a, default=str),
                            ),
                        )
            conn.close()
    except Exception as e:
        print(f"Warning: Failed to persist run to DB: {e}")
    # --- DB PERSISTENCE END ---

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

    # 3) Log Executions (JSONL)
    for result in execution_results:
        _append_execution_log({
            "approval_id": approval_id,
            "run_id": req.run_id,
            "timestamp": ts,
            **result
        })

    # --- DB UPDATE START ---
    try:
        conn = get_conn()
        if conn:
            with conn.cursor() as cur:
                approval_ts = datetime.fromisoformat(ts)
                for action in req.actions:
                    # If the action has an ID (mapped from DB run), use it.
                    # If coming from a fresh stateless run, we might not have 'action_id' yet in the request.
                    # But if we want to update logical status, we need to match it.
                    # For this demo, we'll try to use action_id if present.
                    act_id = action.get("action_id")
                    if act_id:
                        cur.execute(
                            "UPDATE aas_actions SET status='approved' WHERE action_id = %s",
                            (act_id,)
                        )
                        
                        # Also log execution
                        execution_id = str(uuid4())
                        # Find matching result if possible (ordered list)
                        # Minimal implementation: just log one execution row per approved action
                        cur.execute(
                            """
                            INSERT INTO aas_executions (execution_id, action_id, executed_at, status, result)
                            VALUES (%s, %s, %s, %s, %s)
                            """,
                            (execution_id, act_id, approval_ts, "ok", json.dumps({"note": "demo execution"}))
                        )
                        
                        cur.execute(
                            "UPDATE aas_actions SET status='executed' WHERE action_id = %s",
                            (act_id,)
                        )
            conn.close()
    except Exception as e:
        print(f"Warning: Failed to update DB on approve: {e}")
    # --- DB UPDATE END ---

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
def _build_tableau_embed_url(server_url: str, site_id: str, content_url: str) -> str:
    # Build a Tableau Cloud/Server embed URL for a view.
    # Canonical: https://<server>/t/<site>/views/<workbook>/<view>?:showVizHome=no&:embed=yes
    base = (server_url or '').rstrip('/')
    safe_content = '/'.join(quote(part) for part in (content_url or '').lstrip('/').split('/'))
    if site_id:
        return f"{base}/t/{site_id}/views/{safe_content}?:showVizHome=no&:embed=yes"
    return f"{base}/views/{safe_content}?:showVizHome=no&:embed=yes"


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
        return {"status": "success", "views": views}
    except Exception as e:
        return {"status": "error", "message": str(e), "views": []}
@app.get("/context/actions")
def context_actions(region: str | None = None, owner: str | None = None, stage: str | None = None):
    """
    Return pending actions filtered by business context (for Tableau integration).
    """
    conn = get_conn()
    if not conn:
        return {"actions": [], "status": "no_db_configured"}

    try:
        where = ["status IN ('pending', 'new')"]
        args = []
        if region:
            where.append("region = %s")
            args.append(region)
        if owner:
            where.append("owner = %s")
            args.append(owner)
        if stage:
            where.append("stage = %s")
            args.append(stage)

        sql = (
            "SELECT action_id, action_type, title, description, priority, owner, region, stage, opportunity_id, payload "
            "FROM aas_actions WHERE " + " AND ".join(where) +
            " ORDER BY priority ASC, created_at DESC LIMIT 50"
        )

        with conn.cursor() as cur:
            cur.execute(sql, tuple(args))
            rows = cur.fetchall()
        
        out = []
        for r in rows:
            out.append({
                "action_id": r[0],  # Important: frontend needs this to approve back specific items
                "type": r[1],
                "title": r[2],
                "description": r[3],
                "priority": r[4],
                "owner": r[5],
                "region": r[6],
                "stage": r[7],
                "opportunity_id": r[8],
                "metadata": json.loads(r[9]) if r[9] else {},
                # Flatten metadata for easier frontend usage if needed, or keep distinct
                ** (json.loads(r[9]) if r[9] else {}) 
            })
        
        conn.close()
        return {"actions": out, "filters": {"region": region, "owner": owner, "stage": stage}}

    except Exception as e:
        return {"error": str(e)}


def _build_tableau_jwt(user: str) -> str:
    client_id = os.getenv("TABLEAU_CONNECTED_APP_CLIENT_ID")
    kid = os.getenv("TABLEAU_CONNECTED_APP_SECRET_ID")
    secret = os.getenv("TABLEAU_CONNECTED_APP_SECRET_VALUE")

    if not (client_id and kid and secret):
        raise RuntimeError("Missing Tableau Connected App env vars")

    token = jwt.encode(
        {
            "iss": client_id,
            "exp": datetime.now(timezone.utc) + datetime.timedelta(minutes=10),
            "jti": str(uuid4()),
            "aud": "tableau",
            "sub": user,
            "scp": ["tableau:views:embed"],
        },
        secret,
        algorithm="HS256",
        headers={"kid": kid, "iss": client_id},
    )
    return token


@app.get("/tableau/jwt")
def tableau_jwt():
    """Generate a valid JWT for Tableau Connected App embedding."""
    user = os.getenv("TABLEAU_CONNECTED_APP_USERNAME", "aas_demo")
    
    # 1. Get the configured Viz URL (Essential for Cloud Embed)
    # Prefer explicit CLOUD URL, fallback to PUBLIC if needed (though public doesn't need JWT)
    viz_url = os.getenv("TABLEAU_VIZ_URL_CLOUD")
    
    if not viz_url:
        return {"status": "error", "message": "TABLEAU_VIZ_URL_CLOUD not set in environment"}

    # 2. Sanity Check (Instruction 29)
    if "/views/" not in viz_url:
        print(f"Error: Invalid Tableau Viz URL configured: {viz_url}")
        # We return 500 or a clear error so frontend stops
        raise HTTPException(status_code=500, detail="Misconfigured TABLEAU_VIZ_URL_CLOUD. Must contain '/views/'.")

    try:
        token = _build_tableau_jwt(user)
        return {"token": token, "vizUrl": viz_url}
    except Exception as e:
        return {"status": "error", "message": str(e)}
