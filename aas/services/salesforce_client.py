"""Salesforce client for integrations.

This client uses simple_salesforce to verify and execute actions against a live Salesforce instance.
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
    """Client for Salesforce interactions."""

    def __init__(self, username: str = "", password: str = "", security_token: str = "", domain: str = "login") -> None:
        self.username = username or os.getenv("SF_USERNAME")
        self.password = password or os.getenv("SF_PASSWORD")
        self.security_token = security_token or os.getenv("SF_SECURITY_TOKEN")
        self.domain = domain or os.getenv("SF_DOMAIN", "login")
        self.sf = None

        if self.username and self.password and self.security_token:
            if Salesforce:
                try:
                    self.sf = Salesforce(
                        username=self.username,
                        password=self.password,
                        security_token=self.security_token,
                        domain=self.domain
                    )
                    logger.info("Salesforce client authenticated successfully.")
                except Exception as e:
                    logger.error(f"Failed to authenticate with Salesforce: {e}")
            else:
                logger.warning("simple_salesforce not installed. Salesforce integration disabled.")
        else:
            logger.info("Salesforce credentials not provided. Client running in stub mode (logging only).")

    def create_task(self, subject: str, description: str, owner_id: str, what_id: str) -> Dict[str, Any]:
        """Create a task in Salesforce.

        Args:
            subject: Title of the task.
            description: Longer description.
            owner_id: User ID of the task owner.
            what_id: ID of the related object (e.g. Opportunity ID).

        Returns:
            A dictionary representing the created task (or stub result).
        """
        if self.sf:
            try:
                res = self.sf.Task.create({
                    "Subject": subject,
                    "Description": description,
                    "OwnerId": owner_id,
                    "WhatId": what_id,
                    "Status": "Not Started",
                    "Priority": "Normal"
                })
                logger.info(f"Created Salesforce Task: {res.get('id')}")
                return {"id": res.get("id"), "success": True}
            except Exception as e:
                logger.error(f"Failed to create Salesforce Task: {e}")
                raise e
        else:
            logger.warning(f"[STUB] creating Salesforce task: {subject} for {what_id}")
            return {"id": "stub_task_id_123", "success": True, "stub": True}

    def update_record(self, object_name: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Salesforce record.

        Args:
            object_name: The API name of the object (e.g. 'Opportunity').
            record_id: The ID of the record to update.
            fields: A dictionary of fields to update.

        Returns:
            A dictionary representing the updated record (or stub result).
        """
        if self.sf:
            try:
                # getattr(self.sf, object_name) fetches the resource, e.g. self.sf.Opportunity
                resource = getattr(self.sf, object_name)
                res = resource.update(record_id, fields)
                logger.info(f"Updated Salesforce {object_name} {record_id} with {fields}")
                return {"id": record_id, "success": True, "result": res}
            except Exception as e:
                logger.error(f"Failed to update Salesforce record: {e}")
                raise e
        else:
            logger.warning(f"[STUB] Updating {object_name} {record_id} with {fields}")
            return {"id": record_id, "success": True, "stub": True}