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

    def get_views(self) -> list[Any]:
        """List available views using tableauserverclient.
        
        Returns a list of dictionaries with view metadata and computed embed URLs.
        """
        import tableauserverclient as TSC

        if not all([self.server_url, self.token_name, self.token_secret]):
            return []

        try:
            tableau_auth = TSC.PersonalAccessTokenAuth(
                self.token_name, 
                self.token_secret, 
                site_id=self.site_id
            )
            server = TSC.Server(self.server_url, use_server_version=True)
            
            views_list = []
            with server.auth.sign_in(tableau_auth):
                # Query all views on the site
                all_views, pagination_item = server.views.get()
                
                base = self.server_url.rstrip('/')
                for v in all_views:
                    # Construct the embed URL standard for Tableau Cloud/Server
                    if self.site_id:
                        embed_url = f"{base}/t/{self.site_id}/views/{v.content_url}?:showVizHome=no"
                    else:
                        embed_url = f"{base}/views/{v.content_url}?:showVizHome=no"
                    
                    views_list.append({
                        "id": v.id,
                        "name": v.name,
                        "workbook_id": v.workbook_id,
                        "content_url": v.content_url,
                        "embed_url": embed_url
                    })
            
            return views_list

        except Exception as e:
            # Re-importing logger just in case, but usually it's at the top
            from ..utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Tableau API error: {e}")
            return []

    def publish_workbook(self, workbook_path: str, project_id: str) -> Any:
        """Publish a workbook to Tableau Server/Online."""
        raise NotImplementedError

    def query_view(self, view_id: str) -> Any:
        """Query data from a published view."""
        raise NotImplementedError
