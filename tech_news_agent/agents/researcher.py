# agents/researcher.py
from crewai import Agent
from agents.llm import llm
from tools.search_tool import search_tool
from tools.scrape_tool import scraper
from tools.fact_lookup import fact_lookup_tool
from tools.memory_tool import url_save_tool
from prompts.reasoning_template import REASONING_TEMPLATE

news_researcher = Agent(
    role="Senior Researcher",
    goal=(
        REASONING_TEMPLATE +
        "Before searching the web, FIRST check stored memory for previously saved URLs. "
        "If relevant updates are missing, perform a new web search for {topic}. "
        "Save all novel URLs and their summaries using the URL_Saver tool."
    ),
    backstory=(
        "You are responsible for analyzing the latest news, detecting relevance, "
        "spotting novelty, and avoiding duplicates using memory retrieval."
    ),
    llm=llm,
    memory=True,               # Use CrewAI built-in memory
    tools=[search_tool, scraper, fact_lookup_tool, url_save_tool],
    max_iterations=1,
    verbose=False,
    allow_delegation=True
)
