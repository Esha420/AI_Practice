# memory/json_memory.py
import json
import os

class JSONMemory:
    def __init__(self, file_path):
        self.file_path = file_path
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump({}, f)

    def save(self, key, value):
        data = self.load_all()
        data[key] = value
        self._save(data)

    def load_all(self):
        try:
            with open(self.file_path, "r") as f:
                return json.load(f)
        except:
            return {}

    # Backwards compatibility for your tools
    def set(self, key, value):
        self.save(key, value)

    def get(self, key):
        data = self.load_all()
        return data.get(key)

    def _save(self, data):
        with open(self.file_path, "w") as f:
            json.dump(data, f, indent=2)
