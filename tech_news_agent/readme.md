# Tech News Multi-Agent System (CrewAI)

This project is a fully automated AI-powered multi-agent workflow for researching, summarizing, and fact-checking the latest technology news. It uses CrewAI, Gemini 2.5 Flash, custom tools, and persistent JSON-based memory to create an efficient and self-improving news pipeline.

---

## Features

### Multi-Agent Architecture
The system uses three agents:

1. Researcher Agent  
   - Searches the web  
   - Scrapes articles  
   - Detects novelty using memory  

2. Writer Agent  
   - Converts raw research into structured summaries  
   - Uses memory for writing style consistency  

3. Fact Checker Agent  
   - Verifies claims  
   - Checks persistent factual memory  
   - Cross-validates using search and scraping tools  

### Persistent Memory System
Each agent uses a custom JSON-based memory implementation:

memory/

-urls.JSON

-summaries.json

-facts.json


This allows:
- Avoiding repeated research  
- Reusing summaries  
- Storing validated facts  
- Maintaining style consistency  

### Built-in Caching
CrewAI handles:
- Tool execution caching
- LLM prompt caching

You can also add custom caching logic using the JSON memory files.

### Tools Integrated
| Tool | Purpose |
|------|---------|
| SerperDevTool | Web search |
| ScrapeTool | Extract website text |
| FactLookupTool | Check claims inside factual memory |

---

## Installation

### 1. Clone the repository
```
git clone <this-repo-url>
cd tech_news_agent
```

### 2. Create and activate environment
```
python3 -m venv llm-env
source llm-env/bin/activate
```

### 3. Install dependencies
```
pip install -r requirements.txt
```

### 4. Add environment variables
Create a `.env` file:
```
GOOGLE_API_KEY=your_key
SERPER_API_KEY=your_serper_key
```

---

## Running the System

Run the main pipeline:
```
python crew.py
```


The pipeline performs:
1. Research  
2. Writing  
3. Fact-checking  
4. Saving results to memory  

Outputs are displayed and also stored in memory files.

---

## Memory System

### How JSONMemory Works
Each agent is assigned a memory file:
- researcher_memory = JSONMemory("memory/urls.json")
- writer_memory = JSONMemory("memory/summaries.json")
- fact_checker_memory = JSONMemory("memory/facts.json")


### Cache-like behavior
Before performing research/writing/fact-checking, the system checks:

- If topic exists in urls.json → reuse research  
- If topic exists in summaries.json → reuse summary  
- If fact exists in facts.json → skip external validation  

This reduces API calls and improves speed.

---

## Tools

### Web Search  
Powered by Serper (Google Search API proxy).

### Web Scraper  
Custom built using Requests + BeautifulSoup.

### Fact Lookup Tool  
Looks into facts.json and returns:
- FACT MATCH  
- NO MATCH FOUND  

---

## Agents

### Researcher Agent
- Finds new URLs  
- Scrapes articles  
- Avoids old URLs using memory  

### Writer Agent
- Writes summaries  
- Maintains style using memory  

### Fact Checker Agent
- Verifies statements  
- Saves new validated facts  
- Checks previous facts to avoid duplication  

---

## Execution Flow

1. research_task  
2. write_task  
3. fact_check_task  
4. Output  

---

## Caching Behavior

CrewAI automatically caches:
- Tool calls (scraping, searching)  
- LLM responses (prompt-level caching)

Plus, JSON memory acts as long-term cache.

---
