import streamlit as st
from agents import StartupValidatorAgent

st.title("Startup Idea Validator (Local HF + Firecrawl + GitHub)")

agent = StartupValidatorAgent()

idea = st.text_input("Enter your startup idea:")

if st.button("Validate Idea") and idea.strip():
    with st.spinner("Validating your idea..."):
        report = agent.validate(idea)
    st.text_area("Validation Report", value=report, height=400)
