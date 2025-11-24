# memory/short_term_memory.py
import json
import os

class ShortTermMemory:
    def __init__(self, window=5):
        self.window = window
        self.buffer = []

    def add(self, text: str):
        self.buffer.append(text)
        self.buffer = self.buffer[-self.window:]

    def get_context(self) -> str:
        return "\n".join(self.buffer) if self.buffer else "No recent context."
