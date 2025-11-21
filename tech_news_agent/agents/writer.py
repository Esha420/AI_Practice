#agents/writer.py
from crewai import Agent
from agents.llm import llm
from tools.search_tool import search_tool
from tools.scrape_tool import scraper
from tools.fact_lookup import fact_lookup_tool
from memory.json_memory import JSONMemory
from tools.memory_tool import summary_save_tool

fact_checker = fact_lookup_tool

writer_memory = JSONMemory("memory/summaries.json")

news_writer = Agent(
    role="Writer",
    goal=(
        "Write a clean, factual summary of the research in EXACTLY this format:\n"
        "1. Headline\n2. Bullet insights\n3. Final paragraph"
        "Use the Summary_Saver tool to store the relevant summary"
    ),
    backstory="You convert raw research into clean articles.",
    llm=llm,
    max_iterations=1,
    memory=writer_memory,
    tools=[scraper, fact_checker, search_tool, summary_save_tool],
    verbose=True
)
