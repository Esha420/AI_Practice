#tasks/fact_check_task.py
from crewai import Task
from agents.fact_checker import fact_checker
from tools.search_tool import search_tool
from tools.scrape_tool import scraper
from tools.memory_tool import fact_save_tool

fact_check_task = Task(
    description=(
        "Fact-check the drafted article. Ensure accuracy by re-scanning "
        "sources and cross-verifying using web search."
        "Use the Fact_Saver tool to save a newly verified facts."
    ),
    expected_output="Verified article OR corrections list.",
    tools=[search_tool, scraper, fact_save_tool],
    agent=fact_checker,
    output_file="memory/facts.md"
)
