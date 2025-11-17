import os
from firecrawl import Firecrawl
from github import Github
from textblob import TextBlob
from transformers import pipeline

# --- Load tokens ---
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# --- Initialize clients ---
fc = Firecrawl(api_key=FIRECRAWL_API_KEY)
gh = Github(GITHUB_TOKEN)

# --- Initialize Hugging Face model ---
llm = pipeline("text-generation", model="EleutherAI/gpt-neo-125M")

# -------- LLM Function --------
def run_llm(prompt: str) -> str:
    """Generate text using HF model."""
    result = llm(prompt, max_length=200, do_sample=True)[0]['generated_text']
    return result

# -------- Market Research Tool --------
def market_research_tool(idea: str) -> str:
    query = f"{idea} startup market trends, competitors, market size"
    results = fc.search(query, num_results=3)
    texts = [r['text'] for r in results]
    combined_text = " ".join(texts)
    # Summarize / analyze using local LLM
    prompt = f"Summarize the market research for this startup idea: {idea}\n\nData: {combined_text}"
    summary = run_llm(prompt)
    return f"Market Research Summary:\n{summary}"

# -------- Community Sentiment Tool --------
def community_sentiment_tool(idea: str) -> str:
    sample_comments = [
        f"I love the idea of {idea}, very promising!",
        f"{idea} seems too niche, not sure it will work.",
        f"{idea} is interesting but similar things exist.",
    ]
    sentiments = [TextBlob(c).sentiment.polarity for c in sample_comments]
    avg_sentiment = sum(sentiments)/len(sentiments)
    feedback = "Positive" if avg_sentiment > 0 else "Negative"
    return f"Community Feedback: {feedback} (avg sentiment={avg_sentiment:.2f})"

# -------- Technical Feasibility Tool (GitHub) --------
def technical_feasibility_tool(idea: str) -> str:
    query = f"{idea}"
    repos = gh.search_repositories(query=query)
    repo_count = repos.totalCount
    feasibility = "Simple" if repo_count < 5 else "Challenging"
    return f"Technical Feasibility: {feasibility} (related repos found: {repo_count})"
