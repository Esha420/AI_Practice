# daily_report.py
import json
from datetime import datetime, timezone
from pathlib import Path
import inngest
from .slack import send_slack_message

from .inngest_client import inngest_client
from .logger import LOG_FILE as EVENTS_FILE


def count_events_today(event_name: str) -> int:
    if not EVENTS_FILE.exists():
        return 0

    today = datetime.now(timezone.utc).date()
    count = 0

    with EVENTS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)

                # FIX: Correct field name ("event")
                if data.get("event") != event_name:
                    continue

                ts = data.get("ts")
                if not ts:
                    continue

                event_time = datetime.fromisoformat(ts).date()
                if event_time == today:
                    count += 1

            except Exception:
                continue
    return count


@inngest_client.create_function(
    fn_id="Daily Report",
    trigger=inngest.TriggerEvent(event="schedule/daily"),
)
async def daily_report(ctx: inngest.Context):

    pdf_count_today = count_events_today("rag_ingest")
    queries_today = count_events_today("rag_query")
    summaries_today = count_events_today("rag_summary")

    message = (
        f"📊 *Daily RAG Report - {datetime.now(timezone.utc).date()}*\n"
        f"- PDFs ingested today: {pdf_count_today}\n"
        f"- Queries processed: {queries_today}\n"
        f"- Summaries generated: {summaries_today}"
    )

    send_slack_message(message, channel="#reports")
    return {"status": "success"}
