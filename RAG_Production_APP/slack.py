# slack.py
import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL", "#general")

client = WebClient(token=SLACK_BOT_TOKEN)

def send_slack_message(text: str, channel: str = SLACK_CHANNEL):
    """Send a message to a Slack channel."""
    try:
        client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        print("Slack error:", e.response["error"])

