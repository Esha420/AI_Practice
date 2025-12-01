# data_loader.py
import os
from dotenv import load_dotenv

# Google GenAI SDK
import google.generativeai as genai

from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter

load_dotenv()

# configure genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Use a Gemini embedding model — gemini embedding models (e.g. gemini-embedding-001) typically return 3072 dims
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 3072  # keep as original

splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)


def load_and_chunk_pdf(path: str):
    docs = PDFReader().load_data(file=path)
    texts = [d.text for d in docs if getattr(d, "text", None)]
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))
    return chunks


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Clean Gemini embedding function (OpenAI-style).
    Returns a list of embedding vectors, one per input text.
    """
    response = genai.embed_content(
        model=EMBED_MODEL,
        content=texts,
    )
    
    # response.embedding → list[list[float]]
    # response.embeddings → list of embeddings (SDK-dependent)
    if hasattr(response, "embeddings"):
        return [e["embedding"] if isinstance(e, dict) else e.embedding for e in response.embeddings]
    
    # fallback: single batch return
    return response["embedding"]