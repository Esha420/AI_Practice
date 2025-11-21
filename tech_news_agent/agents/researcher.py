#agents/researcher.py
import os
from crewai import Agent, LLM
from dotenv import load_dotenv
from memory.json_memory import JSONMemory
from tools.search_tool import search_tool
from tools.scrape_tool import scraper
from tools.fact_lookup import fact_lookup_tool
from tools.memory_tool import url_save_tool

load_dotenv()

# LLM setup
llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.3,
    api_key=os.getenv("GOOGLE_API_KEY")
)

researcher_memory = JSONMemory("memory/urls.json")

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
    memory=researcher_memory,
    tools=[search_tool, scraper, fact_lookup_tool, url_save_tool],
    max_iterations=1,
    verbose=True,
    allow_delegation=True
)
