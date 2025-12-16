"""Placeholder client for Slack integrations.

To send messages to Slack channels or users, you would normally use the
`slack_sdk.WebClient` and provide a bot token. This stub provides a
minimal interface that your agents can call without pulling in the
actual Slack SDK until you're ready to implement it.
"""

from __future__ import annotations

from typing import Any, Dict


class SlackClient:
    """Minimal stub of a Slack client."""

    def __init__(self, bot_token: str = "") -> None:
        self.bot_token = bot_token
        # In a real implementation, you would initialise `WebClient` here

    def send_message(self, channel: str, text: str, blocks: Any | None = None) -> Dict[str, Any]:
        """Send a message to a Slack channel.

        Args:
            channel: The Slack channel ID or name.
            text: The plain text body of the message.
            blocks: Optional Block Kit payload.

        Returns:
            A dictionary representing the API response (stubbed).
        """
        raise NotImplementedError