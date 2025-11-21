# tools/scrape_tool.py
from crewai.tools import BaseTool
import requests
from bs4 import BeautifulSoup

class ScrapeTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="scrape_webpage",
            description="Extracts readable article text from any webpage URL.",
            func=self._run
        )

    def _run(self, url: str) -> str:
        """Required method for synchronous execution in CrewAI."""
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
            text = "\n".join(paragraphs)
            return text if text else "No readable content found on the page."
        except Exception as e:
            return f"Scraping error: {str(e)}"

# instantiate for agents
scraper = ScrapeTool()
