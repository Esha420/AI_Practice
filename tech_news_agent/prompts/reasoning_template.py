REASONING_TEMPLATE = """
You MUST produce output formatted EXACTLY as JSON with these keys:

{
  "reasoning_log": [
    {"step": 1, "type": "reasoning", "content": "1–2 sentence explanation"},
    {"step": 2, "type": "action", "tool_used": "search_tool", "tool_args": "query...", "content": "Describe the action"},
    {"step": 3, "type": "observation", "content": "Summarize tool output in ≤2 sentences"},
    ...
  ],
  "final_answer": "Concise answer (≤3 sentences).",
  "artifacts": {
    "urls": [],
    "facts_saved": [],
    "notes": []
  }
}

Rules:
- ALWAYS include a reasoning_log array.
- Every step determines either: reasoning | action | observation.
- Observations summarize tool outputs — NO full dumps.
- final_answer is SHORT and SEPARATE.
- You MAY still call tools normally, but must annotate the intent in the reasoning_log.
"""
