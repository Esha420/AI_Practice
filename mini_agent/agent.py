# agent.py
from tools import search_tool, calculator, weather_tool
import re

# 1️⃣ Tool registry
TOOLS = {
    "weather_tool": weather_tool,
    "calculator": calculator,
    "search_tool": search_tool
}

def extract_city(text):
    """Extract city name after 'in' or 'at'."""
    match = re.search(r'\b(?:in|at)\s+([A-Za-z\s]+)', text)
    if match:
        city = match.group(1).strip()
        # Stop at numbers or math words
        city = re.split(r'\s+(plus|minus|times|multiplied|divided|\d+)', city)[0]
        return city
    return None

def extract_math_expression(text, base_value=None):
    """
    Extract math expression from text.
    If base_value is provided, prepend it (e.g., temperature + 10).
    Supports +, -, *, /.
    """
    # Convert words to symbols
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

def decide_tool(user_input):
    """
    Simulate LLM reasoning: decide which tool to use and return plan.
    """
    user_lower = user_input.lower()

    # Weather
    if "temperature" in user_lower or "weather" in user_lower:
        city = extract_city(user_input)
        if city:
            plan = {
                "tool": "weather_tool",
                "input": city,
                "reason": f"User asked for temperature/weather in {city}."
            }
            return plan
        else:
            return {"tool": None, "input": "Please specify a city.", "reason": "No city mentioned."}

    # Calculator
    elif "calculate" in user_lower or any(op in user_lower for op in ["+", "-", "*", "/"]):
        expr = extract_math_expression(user_input)
        if expr:
            return {"tool": "calculator", "input": expr, "reason": "User asked for a calculation."}
        return {"tool": None, "input": "Cannot extract expression.", "reason": "Failed parsing math."}

    # Search
    elif "search" in user_lower:
        query = user_lower.replace("search", "").strip()
        return {"tool": "search_tool", "input": query, "reason": "User asked to search for something."}

    # Unknown
    return {"tool": None, "input": "I don't know which tool to use.", "reason": "No matching tool found."}

def mini_agent(user_input):
    # Step 1: Plan (simulate LLM reasoning)
    plan = decide_tool(user_input)
    print(f"[Agent Plan] Reason: {plan['reason']} | Tool: {plan['tool']} | Input: {plan['input']}")

    tool_name = plan["tool"]
    tool_input = plan["input"]

    if not tool_name:
        return tool_input

    # Step 2: Execute tool
    result = TOOLS[tool_name](tool_input)

    # Step 3: Handle math after weather
    if tool_name == "weather_tool" and "°" in result:
        temp_value = float(result.split("°")[0])
        math_expr = extract_math_expression(user_input, base_value=temp_value)
        if math_expr:
            calc_result = calculator(math_expr)
            return f"The adjusted temperature is {calc_result}°C."
        return f"The temperature in {tool_input} is {result}."

    return result
