"""Salesforce client for integrations.

This client uses simple_salesforce to verify and execute actions against a live Salesforce instance.
Supports two modes:
- stub: Safe default, returns previews of what would be executed
- live: Attempts real API calls with provided credentials
"""

from __future__ import annotations

import os
from typing import Any, Dict
try:
    from simple_salesforce import Salesforce
except ImportError:
    Salesforce = None

from ..utils.logger import get_logger

logger = get_logger(__name__)


class SalesforceClient:
    """Client for Salesforce interactions with stub/live mode support."""

    def __init__(self, username: str = "", password: str = "", security_token: str = "", domain: str = "login") -> None:
        """
        Initialize Salesforce client.
        
        Reads SALESFORCE_MODE from environment:
        - stub (default): No real API calls, returns previews
        - live: Attempts authentication and real API calls
        """
        self.username = username or os.getenv("SF_USERNAME")
        self.password = password or os.getenv("SF_PASSWORD")
        self.security_token = security_token or os.getenv("SF_SECURITY_TOKEN")
        self.domain = domain or os.getenv("SF_DOMAIN", "login")
        self.sf = None
        
        # Read mode from environment (stub or live)
        self.mode = os.getenv("SALESFORCE_MODE", "stub").lower()
        
        if self.mode == "live":
            # Only attempt authentication in live mode
            if self.username and self.password and self.security_token:
                if Salesforce:
                    try:
                        self.sf = Salesforce(
                            username=self.username,
                            password=self.password,
                            security_token=self.security_token,
                            domain=self.domain
                        )
                        logger.info("Salesforce client authenticated successfully (LIVE mode).")
                    except Exception as e:
                        logger.warning(f"Failed to authenticate with Salesforce: {e}. Falling back to stub mode.")
                        self.mode = "stub"  # Fallback to stub if auth fails
                else:
                    logger.warning("simple_salesforce not installed. Falling back to stub mode.")
                    self.mode = "stub"
            else:
                logger.warning("Salesforce credentials not provided. Falling back to stub mode.")
                self.mode = "stub"
        else:
            logger.info("Salesforce client running in STUB mode (no real API calls).")

    def get_mode(self) -> str:
        """Return the current mode (stub or live)."""
        return self.mode

    def create_task(self, subject: str, description: str, owner_id: str, what_id: str) -> Dict[str, Any]:
        """Create a task in Salesforce.

        Args:
            subject: Title of the task.
            description: Longer description.
            owner_id: User ID of the task owner.
            what_id: ID of the related object (e.g. Opportunity ID).

        Returns:
            A dictionary representing the created task (or stub result with preview).
        """
        task_fields = {
            "Subject": subject,
            "Description": description,
            "OwnerId": owner_id,
            "WhatId": what_id,
            "Status": "Not Started",
            "Priority": "Normal"
        }
        
        if self.mode == "live" and self.sf:
            try:
                res = self.sf.Task.create(task_fields)
                logger.info(f"Created Salesforce Task: {res.get('id')}")
                return {
                    "id": res.get("id"),
                    "success": True,
                    "mode": "live"
                }
            except Exception as e:
                logger.error(f"Failed to create Salesforce Task: {e}")
                raise e
        else:
            # Stub mode: return preview
            logger.info(f"[STUB] Would create Salesforce Task: {subject} for {what_id}")
            return {
                "id": "stub_task_id_123",
                "success": True,
                "mode": "stub",
                "preview": {
                    "object": "Task",
                    "operation": "create",
                    "fields": task_fields,
                    "description": f"Would create Task: '{subject}' assigned to {owner_id} for record {what_id}"
                }
            }

    def update_record(self, object_name: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Salesforce record.

        Args:
            object_name: The API name of the object (e.g. 'Opportunity').
            record_id: The ID of the record to update.
            fields: A dictionary of fields to update.

        Returns:
            A dictionary representing the updated record (or stub result with preview).
        """
        if self.mode == "live" and self.sf:
            try:
                # getattr(self.sf, object_name) fetches the resource, e.g. self.sf.Opportunity
                resource = getattr(self.sf, object_name)
                res = resource.update(record_id, fields)
                logger.info(f"Updated Salesforce {object_name} {record_id} with {fields}")
                return {
                    "id": record_id,
                    "success": True,
                    "mode": "live",
                    "result": res
                }
            except Exception as e:
                logger.error(f"Failed to update Salesforce record: {e}")
                raise e
        else:
            # Stub mode: return preview
            logger.info(f"[STUB] Would update {object_name} {record_id} with {fields}")
            return {
                "id": record_id,
                "success": True,
                "mode": "stub",
                "preview": {
                    "object": object_name,
                    "operation": "update",
                    "record_id": record_id,
                    "fields": fields,
                    "description": f"Would update {object_name} {record_id} with fields: {', '.join(fields.keys())}"
                }
            }