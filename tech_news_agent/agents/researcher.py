#agents/researcher.py
from crewai import Agent
from agents.llm import llm
from tools.search_tool import search_tool
from tools.scrape_tool import scraper
from tools.fact_lookup import fact_lookup_tool
from tools.memory_tool import url_save_tool


news_researcher = Agent(
    role="Senior Researcher",
    goal=("Find new and important updates about {topic} and check if they are novel."
          "Use the URL_Saver tool to save all relevent URLs and their brief summary before finishing the task."

    ),
    backstory=(
        "You are responsible for analyzing the latest news, "
        "detecting relevance, spotting novelty, and performing "
        "early verification checks."
    ),
    llm=llm,
    agent_memory=True,
    memory_retrieval=True,
    memory_path="memory/urls.json",
    tools=[search_tool, scraper, fact_lookup_tool, url_save_tool],
    max_iterations=1,
    verbose=False,
    allow_delegation=True
)
