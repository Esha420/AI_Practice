# tools/news_tool.py
import requests
import os

API_KEY = os.getenv("NEWS_API_KEY")  # store your NewsAPI key in environment variable

def news_tool(query="technology"):
    """
    Fetch top news headlines for a category or search term.
    """
    url = f"https://newsapi.org/v2/top-headlines?q={query}&language=en&apiKey={API_KEY}"
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("status") != "ok" or not data.get("articles"):
            return f"No news found for '{query}'."
        headlines = [article["title"] for article in data["articles"][:5]]
        return "\n".join(headlines)
    except Exception as e:
        return f"Error fetching news: {e}"
