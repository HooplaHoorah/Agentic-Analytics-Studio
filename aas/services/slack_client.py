"""Real client for Slack integrations using slack_sdk."""

from __future__ import annotations

from typing import Any, Dict


class SlackClient:
    """Client for Slack interactions."""

    def __init__(self, bot_token: str = "") -> None:
        self.bot_token = bot_token
        if self.bot_token:
            from slack_sdk import WebClient
            self.client = WebClient(token=self.bot_token)
        else:
            self.client = None

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
        except Exception as e:
            from ..utils.logger import get_logger
            logger = get_logger(__name__)
            logger.error(f"Slack API error: {e}")
            raise e