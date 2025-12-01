#tools/memory_tool.py
from crewai.tools import BaseTool
from memory.json_memory import JSONMemory # Import your custom memory
from memory.fact_memory_db import FactMemoryDB

# Instantiate your persistent memories for the tools to use
url_memory = JSONMemory("memory/urls.json")
summary_memory = JSONMemory("memory/summaries.json")
fact_db = FactMemoryDB(db_path="memory/facts.db", max_facts=200)


class URLSaveTool(BaseTool):
    name: str = "URL_Saver"
    description: str = "A tool to permanently save a newly found URL (as key) and its title/summary (as value) to the URL memory file."

    def _run(self, url: str, summary: str) -> str:
        """Save a key-value pair to the URLs JSON memory."""
        url_memory.set(url, summary)
        return f"Successfully saved URL: {url} to memory."

class FactSaveTool(BaseTool):
    name: str = "Fact_Saver"
    description: str = "Save a verified fact and its evidence into the SQLite memory database."

    def _run(self, fact: str, evidence: str = "") -> str:
        fact_db.save_fact(fact, evidence)
        return f"Fact saved to DB: {fact}"
    
    
class SummarySaveTool(BaseTool):
    name: str = "Summary_Saver"
    description: str = "A tool to permanently save an article summary (as key) and its key insights (as value) to the Summary memory file."

    def _run(self, summary_title: str, insights: str) -> str:
        """Save a key-value pair to the Summaries JSON memory."""
        summary_memory.set(summary_title, insights)
        return f"Successfully saved summary: {summary_title} to memory."


# Instantiate the tools for use in agents/tasks
url_save_tool = URLSaveTool()
fact_save_tool = FactSaveTool()
summary_save_tool = SummarySaveTool()