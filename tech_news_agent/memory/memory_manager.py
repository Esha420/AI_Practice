# memory/memory_manager.py
from memory.short_term_memory import ShortTermMemory
from memory.fact_memory_db import FactMemoryDB


class MemoryManager:
    def __init__(self):
        self.short_term = ShortTermMemory(window=5)
        self.fact_db = FactMemoryDB()

    def get_memory_block(self, agent):
        stm = self.short_term.get_context()
        
        # Load last 20 verified facts
        ltm_facts = self.fact_db.get_recent_facts(20)

        long_term_text = "\n".join(f"- {f}" for f in ltm_facts) if ltm_facts else "No stored facts."

        return (
            f"\n### MEMORY CONTEXT FOR {agent.role}\n"
            f"---\n"
            f"Short-term memory:\n{stm}\n\n"
            f"Long-term verified facts:\n{long_term_text}\n---\n"
        )
