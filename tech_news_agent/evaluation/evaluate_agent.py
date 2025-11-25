# evaluation/evaluate_agent.py
import time
import json
from pathlib import Path

class AgentEvaluator:
    def __init__(self, log_file="memory/agent_eval_log.json"):
        self.log_file = Path(log_file)
        if not self.log_file.exists():
            self.log_file.write_text(json.dumps([]))  # initialize empty log list

    def evaluate(self, agent_name, prompt, response_text, success=None):
        """
        Logs agent performance in JSON.
        Ensures `response_text` is a plain string (already cleaned).
        """
        record = {
            "agent": agent_name,
            "prompt": prompt,
            "response": response_text,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "success": success
        }

        logs = json.loads(self.log_file.read_text())
        logs.append(record)
        self.log_file.write_text(json.dumps(logs, indent=2))

        print(f"[EVALUATION] Logged performance of {agent_name}")
