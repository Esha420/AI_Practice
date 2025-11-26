# agents/writer.py
from crewai import Agent
from agents.llm import llm
from tools.search_tool import search_tool
from tools.scrape_tool import scraper
from tools.fact_lookup import fact_lookup_tool
from tools.memory_tool import summary_save_tool
from prompts.reasoning_template import REASONING_TEMPLATE

news_writer = Agent(
    role="Writer",
    goal=(
        REASONING_TEMPLATE +
        "Write a clean, factual summary of the research in EXACTLY this format:\n"
        "1. Headline\n2. Bullet insights\n3. Final paragraph\n"
        "Check CrewAI memory for previous summaries to avoid duplication. "
        "Use Summary_Saver tool to store the final summary."
    ),
    backstory="You convert raw research into concise, readable articles.",
    llm=llm,
    memory=True,
    tools=[scraper, fact_lookup_tool, search_tool, summary_save_tool],
    max_iterations=1,
    verbose=False,
    allow_delegation=True
)
