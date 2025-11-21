# Agentic AI News Pipeline (CrewAI)

This project implements a sophisticated Multi-Agent System (MAS) designed to autonomously research, filter, and summarize the latest technology news. Built using the CrewAI framework and powered by Google Gemini, it functions as an automated editorial pipeline, efficiently delivering concise summaries while ensuring minimal redundant processing through a built-in memory system.

## Core Objective

The primary goal is to address information overload by transforming raw, real-time news feeds into high-quality, actionable reports. The system ensures that only articles not previously processed are analyzed, optimizing API usage and maintaining a fresh daily digest.

##  Architecture and Key Features

The project follows a Sequential Pipeline Pattern where two specialized AI agents collaborate to achieve the final outcome.

### 1. Agents and Roles

| Agent | Role | Goal | Key Action |
|-------|------|------|------------|
| Senior Researcher | Data Analyst | Identify and filter relevant, non-summarized news articles from the source feed. | Executes the NewsFetcher Tool and applies memory checks. |
| Summary Reporter | Content Creator | Scrape, analyze, summarize, and compile the final report for the end-user. | Executes the ArticleScraper and GeminiSummarizer Tools. |

### 2. Tools (Capabilities)

Each agent is equipped with specialized tools to interact with the environment:

- **NewsFetcher:** Scans RSS feeds and cross-references article URLs against the project's internal memory store (`memory.json`).
- **ArticleScraper:** Extracts the clean main text content from a given URL, preparing the input for the LLM.
- **GeminiSummarizer:** Sends the scraped text to the Gemini 2.5 Flash model for summarization and ensures the URL is logged to memory upon success.

### 3. The Sequential Pipeline

The `crew.py` orchestrates a strict sequential process (`Process.sequential`):

1. **Phase 1 (Researcher):** Executes the research task, generating a list of new, unread article URLs.  
2. **Handoff:** The list of URLs becomes the input context for the Reporter.  
3. **Phase 2 (Reporter):** Processes each URL one by one (scrape, summarize, and log to memory), compiling the individual summaries into the final report document.

##  Setup and Installation

Follow these steps to get the project running locally.

### Prerequisites

- Python 3.8+
- A valid Google AI API Key

### 1. Create and Activate Virtual Environment

```bash
python -m venv llm-env
source llm-env/bin/activate  # On Windows, use `llm-env\Scripts\activate`
```

### 2. Install Dependencies
``` pip install -r requirements.txt```

### 3. Configure API Key
```
SERPER_API_KEY=_YOUR_API_KEY_
GOOGLE_API_KEY=_YOUR_API_KEY_
```

### 4. Execution
From root directory run:
```
python crew.py
```
