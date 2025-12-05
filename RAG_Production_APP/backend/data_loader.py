#data_loader.py
import os
import json
import asyncio
from dotenv import load_dotenv

# Google GenAI SDK
import google.generativeai as genai

from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SentenceSplitter
from .cache import RedisCache

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Embedding model settings
EMBED_MODEL = "gemini-embedding-001"
EMBED_DIM = 3072

# Chunking helper
splitter = SentenceSplitter(chunk_size=1000, chunk_overlap=200)


# ---------------------------------------------------------
# ASYNC PDF LOADING + CHUNKING
# ---------------------------------------------------------
async def load_and_chunk_pdf(path: str):
    """
    Asynchronously loads a PDF and splits it into text chunks.
    """
    loop = asyncio.get_running_loop()
    # Load PDF in a thread to avoid blocking
    docs = await loop.run_in_executor(None, PDFReader().load_data, path)
    texts = [d.text for d in docs if getattr(d, "text", None)]

    # Chunk text (CPU-bound, but typically fast)
    chunks = []
    for t in texts:
        chunks.extend(splitter.split_text(t))

    return chunks


# ---------------------------------------------------------
# ASYNC EMBEDDINGS + REDIS CACHE
# ---------------------------------------------------------
async def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    Asynchronously embeds texts using Gemini embeddings with Redis caching.
    """
    embeddings: list[list[float]] = []
    to_compute: list[str] = []
    index_map: list[int] = []

    redis_cache = RedisCache()

    # Check cache first
    for i, t in enumerate(texts):
        cached = await redis_cache.cache_get(f"embed:{t}")
        if cached is not None:
            # cached may already be a list, only call json.loads if it's a string
            if isinstance(cached, str):
                try:
                    cached = json.loads(cached)
                except json.JSONDecodeError:
                    pass  # fallback: keep string (unlikely for embeddings)
            embeddings.append(cached)
        else:
            index_map.append(i)
            to_compute.append(t)
            embeddings.append(None)

    # Compute embeddings for texts not in cache
    if to_compute:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: genai.embed_content(model=EMBED_MODEL, content=to_compute)
        )

        # Handle response (Gemini SDK may return different structures)
        if hasattr(response, "embeddings"):
            computed = response.embeddings
        elif isinstance(response, dict) and "embedding" in response:
            computed = response["embedding"]
        else:
            computed = response  # fallback

        # Fill embeddings and cache results
        for j, vec in enumerate(computed):
            embeddings[index_map[j]] = vec
            await redis_cache.cache_set(f"embed:{to_compute[j]}", vec)

    return embeddings
