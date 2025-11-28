#tasks/writing_task.py
from crewai import Task
from agents.writer import news_writer
from tools.scrape_tool import scraper
from tools.fact_lookup import fact_lookup_tool
from tools.memory_tool import summary_save_tool

write_task = Task(
    description=(
        "Write a clear article summarizing the research findings "
        "for {topic}. Pull essential content from provided URLs."
        "Use the Summary_Saver tool to save final article headline/insights."
    ),
    expected_output="markdown article",
    tools=[scraper, fact_lookup_tool, summary_save_tool],
    agent=news_writer,
    output_file="memory/output_article.md"
)
