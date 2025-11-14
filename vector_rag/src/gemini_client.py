from langchain_core.runnables import Runnable
from typing import Any

class GeminiChat(Runnable):
    """A simple Gemini wrapper implementing Runnable interface."""

    def __init__(self, model_name: str, api_key: str):
        self.model_name = model_name
        self.api_key = api_key

    def _call(self, inputs: Any, run_manager=None) -> str:
        """
        inputs can be a dict {'query': ..., 'context': ...} or a raw string.
        """
        if isinstance(inputs, dict):
            query = inputs.get("query", "")
            context = inputs.get("context", "")
        else:
            query = str(inputs)
            context = ""

        # Here you can add actual Gemini API call using the api_key.
        # For now, returning dummy response for testing.
        return f"[Gemini response] Query: '{query}', Context length: {len(context)}"

    # Required by Runnable abstract class
    def invoke(self, inputs: Any, run_manager=None) -> str:
        return self._call(inputs, run_manager)
