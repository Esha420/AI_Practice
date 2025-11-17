# src/tools/github_tool.py
import os
import requests

GITHUB_SEARCH_URL = "https://api.github.com/search/repositories"

def github_search_repos(query: str, top_k: int = 5) -> str:
    token = os.getenv("GITHUB_TOKEN")
    params = {"q": f"{query} in:name,description", "sort": "stars", "per_page": top_k}
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    try:
        r = requests.get(GITHUB_SEARCH_URL, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        items = data.get("items", [])[:top_k]
        lines = []
        for i, it in enumerate(items):
            full_name = it.get("full_name")
            stars = it.get("stargazers_count", 0)
            desc = it.get("description") or ""
            html_url = it.get("html_url")
            lines.append(f"{i+1}. {full_name} ({stars} ⭐)\n{desc}\n{html_url}\n")
        return "\n".join(lines) if lines else "No GitHub repos found."
    except Exception as e:
        return f"GitHub search error: {e}"
