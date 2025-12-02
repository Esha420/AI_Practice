# slack.py
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#general")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_slack_message(text: str):
    """Send a message to Slack."""
    try:
        client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text=text
        )
    except SlackApiError as e:
        print("Slack error:", e.response["error"])
