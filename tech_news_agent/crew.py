# crew.py
import os, time
from crewai import Crew, Process
from tasks.research_task import research_task
from tasks.writing_task import write_task
from tasks.fact_check_task import fact_check_task
from agents.researcher import news_researcher
from agents.writer import news_writer
from agents.fact_checker import fact_checker
from crewai.events import BaseEventListener, TaskCompletedEvent, CrewTestCompletedEvent
from evaluation.evaluate_agent import AgentEvaluator
from memory.memory_manager import MemoryManager

# Set storage dir for CrewAI built-in memory
os.environ["CREWAI_STORAGE_DIR"] = "memory/db"

memory_manager = MemoryManager()
# ---------------- MEMORY LOGGER ----------------
class MemoryLogger(BaseEventListener):
    def setup_listeners(self, crew):
        # CrewAI handles event registration automatically
        pass

    def on_task_completed(self, event: TaskCompletedEvent):
        print(f"\n[TASK COMPLETED] {event.task.description}")

        if hasattr(event.agent, "memory_handler") and event.agent.memory_handler:
            memory = event.agent.memory_handler.load_all()
            print(f"[MEMORY STATE - {event.agent.role}]: {memory}")
        if event.task.output_file and os.path.exists(event.task.output_file):
            print("\n[REASONING LOG CONTENT]")
            with open(event.task.output_file, "r") as f:
                print(f.read())


    def on_step_completed(self, event: CrewTestCompletedEvent):
        print(f"[STEP COMPLETED] {event.agent.role} finished a step")


# ---------------- CREW SETUP ----------------
crew = Crew(
    agents=[news_researcher, news_writer, fact_checker],
    tasks=[research_task, write_task, fact_check_task],
    process=Process.sequential,
    verbose=True,
    memory=True,
    memory_config={
        "retrieve": True,
        "save": True,
        "max_tokens": 2000
    },
    event_listeners=[MemoryLogger()]
)

evaluator = AgentEvaluator()


# ---------------- EVALUATION RUNNER ----------------
def evaluate_agent_run(agent, task, inputs, memory_manager: MemoryManager):
    """
    Executes one task with one agent — then logs performance metrics.
    Integrates Short-Term Memory.
    """
    # 1. GET STM CONTEXT
    stm_context = memory_manager.short_term.get_context()

    # Convert inputs dict → string for CrewAI context
    context_str = "\n".join([f"{k}: {v}" for k, v in inputs.items()])
    
    # 2. ADD STM TO AGENT CONTEXT
    # This adds the recent history (STM) to the context for the *next* agent to consider.
    full_context = f"{context_str}\n\n--- RECENT HISTORY (STM) ---\n{stm_context}"


    start = time.time()
    # Execute with the full context
    response = task.execute_sync(agent, context=full_context)
    duration = time.time() - start

    # Convert TaskOutput → safe string
    # ... (same logic as before)
    if hasattr(response, "output") and response.output:
        response_text = response.output
    elif hasattr(response, "raw"):
        response_text = str(response.raw)
    else:
        response_text = str(response)

    # 3. UPDATE STM BUFFER with the latest task completion (agent role + final output)
    stm_update = f"[{agent.role} COMPLETED]:\n{response_text[:300]}...\n" # Truncate for efficiency
    memory_manager.short_term.add(stm_update)
    
    print(f"\n[AGENT EVALUATION] {agent.role}")
    print(f"Prompt: {context_str}")
    print("\n=== RAW AGENT OUTPUT ===")
    print(response_text)
    print("=== END OUTPUT ===\n")
    print(f"Time taken: {duration:.2f}s")

    evaluator.evaluate(agent.role, context_str, response_text, success=None)

    return response_text


# ---------------- MAIN EXECUTION ----------------
if __name__ == "__main__":
    topic_input = {"topic": "Use of AI Everyday"}

    for agent, task in zip(crew.agents, crew.tasks):
        print(f"\n[STARTING TASK] {task.description}")
        # 🎯 PASS THE MEMORY MANAGER HERE
        evaluate_agent_run(agent, task, topic_input, memory_manager) 

    print("\n[Crew Execution Completed]")