# daily_report.py
import inngest
from slack import send_slack_message
from vector_db import QdrantStorage
import datetime

from inngest_client import inngest_client # reuse your existing Inngest client

@inngest_client.create_function(
    fn_id="Daily Report",
    trigger=inngest.TriggerEvent(event="schedule/daily")  # This is the scheduled event
)
async def daily_report(ctx: inngest.Context):
    """
    Sends a daily summary report to Slack.
    """
    # Example: Count total PDFs ingested today
    # You can customize the log storage & query
    store = QdrantStorage()
    
    # If you saved ingestion logs in a file/db, read and summarize them
    # For now, let's assume we track PDF counts in Qdrant metadata
    # Example placeholder
    pdf_count_today = 10  # TODO: Replace with actual log query

    message = (
        f"📊 *Daily RAG Report - {datetime.date.today()}*\n"
        f"- PDFs ingested today: {pdf_count_today}\n"
        f"- Queries processed: TODO\n"
        f"- Summaries generated: TODO"
    )

    send_slack_message(message, channel="#reports")
    return {"status": "success"}
