# memory/json_memory.py
import json
import os

class JSONMemory:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = {}
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                try:
                    self.data = json.load(f)
                except json.JSONDecodeError:
                    self.data = {}

    def get(self, key):
        """Return stored value for key or None if not present."""
        return self.data.get(key)

    def set(self, key, value):
        """Store value and persist to disk."""
        self.data[key] = value
        self._save()

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=2)

    def all(self):
        """Return entire memory dictionary."""
        return self.data
