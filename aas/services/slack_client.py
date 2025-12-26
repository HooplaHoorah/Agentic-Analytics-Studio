"""Real client for Slack integrations using slack_sdk."""

from __future__ import annotations

from typing import Any, Dict
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SlackClient:
    """Client for Slack interactions."""

    def __init__(self, bot_token: str = "") -> None:
        self.bot_token = bot_token
        self.client = WebClient(token=self.bot_token) if self.bot_token else None

    def send_message(self, channel: str, text: str, blocks: Any | None = None) -> Dict[str, Any]:
        """Send a message to a Slack channel.

        Args:
            channel: The Slack channel ID or name.
            text: The plain text body of the message.
            blocks: Optional Block Kit payload.

        Returns:
            A dictionary representing the API response.
        """
        if not self.client:
            return {"status": "demo_success", "note": "Slack not configured."}

        try:
            response = self.client.chat_postMessage(
                channel=channel,
                text=text,
                blocks=blocks
            )
            return response.data
        except SlackApiError as e:
            logger.error(f"Error sending message to Slack: {e}")
            raise e