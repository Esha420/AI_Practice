# src/tools/hackernews.py
import requests

ALGOLIA_HN_SEARCH = "https://hn.algolia.com/api/v1/search"

def hackernews_search(query: str, top_k: int = 5) -> str:
    params = {"query": query, "tags": "story", "hitsPerPage": top_k}
    try:
        r = requests.get(ALGOLIA_HN_SEARCH, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        hits = data.get("hits", [])[:top_k]
        out_lines = []
        for i, h in enumerate(hits):
            title = h.get("title") or h.get("story_title") or ""
            url = h.get("url") or h.get("story_url") or ""
            points = h.get("points", 0)
            comments = h.get("num_comments", 0)
            out_lines.append(f"{i+1}. {title}\nURL: {url}\nPoints: {points}, Comments: {comments}\n")
        return "\n".join(out_lines) if out_lines else "No recent Hacker News discussions found."
    except Exception as e:
        return f"Hacker News error: {e}"
