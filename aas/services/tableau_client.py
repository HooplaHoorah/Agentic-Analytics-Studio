"""Real client for Tableau integrations using tableauserverclient."""

from __future__ import annotations

import tableauserverclient as TSC
from typing import Any, List, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TableauClient:
    """Client for Tableau Server/Cloud interactions."""

    def __init__(self, server_url: str = "", site_id: str = "", token_name: str = "", token_secret: str = "") -> None:
        self.server_url = server_url
        self.site_id = site_id
        self.token_name = token_name
        self.token_secret = token_secret
        self.auth = TSC.PersonalAccessTokenAuth(
            token_name=self.token_name,
            personal_access_token=self.token_secret,
            site_id=self.site_id
        ) if self.token_name and self.token_secret else None
        self.server = TSC.Server(self.server_url, use_server_version=True) if self.server_url else None

    def get_views(self) -> List[Any]:
        """List all views available on the site."""
        if not self.server or not self.auth:
            raise ValueError("TableauClient not initialized with proper credentials")

        with self.server.auth.sign_in(self.auth):
            all_views, pagination_item = self.server.views.get()
            return all_views

    def query_view_data(self, view_id: str) -> Any:
        """Query data from a published view (CSV format)."""
        if not self.server or not self.auth:
            raise ValueError("TableauClient not initialized with proper credentials")

        with self.server.auth.sign_in(self.auth):
            view_item = self.server.views.get_by_id(view_id)
            self.server.views.populate_csv(view_item)
            return view_item.csv

    def publish_workbook(self, workbook_path: str, project_id: str) -> Any:
        """Publish a workbook to Tableau Server/Online."""
        if not self.server or not self.auth:
            raise ValueError("TableauClient not initialized with proper credentials")

        with self.server.auth.sign_in(self.auth):
            new_workbook = TSC.WorkbookItem(project_id)
            new_workbook = self.server.workbooks.publish(new_workbook, workbook_path, TSC.PublishMode.Overwrite)
            return new_workbook