# src/tools/firecrawl.py
import os
import requests

FIRECRAWL_ENDPOINT = "https://api.firecrawl.dev/v1/search"  # example; adjust if required

def market_research_firecrawl(query: str, top_k: int = 5) -> str:
    """
    Query Firecrawl (if configured) for market research. Returns summarized text.
    If FIRECRAWL_API_KEY not set, returns a note.
    """
    key = os.getenv("FIRECRAWL_API_KEY")
    if not key:
        return "Firecrawl API key not configured. Skipping detailed market crawling."
    params = {"q": query, "size": top_k}
    headers = {"Authorization": f"Bearer {key}"}
    try:
        resp = requests.get(FIRECRAWL_ENDPOINT, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        # data format may vary; attempt to extract titles/snippets
        hits = data.get("results", []) or data.get("hits", []) or []
        lines = []
        for i, h in enumerate(hits[:top_k]):
            title = h.get("title") or h.get("headline") or h.get("name") or ""
            snippet = h.get("snippet") or h.get("text") or h.get("summary") or ""
            lines.append(f"{i+1}. {title}\n{snippet}\n")
        return "\n".join(lines) if lines else "No results from Firecrawl."
    except Exception as e:
        return f"Firecrawl error: {e}"
