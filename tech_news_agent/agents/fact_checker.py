# agents/fact_checker.py
from crewai import Agent
from agents.llm import llm
from tools.search_tool import search_tool
from tools.scrape_tool import scraper
from tools.fact_lookup import fact_lookup_tool
from tools.memory_tool import fact_save_tool

fact_checker = Agent(
    role="Fact Verification Analyst",
    goal=(
        "Evaluate statements, summaries, and extracted article information for factual accuracy. "
        "Check memory first for previously verified facts. Cross-verify with external sources if needed. "
        "Use Fact_Saver tool to save newly verified facts. "
        "Return JSON: [{statement, pass_fail, evidence}]."
    ),
    backstory=(
        "A meticulous analyst specializing in detecting hallucinations, cross-referencing claims, "
        "and verifying new facts."
    ),
    llm=llm,
    memory=True,
    tools=[search_tool, scraper, fact_lookup_tool, fact_save_tool],
    max_iterations=1,
    verbose=False,
    allow_delegation=False
)
