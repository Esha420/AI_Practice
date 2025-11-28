#tasks/research_task.py
from crewai import Task
from agents.researcher import news_researcher
from tools.search_tool import search_tool
from tools.memory_tool import url_save_tool


research_task = Task(
    description=(
        "Research the latest developments in {topic}. "
        "Use the URL_Saver tool to save the novel URLs."
    ),
    expected_output="artifacts",
    tools=[search_tool, url_save_tool],
    agent=news_researcher
)
