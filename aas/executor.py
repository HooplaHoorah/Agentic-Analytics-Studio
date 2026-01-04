"""Executor for approved actions."""

import os
from datetime import datetime, timezone
from typing import Any, Dict, List

from .services.salesforce_client import SalesforceClient
from .services.slack_client import SlackClient
from .utils.logger import get_logger

logger = get_logger(__name__)

def execute_actions(actions: List[Dict[str, Any]], run_id: str | None = None) -> List[Dict[str, Any]]:
    """Route actions to appropriate service clients or log as demo execution.
    
    Args:
        actions: List of action dictionaries from the frontend/API.
        run_id: The ID of the analysis run that generated these actions.
        
    Returns:
        List of execution result dictionaries with status and details.
    """
    results = []
    
    # Config check (from env vars as per instructions)
    # Config check (from env vars as per instructions)
    sf_user = os.getenv("SF_USERNAME")
    slack_token = os.getenv("SLACK_BOT_TOKEN")
    
    # Instantiate clients (they handle their own fallback auth internally usually, but we check presence to decide mode)
    # We pass explicit None if not set so they can decide to fallback or error
    sf_client = SalesforceClient()
    slack_client = SlackClient(bot_token=slack_token) if slack_token else None
    
    for action in actions:
        action_type = action.get("type")
        action_id = action.get("id")
        metadata = action.get("metadata", {})
        
        result = {
            "action_id": action_id,
            "type": action_type,
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "details": {}
        }
        
        try:
            if action_type == "salesforce_task":
                if sf_client:
                    try:
                        # Attempt real call if implemented
                        payload = dict(
                            subject=metadata.get("subject", "AAS Follow-up"),
                            description=action.get("description", ""),
                            owner_id=metadata.get("owner", "default"),
                            what_id=metadata.get("opportunity_id", "")
                        )
                        
                        # --- DEMO STUB WRITER START ---
                        # Write what we WOULD have sent to SFDC
                        try:
                            import json
                            os.makedirs("/tmp", exist_ok=True)
                            with open("/tmp/sf_last_task.json", "w") as f:
                                json.dump(payload, f, indent=2)
                        except Exception as e:
                            logger.warning(f"Failed to write SF stub file: {e}")
                        # --- DEMO STUB WRITER END ---

                        res = sf_client.create_task(**payload)
                        result["details"] = res
                    except NotImplementedError:
                        result["status"] = "demo_success"
                        result["details"] = {"note": "Salesforce task logged in demo mode (client not implemented)."}
                else:
                    result["status"] = "demo_success"
                    result["details"] = {"note": "Salesforce not configured; running in demo mode."}
                    
            elif action_type == "slack_message":
                if slack_client:
                    # --- DEMO STUB WRITER START ---
                    try:
                        import json
                        os.makedirs("/tmp", exist_ok=True)
                        stub_data = {
                            "channel": metadata.get("channel", "#general"),
                            "text": metadata.get("text", action.get("description", "")),
                            "action_title": action.get("title"),
                            "timestamp": datetime.now().isoformat()
                        }
                        with open("/tmp/slack_last_message.json", "w") as f:
                            json.dump(stub_data, f, indent=2)
                    except Exception as e:
                        logger.warning(f"Failed to write Slack stub file: {e}")
                    # --- DEMO STUB WRITER END ---

                    res = slack_client.send_message(
                        channel=metadata.get("channel", "#general"),
                        text=metadata.get("text", action.get("description", ""))
                    )
                    result["details"] = res
                else:
                    result["status"] = "demo_success"
                    result["details"] = {"note": "Slack not configured; running in demo mode."}
            
            else:
                result["status"] = "ignored"
                result["details"] = {"note": f"Action type '{action_type}' has no executor."}
                
        except Exception as e:
            logger.error(f"Error executing action {action_id}: {e}")
            result["status"] = "error"
            result["details"] = {"error": str(e)}
            
        results.append(result)
        
    return results
