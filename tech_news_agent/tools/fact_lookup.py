# tools/fact_lookup.py
from crewai.tools import BaseTool
import json
import os

class FactLookupTool(BaseTool):
    """Tool to check if a claim exists in memory/facts.json"""

    def __init__(self):
        super().__init__(
            name="fact_lookup",  # pass literal instead of self.name
            description="Checks if a claim appears inside stored factual records.",
            func=self._run
        )

    def _run(self, claim: str) -> str:
        """Check if the claim exists in memory/facts.json."""
        path = "memory/facts.json"

        if not os.path.exists(path):
            return "Fact memory not initialized."

        with open(path, "r") as f:
            facts = json.load(f)

        for fact in facts:
            if claim.lower() in fact.lower():
                return f"FACT MATCH: {fact}"

        return "NO MATCH FOUND."

# instantiate for agents
fact_lookup_tool = FactLookupTool()
