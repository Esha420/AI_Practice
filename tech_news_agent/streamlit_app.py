#streamlit_app.py
import streamlit as st
import json
import re 
import time

from crew import evaluate_agent_run
from agents.researcher import news_researcher
from agents.writer import news_writer
from agents.fact_checker import fact_checker
from tasks.research_task import research_task
from tasks.writing_task import write_task
from tasks.fact_check_task import fact_check_task
from memory.memory_manager import MemoryManager 


# ---------------- Helper Functions ----------------

def safe_json_loads(text):
    """
    Safely loads JSON from a string, handling the common case where the
    string contains a JSON object wrapped in markdown code fences
    (e.g., '```json\n{...}\n```').
    """
    # 1. Look for a JSON code block pattern
    match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
    
    if match:
        # Extract the content inside the '```json' block
        json_string = match.group(1).strip()
    else:
        # Assume the text is a pure JSON string and try to clean up
        json_string = text.strip()

    try:
        # Try to load the cleaned string
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        # print(f"JSON Decode Error: {e} for string: {json_string[:200]}...") # Optional: for debugging
        return None

def clean_research_output(raw_output):
    data = safe_json_loads(raw_output)
    if not data:
        return "No research artifacts found. (JSON parsing failed or empty response.)"
    
    # The 'artifacts' key might be inside the main object, and the 'final_answer' is the summary
    
    # Display the final summary/answer first
    final_answer = data.get("final_answer", "")
    out_lines = [f"**Final Research Summary:**\n{final_answer}\n"]
    
    # Display artifacts
    artifacts = data.get("artifacts", {})
    urls = artifacts.get("urls", [])
    facts = artifacts.get("facts_saved", [])
    
    out_lines.append("---")
    
    if urls:
        out_lines.append("### 🔗 URLs Visited")
        # Use simple link formatting that works well in markdown
        out_lines += [f"- [{u.split('/')[2].split('.')[0]}...](**{u}**)" for u in urls] 
    if facts:
        out_lines.append("### 📝 Facts Saved")
        out_lines += [f"- {f}" for f in facts]
        
    return "\n".join(out_lines)

def clean_writer_output(raw_output):
    data = safe_json_loads(raw_output)
    if data and "final_answer" in data:
        return data["final_answer"]
    return "No article generated. (JSON parsing failed or 'final_answer' missing.)"

def clean_fact_checker_output(raw_output):
    data = safe_json_loads(raw_output)
    if not data or "reasoning_log" not in data:
        return "No reasoning log available. (JSON parsing failed or 'reasoning_log' missing.)"
    log = data["reasoning_log"]
    lines = []
    # If the log is a string (e.g., from a tool output failure), handle it as is
    if isinstance(log, str):
        return f"Raw log output:\n{log}"
        
    for step in log:
        step_type = step.get("type", "").capitalize()
        content = step.get("content", "")
        # Use Markdown blockquote for better display of log steps
        lines.append(f"**Step {step.get('step', '?')} — {step_type}**\n> {content.replace('\n', '\n> ')}\n")
    return "\n".join(lines)

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="AI News Crew", layout="wide")
st.title("📰 AI News Generation Crew")
st.write("Enter a topic to run the full CrewAI pipeline.")

topic = st.text_input("Enter a Topic", value="Use of technology in farming")
run_button = st.button("Run Crew Pipeline")

if run_button:
    if not topic.strip():
        st.error("Please enter a valid topic.")
        st.stop()

    # 🎯 REQUIRED FIX 2: Instantiate the Memory Manager here
    memory_manager = MemoryManager() 

    st.info("Running pipeline...")
    inputs = {"topic": topic}
    progress = st.progress(0)

    # Tabs
    research_tab, writer_tab, fact_tab = st.tabs(
        ["🔍 Research Output", "✍️ Writing Output", "✔️ Fact-Check Output"]
    )

    # Variables to pass data between steps
    research_data = None
    writer_clean = "No article generated yet."
    urls = []
    
    # 🎯 REQUIRED FIX 4: Initialize fact_clean to prevent NameError if step 3 fails
    fact_clean = "Fact checker failed to run or crashed (output variable not assigned)."


    # ---------------- Research ----------------
    with st.spinner("Step 1/3: Running Research Agent..."):
        try:
            # 🎯 REQUIRED FIX 3A: Pass memory_manager
            raw_research = evaluate_agent_run(news_researcher, research_task, inputs, memory_manager)
            research_data = safe_json_loads(raw_research)
        except Exception as e:
            st.error(f"Research Agent failed: {e}")
            raw_research = "" # Ensure it's not None/unparsed

    with research_tab:
        st.subheader("🔍 Research Summary")
        if research_data:
            research_clean = clean_research_output(raw_research)
            st.markdown(research_clean)
            # Extract URLs for writer *after* successful parsing
            urls = research_data.get("artifacts", {}).get("urls", []) 
        else:
             st.markdown("No research artifacts found. (Check console for errors or ensure agent output is JSON in a ```json block.)")


    progress.progress(33)

    # ---------------- Writer ----------------
    with st.spinner("Step 2/3: Running Writer Agent..."):
        writer_inputs = {"topic": topic, "urls": urls}
        
        # Check if the writer will fail due to missing research data/urls
        if not urls and not research_data:
             st.warning("Writer Agent is running without URLs because research output failed to parse.")
        
        try:
            # 🎯 REQUIRED FIX 3B: Pass memory_manager
            raw_writer = evaluate_agent_run(news_writer, write_task, writer_inputs, memory_manager)
            writer_clean = clean_writer_output(raw_writer)
        except Exception as e:
             st.error(f"Writer Agent failed: {e}")

    with writer_tab:
        st.subheader("✍️ Generated Article")
        st.markdown(writer_clean)
        
    progress.progress(66)

    # ---------------- Fact Checker ----------------
    with st.spinner("Step 3/3: Running Fact Checker Agent..."):
        fact_inputs = {"topic": topic, "article": writer_clean}
        
        try:
            # 🎯 REQUIRED FIX 3C: Pass memory_manager
            raw_fact = evaluate_agent_run(fact_checker, fact_check_task, fact_inputs, memory_manager)
            fact_clean = clean_fact_checker_output(raw_fact)
        except Exception as e:
             st.error(f"Fact Checker Agent failed: {e}")

    with fact_tab:
        st.subheader("✔️ Fact Checker Reasoning")
        # 🎯 This is now safe because fact_clean was initialized above
        st.markdown(fact_clean) 

    progress.progress(100)
    st.success("Crew pipeline completed!")