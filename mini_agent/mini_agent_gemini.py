import os
import re
import json
from tools.search_tool import search_tool
from tools.calculator_tool import calculator
from tools.weather_tool import weather_tool
from tools.code_tool import code_tool
from tools.news_tool import news_tool
from tools.crypto_tool import crypto_tool
from tools.github_tool import github_tool

# Import Google GenAI SDK
from google import genai

# Initialize Gemini client
API_KEY = os.getenv("GOOGLE_API_KEY")
client = genai.Client(api_key=API_KEY)

# Tool registry
TOOL_MAP = {
    "weather_tool": weather_tool,
    "calculator": calculator,
    "search_tool": search_tool,
    "code_tool": code_tool,
    "news_tool": news_tool,
    "crypto_tool": crypto_tool,
    "github_tool": github_tool
}

# Helper: extract math expressions
def extract_math_expression(text, base_value=None):
    text = text.lower().replace("plus", "+").replace("minus", "-") \
        .replace("times", "*").replace("multiplied", "*").replace("divided", "/")
    numbers = re.findall(r"[\d\.]+", text)
    operators = re.findall(r"[\+\-\*\/]", text)
    if not numbers:
        return None
    expr = ""
    if base_value is not None:
        expr += str(base_value)
        for op, num in zip(operators, numbers):
            expr += op + num
    else:
        for n, op in zip(numbers, operators + [""]):
            expr += n + op
    return expr

# MiniAgent class with memory
class MiniAgent:
    def __init__(self):
        self.memory = []

    def run(self, user_input):
        """
        Run the Gemini-powered agent with dynamic tool calls.
        """
        memory_context = "\n".join(self.memory)
        prompt = f"""
You are an AI agent that can use the following tools:
- weather_tool(city)
- calculator(expression)
- search_tool(query)
- code_tool(code_snippet)
- news_tool(query)
- crypto_tool()
- github_tool(owner, repo)

Memory of previous results:
{memory_context}

Decide which tool to call for the user input and return JSON like:
{{"tool": "<tool_name>", "input": <input_for_tool>}}

User Input: {user_input}
"""

        # Call Gemini
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            temperature=0.2,
            max_output_tokens=500,
            text=prompt
        )
        raw_output = response.output_text.strip()

        try:
            tool_call = json.loads(raw_output)
        except:
            tool_call = self.simulated_decide_tool(user_input)

        tool_name = tool_call.get("tool")
        tool_input = tool_call.get("input")

        # Call the correct tool
        if tool_name in TOOL_MAP:
            if tool_name == "crypto_tool":
                result = TOOL_MAP[tool_name]()
            elif tool_name == "github_tool" and isinstance(tool_input, list):
                result = TOOL_MAP[tool_name](*tool_input)
            else:
                result = TOOL_MAP[tool_name](tool_input)
        else:
            result = "Could not determine which tool to use."

        # Handle math after weather
        if tool_name == "weather_tool" and "°" in result:
            temp_value = float(result.split("°")[0])
            math_expr = extract_math_expression(user_input, base_value=temp_value)
            if math_expr:
                calc_result = calculator(math_expr)
                result = f"The adjusted temperature is {calc_result}°C."

        # Store input/result in memory
        self.memory.append(f"{user_input} -> {result}")
        return result

    def simulated_decide_tool(self, user_input):
        """
        Fallback if Gemini output is not valid JSON
        """
        user_lower = user_input.lower()
        if "temperature" in user_lower or "weather" in user_lower:
            city_match = re.search(r'\b(?:in|at)\s+([A-Za-z\s]+)', user_input)
            city = city_match.group(1).strip() if city_match else "Unknown"
            return {"tool": "weather_tool", "input": city}
        elif any(op in user_lower for op in ["+", "-", "*", "/"]):
            expr = extract_math_expression(user_input)
            return {"tool": "calculator", "input": expr}
        elif "bitcoin" in user_lower or "crypto" in user_lower:
            return {"tool": "crypto_tool", "input": None}
        elif "commit" in user_lower or "repo" in user_lower:
            repo_match = re.findall(r"([\w\-]+)/([\w\-]+)", user_input)
            if repo_match:
                owner, repo = repo_match[0]
                return {"tool": "github_tool", "input": [owner, repo]}
        else:
            return {"tool": "search_tool", "input": user_input}
