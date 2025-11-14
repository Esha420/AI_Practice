import re
from tools.search_tool import search_tool
from tools.calculator_tool import calculator
from tools.weather_tool import weather_tool
from tools.code_tool import code_tool
from tools.news_tool import news_tool
from tools.crypto_tool import crypto_tool
from tools.github_tool import github_tool

# Tool registry
TOOL_MAP = {
    "get_weather": weather_tool,
    "calculate": calculator,
    "search": search_tool,
    "code": code_tool,
    "news": news_tool,
    "crypto": crypto_tool,
    "github": github_tool
}

# Function schemas (for documentation / simulation)
FUNCTIONS = [
    {"name": "get_weather", "description": "Get the current weather for a city", "parameters": {"city": "string"}},
    {"name": "calculate", "description": "Perform a mathematical calculation", "parameters": {"expression": "string"}},
    {"name": "search", "description": "Search for information online", "parameters": {"query": "string"}},
    {"name": "code", "description": "Execute a Python code snippet safely", "parameters": {"code_snippet": "string"}},
    {"name": "news", "description": "Fetch top news headlines", "parameters": {"query": "string"}},
    {"name": "crypto", "description": "Fetch Bitcoin price", "parameters": {}},
    {"name": "github", "description": "Fetch recent GitHub commits", "parameters": {"owner": "string", "repo": "string"}}
]

#  Helper functions
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

#  Decide which tool to use
def decide_tool(user_input):
    user_lower = user_input.lower()

    # Weather + optional math adjustment
    if "temperature" in user_lower or "weather" in user_lower:
        city = extract_city(user_input)
        if city:
            return {"tool": "get_weather", "input": city, "reason": f"User asked for temperature/weather in {city}."}
        return {"tool": None, "input": "Please specify a city.", "reason": "No city mentioned."}

    # Calculator
    elif "calculate" in user_lower or any(op in user_lower for op in ["+", "-", "*", "/"]):
        expr = extract_math_expression(user_input)
        if expr:
            return {"tool": "calculate", "input": expr, "reason": "User asked for a calculation."}
        return {"tool": None, "input": "Cannot extract expression.", "reason": "Failed parsing math."}

    # Search
    elif "search" in user_lower:
        query = user_lower.replace("search", "").strip()
        return {"tool": "search", "input": query, "reason": "User asked to search for something."}

    # Code execution for lists / aggregates
    elif any(word in user_lower for word in ["average", "mean", "sum", "max", "min", "code", "execute", "run"]):
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
                code_snippet = f"print([{nums_str}])"
            return {"tool": "code", "input": code_snippet, "reason": "User requested code execution (list operation)."}
        return {"tool": "code", "input": user_input, "reason": "User requested code execution."}

    # News
    elif any(word in user_lower for word in ["news", "headline", "trending"]):
        query = user_lower.replace("news", "").replace("headline", "").replace("trending", "").strip() or "technology"
        return {"tool": "news", "input": query, "reason": "User asked for news headlines."}

    # Crypto
    elif "bitcoin" in user_lower or "crypto" in user_lower:
        return {"tool": "crypto", "input": None, "reason": "User asked for Bitcoin/crypto price."}

    # GitHub detection
    elif "commit" in user_lower or "repo" in user_lower:
        # Look for owner/repo pattern anywhere in the input
        repo_match = re.findall(r"([\w\-]+)/([\w\-]+)", user_input)
        if repo_match:
            owner, repo = repo_match[0]
            return {"tool": "github", "input": (owner, repo), "reason": f"User asked for GitHub commits for {owner}/{repo}"}
        return {"tool": None, "input": "Please specify GitHub owner/repo (e.g., torvalds/linux).", "reason": "No valid repo found in query."}

    # Fallback
    return {"tool": None, "input": "I don't know which tool to use.", "reason": "No matching tool found."}

#  Simulated LLM function-calling with multi-tool support
def simulated_llm_function_call(user_input):
    outputs = []
    # Split multi-tool queries by 'and'
    parts = [p.strip() for p in re.split(r'\band\b', user_input, flags=re.IGNORECASE)]
    for part in parts:
        plan = decide_tool(part)
        print(f"[Simulated LLM Plan] Reason: {plan['reason']} | Tool: {plan['tool']} | Input: {plan['input']}")

        tool_name = plan["tool"]
        tool_input = plan["input"]

        if not tool_name:
            outputs.append(tool_input)
            continue

        if tool_name == "github" and isinstance(tool_input, tuple):
            result = TOOL_MAP[tool_name](*tool_input)
        elif tool_name == "crypto":
            result = TOOL_MAP[tool_name]()
        else:
            result = TOOL_MAP[tool_name](tool_input)

        # Handle math after weather
        if tool_name == "get_weather" and "°" in result:
            temp_value = float(result.split("°")[0])
            math_expr = extract_math_expression(part, base_value=temp_value)
            if math_expr:
                calc_result = calculator(math_expr)
                result = f"The adjusted temperature is {calc_result}°C."
            else:
                result = f"The temperature in {tool_input} is {result}."

        outputs.append(result)

    return "\n".join(outputs)
