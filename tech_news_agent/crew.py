# crew.py
from crewai import Crew, Process
from tasks.research_task import research_task
from tasks.writing_task import write_task
from tasks.fact_check_task import fact_check_task
from agents.researcher import news_researcher
from agents.writer import news_writer
from agents.fact_checker import fact_checker
from memory.memory_manager import MemoryManager

memory_manager = MemoryManager()

crew = Crew(
    agents=[news_researcher, news_writer, fact_checker],
    tasks=[research_task, write_task, fact_check_task],
    process=Process.sequential,
    verbose=True
)

def smart_kickoff(crew, inputs):
    """
    Prepend memory context to the user inputs before running tasks.
    """

    # Read LTM + STM
    memory_context = ""

    for agent in crew.agents:
        memory_context += memory_manager.get_memory_block(agent)

    # Prepend memory to the topic input
    updated_inputs = {
        key: f"{memory_context}\n\nUser Request: {value}"
        for key, value in inputs.items()
    }

    # Update STM with current inputs
    memory_manager.short_term.add(str(inputs))

    return crew.kickoff(inputs=updated_inputs)


result = smart_kickoff(crew, {"topic": "Use of AI Everyday"})
print(result)
