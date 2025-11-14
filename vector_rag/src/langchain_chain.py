from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.gemini_client import GeminiChat
import os
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

if "GOOGLE_API_KEY" not in os.environ:
    raise RuntimeError("GOOGLE_API_KEY not found in .env")

llm = GeminiChat(model_name="gemini-1", api_key=os.environ["GOOGLE_API_KEY"])

def create_chain():
    prompt_template = """
You are a helpful AI assistant. Use the provided context to answer the question.

Context:
{context}

Question:
{query}

Provide a clear, concise answer.
"""
    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["query", "context"]
    )
    parser = StrOutputParser()

    # Runnable pipeline: Prompt -> LLM -> Parser
    chain = prompt | llm | parser
    return chain

def run_chain(chain, **kwargs):
    return chain.invoke(kwargs)
