# memory/memory_manager.py
from memory.short_term_memory import ShortTermMemory

class MemoryManager:
    def __init__(self):
        self.short_term = ShortTermMemory(window=5)

    def get_memory_block(self, agent):
        # CrewAI exposes memory via memory_handler
        ltm = {}

        # If the agent has long-term memory attached
        if hasattr(agent, "memory_handler") and agent.memory_handler:
            try:
                ltm = agent.memory_handler.load_all()
            except:
                ltm = {}

        stm = self.short_term.get_context()

        return (
            f"\n### MEMORY CONTEXT FOR {agent.role}\n"
            f"---\n"
            f"Short-term memory (recent steps):\n{stm}\n\n"
            f"Long-term memory (stored knowledge):\n{ltm}\n---\n"
        )
