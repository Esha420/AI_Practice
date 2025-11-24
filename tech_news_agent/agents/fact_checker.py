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
        "Evaluate statements, summaries, and extracted article information for factual "
        "accuracy. Cross-check against memory-stored facts and external reliable sources."
        "Use the Fact_Saver tool to store the relevant facts before compliting the task."
        "Evaluate each statement with a PASS or FAIL label.\n"
        "Return JSON: [{statement, pass_fail, evidence}]."
    ),
    verbose=False,
    agent_memory=True,
    memory_retrieval=True,
    memory_path="memory/facts.json",
    backstory=(
        "A meticulous analyst with a strong commitment to evidence-based validation. "
        "You specialize in detecting hallucinations, cross-referencing claims using "
        "past verified facts, and verifying new ones using external search tools "
        "and direct article scraping when needed."
    ),
    tools=[
        search_tool,   # External real-time validation
        scraper,       # Validate claims by pulling raw source text
        fact_lookup_tool,   # Check against stored factual memory
        fact_save_tool 
    ],
    llm=llm,
    max_iterations=1,
    allow_delegation=False
)
