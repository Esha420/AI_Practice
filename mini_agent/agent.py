import re
from tools import search_tool, calculator, weather_tool
from tools.code_tool import code_tool

# 1️⃣ Tool registry
TOOL_MAP = {
    "get_weather": weather_tool,
    "calculate": calculator,
    "search": search_tool,
    "code": code_tool
}

# 2️⃣ Function schemas
FUNCTIONS = [
    {
        "name": "get_weather",
        "description": "Get the current weather for a city",
        "parameters": {"city": "string"}
    },
    {
        "name": "calculate",
        "description": "Perform a mathematical calculation",
        "parameters": {"expression": "string"}
    },
    {
        "name": "search",
        "description": "Search for information online",
        "parameters": {"query": "string"}
    },
    {
        "name": "code",
        "description": "Execute a Python code snippet safely",
        "parameters": {"code_snippet": "string"}
    }
]

# 3️⃣ Helper functions
def extract_city(text):
    match = re.search(r'\b(?:in|at)\s+([A-Za-z\s]+)', text)
    if match:
        city = match.group(1).strip()
        city = re.split(r'\s+(plus|minus|times|multiplied|divided|\d+)', city)[0]
        return city
    return None

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

def decide_tool(user_input):
    """
    Simulate LLM deciding which tool to call.
    Handles weather, calculator, search, and code execution for common list operations.
    Always returns a dict with keys: tool, input, reason
    """
    user_lower = user_input.lower()

    # 1️⃣ Weather
    if "temperature" in user_lower or "weather" in user_lower:
        city = extract_city(user_input)
        if city:
            return {
                "tool": "get_weather",
                "input": city,
                "reason": f"User asked for temperature/weather in {city}."
            }
        return {
            "tool": None,
            "input": "Please specify a city.",
            "reason": "No city mentioned."
        }

    # 2️⃣ Basic math expressions
    elif "calculate" in user_lower or any(op in user_lower for op in ["+", "-", "*", "/"]):
        expr = extract_math_expression(user_input)
        if expr:
            return {
                "tool": "calculate",
                "input": expr,
                "reason": "User asked for a calculation."
            }
        return {
            "tool": None,
            "input": "Cannot extract expression.",
            "reason": "Failed parsing math."
        }

    # 3️⃣ Search
    elif "search" in user_lower:
        query = user_lower.replace("search", "").strip()
        return {
            "tool": "search",
            "input": query,
            "reason": "User asked to search for something."
        }

    # 4️⃣ Code execution for lists / aggregates
    elif any(word in user_lower for word in ["average", "mean", "sum", "max", "min", "code", "execute", "run"]):
        # Extract list of numbers from square brackets
        numbers = re.findall(r"\[([0-9, \.]+)\]", user_input)
        if numbers:
            nums_str = numbers[0]
            if "average" in user_lower or "mean" in user_lower:
                code_snippet = f"print(sum([{nums_str}])/len([{nums_str}]))"
            elif "sum" in user_lower:
                code_snippet = f"print(sum([{nums_str}]))"
            elif "max" in user_lower:
                code_snippet = f"print(max([{nums_str}]))"
            elif "min" in user_lower:
                code_snippet = f"print(min([{nums_str}]))"
            else:
                # fallback: just print the list
                code_snippet = f"print([{nums_str}])"
            return {
                "tool": "code",
                "input": code_snippet,
                "reason": "User requested code execution (list operation)."
            }
        # No list detected, pass full user input to code_tool
        return {
            "tool": "code",
            "input": user_input,
            "reason": "User requested code execution."
        }

    # 5️⃣ Default fallback
    return {
        "tool": None,
        "input": "I don't know which tool to use.",
        "reason": "No matching tool found."
    }



# 4️⃣ Simulated function-calling agent
def simulated_llm_function_call(user_input):
    plan = decide_tool(user_input)
    print(f"[Simulated LLM Plan] Reason: {plan['reason']} | Tool: {plan['tool']} | Input: {plan['input']}")

    tool_name = plan["tool"]
    tool_input = plan["input"]

    if not tool_name:
        return tool_input

    result = TOOL_MAP[tool_name](tool_input)

    if tool_name == "get_weather" and "°" in result:
        temp_value = float(result.split("°")[0])
        math_expr = extract_math_expression(user_input, base_value=temp_value)
        if math_expr:
            calc_result = calculator(math_expr)
            return f"The adjusted temperature is {calc_result}°C."
        return f"The temperature in {tool_input} is {result}."

    return result
