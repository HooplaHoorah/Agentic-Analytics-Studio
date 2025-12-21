"""Placeholder client for Tableau integrations.

Use the `tableauserverclient` library (or the Tableau REST API directly)
to publish workbooks, query data or create extracts. Populate the
authentication parameters using environment variables or a configuration
file. This skeleton defines the interface you might use without any
implementation.
"""

from __future__ import annotations

from typing import Any


class TableauClient:
    """Minimal stub of a Tableau client."""

    def __init__(self, server_url: str = "", site_id: str = "", token_name: str = "", token_secret: str = "") -> None:
        self.server_url = server_url
        self.site_id = site_id
        self.token_name = token_name
        self.token_secret = token_secret

    def publish_workbook(self, workbook_path: str, project_id: str) -> Any:
        """Publish a workbook to Tableau Server/Online.

        This method is intentionally unimplemented. When integrating with
        Tableau, use the `tableauserverclient.Server` to sign in and
        publish. See Tableau's Python SDK documentation for details.
        """
        raise NotImplementedError

    def query_view(self, view_id: str) -> Any:
        """Query data from a published view.

        This placeholder returns nothing. Implement it to fetch data or
        images from a Tableau view.
        """
        raise NotImplementedError

    def get_views(self) -> list[Any]:
        """List available views."""
        return []
