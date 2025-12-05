# logger.py

import json
from pathlib import Path
from datetime import datetime, timezone

LOG_FILE = Path("logs/events.jsonl")
LOG_FILE.parent.mkdir(exist_ok=True)


def now_utc() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)


def log_event(event_type: str, data: dict | None = None):
    """
    Log any event with timestamp.
    :param event_type: e.g., 'rag_ingest', 'qdrant_upsert', 'rag_query', 'unsafe_query'
    :param data: additional structured data
    """
    entry = {
        "ts": now_utc().isoformat(),
        "event": event_type,
        "data": data or {}
    }
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def read_events():
    """Return all logged events as a list of dicts."""
    if not LOG_FILE.exists():
        return []
    with LOG_FILE.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def summarize_events():
    """
    Summarize events counts by type.
    Returns dict: {event_type: count, ...}
    """
    events = read_events()
    summary = {}
    for e in events:
        etype = e.get("event", "unknown")
        summary[etype] = summary.get(etype, 0) + 1
    return summary
