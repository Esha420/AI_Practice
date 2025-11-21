#crew.py
from crewai import Crew, Process
from tasks.research_task import research_task
from tasks.writing_task import write_task
from tasks.fact_check_task import fact_check_task
from agents.researcher import news_researcher
from agents.writer import news_writer
from agents.fact_checker import fact_checker

crew = Crew(
    agents=[news_researcher, news_writer, fact_checker],
    tasks=[research_task, write_task, fact_check_task],
    process=Process.sequential,  # sequential but multi-turn via tasks
)

result = crew.kickoff(inputs={"topic": "Use of AI Everyday"})
print(result)
