# External service clients package

"""
The `services` package contains thin wrappers for interacting with external
systems such as Tableau, Salesforce and Slack. In this skeleton they are
placeholders. When you integrate AAS with real APIs, implement the
authentication and request logic in these modules.
"""

__all__ = ["TableauClient", "SalesforceClient", "SlackClient"]

from .tableau_client import TableauClient  # noqa: F401
from .salesforce_client import SalesforceClient  # noqa: F401
from .slack_client import SlackClient  # noqa: F401