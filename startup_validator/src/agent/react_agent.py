# src/agent/react_agent.py
import re
from typing import Callable, Dict, List
from llm.gemini import GeminiClient
from tools.firecrawl import market_research_firecrawl
from tools.hackernews import hackernews_search
from tools.github_tool import github_search_repos
from prompts import SYSTEM_PROMPT

ACTION_RE = re.compile(r"^\s*ACTION:\s*([a-zA-Z0-9_]+)\s*:\s*(.+)$", re.MULTILINE)
FINAL_RE = re.compile(r"^\s*FINAL:\s*(.+)$", re.MULTILINE | re.DOTALL)

class ReactAgent:
    def __init__(self, llm: GeminiClient, max_steps: int = 3):
        self.llm = llm
        self.max_steps = max_steps
        # tools registry: name -> function
        self.tools = {
            "market_research": market_research_firecrawl,
            "hackernews": hackernews_search,
            "github_search": github_search_repos,
        }

    def _call_llm(self, prompt_text: str) -> str:
        # wrapper to call Gemini / local HF model
        return self.llm.generate(prompt_text, max_output_tokens=512)

    def run(self, user_idea: str) -> str:
        """
        Run the ReAct loop: send user idea + history to LLM, parse ACTIONs, run tools, append observations,
        repeat until FINAL or steps exhausted.
        """
        history: List[str] = []
        system_block = SYSTEM_PROMPT.strip()
        prompt = f"User: {user_idea}\n\n{system_block}\n\nHistory:\n"

        for step in range(self.max_steps):
            hist_text = "\n".join(history[-6:])  # keep last few pieces
            full_prompt = f"{prompt}{hist_text}\n\nAgent, produce the next ACTION or FINAL.\n"
            raw = self._call_llm(full_prompt)

            action_m = ACTION_RE.search(raw)
            final_m = FINAL_RE.search(raw)

            # If final found, return it
            if final_m:
                return final_m.group(1).strip()

            # If action found
            if action_m:
                tool_name = action_m.group(1).strip()
                tool_arg = action_m.group(2).strip().strip('"')

                # If tool exists, call it
                tool_fn = self.tools.get(tool_name)
                if tool_fn:
                    observation = tool_fn(tool_arg)
                    history.append(f"ACTION: {tool_name}: {tool_arg}")
                    history.append(f"Observation: {observation}")
                    continue  # next step
                else:
                    # Unknown tool — treat as FINAL
                    return f"FINAL: {tool_arg}"

            # If neither action nor final, treat raw as FINAL
            return f"FINAL: {raw.strip()}"

        # Steps exhausted — force a final assessment
        final_prompt = f"{prompt}\n{''.join(history)}\n\nNow produce a FINAL assessment given the above."
        out = self._call_llm(final_prompt)
        final_m = FINAL_RE.search(out)
        if final_m:
            return final_m.group(1).strip()
        return f"FINAL: {out.strip()}"
