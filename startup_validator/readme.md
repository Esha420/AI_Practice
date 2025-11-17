# Startup Idea Validator

A local AI-powered application to **validate startup ideas**. This project uses a **modular agent architecture** combined with a **language model** to provide structured assessments of startup concepts. It’s built to run **fully locally** using a free Hugging Face model (`google/flan-t5-small`), so no API keys or paid services are required.

---

## Project Overview

The Startup Idea Validator allows users to:

- Input a startup idea or concept.
- Generate a structured AI-driven assessment including feasibility, market potential, and suggestions.
- Explore the idea with auxiliary tools like market research, GitHub repository search, and Hacker News trends.

The project was originally designed for Google Gemini or OpenAI models but has been adapted to work locally with a free Hugging Face model, making it **accessible and free to run**.

---

## Architecture

The project is modular, separating concerns into different layers:

### 1. **Streamlit UI**
- **`src/app.py`**: The main entry point.
- Handles user input, displays assessments, and shows tool outputs.
- Provides a responsive interface with spinners and subheaders for feedback.

### 2. **Agent Layer**
- **`src/agents.py`**: Implements the React-style agent workflow.
- Orchestrates:
  - LLM calls
  - Tool invocation (market research, Hacker News, GitHub)
  - History tracking and action decisions

### 3. **Tools**
- **`src/tool.py/`**: External helper tools for market research, GitHub, and Hacker News data.
- Tools are called by the agent to enrich assessments and provide actionable insights.

---


### Usage
1. Clone the repository
```
git clone <repository_url>
cd startup_validator
```
2. Install requirements.txt
```
pip install requiremnts.txt
```
3. Set your environment variables:
```
FIRECRAWL_API_KEY=
GITHUB_TOKEN=
```
4. Run the Streamlit app
```streamlit run src/app.py```





