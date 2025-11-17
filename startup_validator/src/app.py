# src/app.py
import streamlit as st
import os
from dotenv import load_dotenv

load_dotenv()

from llm.gemini import GeminiClient
from agent.react_agent import ReactAgent
from prompts import SYSTEM_PROMPT

st.set_page_config(page_title="Startup Idea Validator", page_icon="🚀")

st.title("🚀 Startup Idea Validator (Gemini)")

st.markdown(
    """
This demo validates a startup idea by performing market research (Firecrawl if configured),
checking Hacker News sentiment, and searching GitHub for similar projects. It uses Google AI Studio (Gemini) as the LLM.
"""
)

with st.sidebar:
    st.header("Configuration")
    st.write("Make sure you configured `.env` with GOOGLE_API_KEY and optional FIRECRAWL_API_KEY, GITHUB_TOKEN.")
    st.caption("If Firecrawl is not configured the agent will skip market crawling.")

model = st.text_input("Gemini model", value=os.getenv("GEMINI_MODEL", "gemini-1.0"))
if st.button("Reset / Reload model"):
    st.experimental_rerun()

idea = st.text_area("Describe your startup idea", height=140, placeholder="e.g., 'An AI assistant that automatically reconciles invoices for small retailers'")

col1, col2 = st.columns([1, 1])
with col1:
    steps = st.number_input("Max agent steps", min_value=1, max_value=5, value=3)
with col2:
    max_tokens = st.number_input("Max tokens per LLM call", min_value=128, max_value=2048, value=512)

if st.button("Validate idea") and idea.strip():
    st.session_state.setdefault("history", [])
    st.session_state.history.append({"role": "user", "text": idea})
    status = st.empty()
    status.info("Initializing Gemini client...")
    try:
        # Initialize local Hugging Face model instead of Gemini API
        gemini = GeminiClient()  # ✅ use default local model
    except Exception as e:
        status.error(f"Error initializing Gemini client: {e}")
        st.stop()

    agent = ReactAgent(llm=gemini, max_steps=int(steps))
    status.info("Running agent — this may take a few seconds per step.")

    with st.spinner("Validating..."):
        assessment = agent.run(idea)

    st.subheader("✅ Final Assessment")
    st.write(assessment)

