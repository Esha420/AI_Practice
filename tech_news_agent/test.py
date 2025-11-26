# test_two_prompt_run.py

from crew import evaluate_agent_run, crew

# Choose ONLY TWO agents + TWO tasks
agents_to_test = crew.agents[:2]   # researcher + writer
tasks_to_test = crew.tasks[:2]     # research_task + write_task

# Minimal input
topic_input = {"topic": "Future of AI assistants"}

if __name__ == "__main__":
    print("\n[RUNNING TWO-PROMPT TEST CASE]\n")

    for agent, task in zip(agents_to_test, tasks_to_test):
        print(f"\n[STARTING TASK] {task.description}")
        evaluate_agent_run(agent, task, topic_input)

    print("\n[TEST CASE COMPLETED]\n")
