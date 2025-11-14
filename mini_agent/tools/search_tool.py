# tools/search_tool.py
import requests

def search_tool(query):
    """
    Simple DuckDuckGo search API integration.
    Returns top 3 results.
    """
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        results = []
        if "RelatedTopics" in data:
            for topic in data["RelatedTopics"][:3]:
                if "Text" in topic:
                    results.append(topic["Text"])
        if results:
            return "\n".join(results)
        return f"No search results found for '{query}'."
    except Exception as e:
        return f"Error fetching search results: {e}"
