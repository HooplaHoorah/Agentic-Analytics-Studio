"""Placeholder client for Salesforce integrations.

This stub defines minimal methods for creating tasks or updating records.
In a real implementation you would initialise a `Salesforce` object from
the `simple_salesforce` library or use Salesforce’s REST API with your
credentials. Environment variables (e.g. username, password, token) or
Salesforce connected app settings should be stored securely and loaded
outside of source control.
"""

from __future__ import annotations

from typing import Any, Dict


class SalesforceClient:
    """Minimal stub of a Salesforce client."""

    def __init__(self, username: str = "", password: str = "", security_token: str = "", domain: str = "login") -> None:
        self.username = username
        self.password = password
        self.security_token = security_token
        self.domain = domain
        # In a real client, authenticate here

    def create_task(self, subject: str, description: str, owner_id: str, what_id: str) -> Dict[str, Any]:
        """Create a task in Salesforce.

        Args:
            subject: Title of the task.
            description: Longer description.
            owner_id: User ID of the task owner.
            what_id: ID of the related object (e.g. Opportunity ID).

        Returns:
            A dictionary representing the created task (stubbed).
        """
        # Placeholder implementation
        raise NotImplementedError

    def update_record(self, object_name: str, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Salesforce record with new values.

        Args:
            object_name: The API name of the object (e.g. 'Opportunity').
            record_id: The ID of the record to update.
            fields: A dictionary of fields to update.

        Returns:
            A dictionary representing the updated record (stubbed).
        """
        raise NotImplementedError