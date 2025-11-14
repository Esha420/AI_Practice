#  Mini-Agent Framework (Gemini + Python Tools)

A fully custom-built **AI agent framework** powered by **Google Gemini + Python tool execution** — designed to mimic the behavior of advanced agent platforms like LangChain, OpenAI Assistants, or Dify, but implemented entirely from scratch.

This Mini-Agent supports:

- **Tool Calling** (weather, search, math, crypto, GitHub, news, code execution)  
-  **Multi-step reasoning**  
- **Python code execution sandbox**  
- **External data simulation (crypto, news, GitHub commits)**  
- **Custom intent router**  
- **Gemini function calling**  


---


---

#  Features

## ✔ 1. Dynamic Tool Calling  
The agent automatically chooses the correct tool based on user intent:

| Task | Tool |
|------|------|
| Weather + math | get_weather → calculator |
| Math operations | calculator |
| Code execution | code_tool |
| Bitcoin price | crypto_tool |
| GitHub repository commits | github_tool |
| News summaries | news_tool |
| Search queries | search_tool |

---

## ✔ 2. Multi-Step Reasoning  
The agent can chain tools:
```
User: What’s the temperature in Tokyo plus 10?

→ weather_tool("Tokyo") returns 23°
→ calculator_tool("23 + 10") returns 33°
→ final answer: 33°C
```

---

## ✔ 6. Gemini Function Calling  
Uses Google's **Gemini 2.5 Flash** to:

- interpret requests
- decide tool usage
- generate tool inputs
- combine results into answers

---

#  Architecture Overview

Your Mini-Agent is made of **five core layers**:

### 1. User → Agent Loop  
`run_agent.py` handles typing input, calling the agent, printing output.

### 2. Router (Decision Engine)  
Inside `agent.py` → `simulated_llm_function_call()`

This decides:

- intent  
- tool to use  
- parameters for the tool  
- fallback to normal chat

### 3. Tools (actual functionality)  
Each tool lives inside `tools/`.

---

#  Full Workflow

This is the full lifecycle of a user query:

### Step 1 — User asks a question  
Example:  
"What is the average of [3, 7, 9, 12]?"

### Step 2 — Router analyzes intent  
- sees a list of numbers  
- sees it’s a math question  
- decides: **use code_tool**

### Step 3 — Router generates a plan  
```
{
"reason": "User requested code execution for math",
"tool": "code",
"input": "print(sum([3,7,9,12])/4)"
}
```

### Step 4 — Tool executes  
`code_tool.py` runs the Python code safely.

### Step 5 — Output returned  
`7.75`

### Step 6 — Agent returns final answer  
"7.75"

---

#  Tools Included

## 1. Weather Tool  
Simulated weather API.

## 2. Calculator Tool  
Evaluates math expressions safely.

## 3. Code Execution Tool  
Runs Python code in a restricted environment.

## 4. Crypto Tool  
Returns a simulated Bitcoin price.

## 5. GitHub Tool  
Returns simulated commits for any repo.

## 6. News Tool  
Returns simulated top headlines.

## 7. Search Tool  
Performs fake "search queries" and responds with pre-filled data.

---

---

#  Installation
```
git clone <this repo>
pip install requirements.txt
cd mini_agent
python run_agent.py
```
### Usage
Input your queries.