# main.py

import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
from dotenv import load_dotenv
import uuid
import os
import datetime
import asyncio
import time

from .data_loader import load_and_chunk_pdf, embed_texts
from .vector_db import QdrantStorage
from .custom_types import RAQQueryResult, RAGSearchResult, RAGUpsertResult, RAGChunkAndSrc
from .safety import is_safe_input, sanitize_output
from .slack import send_slack_message
from .logger import log_event
from .daily_report import daily_report
from .cache import RedisCache
from .inngest_client import inngest_client
import google.generativeai as genai

# -----------------------------------------------------------
# ENV & CONFIG
# -----------------------------------------------------------

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_cache = RedisCache(redis_url=REDIS_URL)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
_gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")

# Track performance
def measure(fn):
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await fn(*args, **kwargs)
        log_event("latency", {"fn": fn.__name__, "latency_ms": (time.time() - start) * 1000})
        return result
    return wrapper


# ================================
# RAG: INGEST PDF
# ================================
@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
    throttle=inngest.Throttle(limit=2, period=datetime.timedelta(minutes=1)),
    rate_limit=inngest.RateLimit(limit=1, period=datetime.timedelta(hours=4), key="event.data.source_id"),
)
@measure
async def rag_ingest_pdf(ctx: inngest.Context):

    async def _load():
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = await load_and_chunk_pdf(pdf_path)  # <-- await async load
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

    async def _upsert(chunks_and_src: RAGChunkAndSrc):
        chunks = chunks_and_src.chunks
        source_id = chunks_and_src.source_id
        vecs = await embed_texts(chunks)  # <-- await async embeddings

        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]

        await QdrantStorage().upsert(ids, vecs, payloads)
        log_event("rag_ingest", {"source_id": source_id, "chunks": len(chunks)})
        return RAGUpsertResult(ingested=len(chunks))

    chunk_data = await ctx.step.run("load-and-chunk", lambda: _load(), output_type=RAGChunkAndSrc)
    result = await ctx.step.run("embed-and-upsert", lambda: _upsert(chunk_data), output_type=RAGUpsertResult)
    
    return result.model_dump()

# ================================
# RAG: QUERY PDF
# ================================
@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")
)
@measure
async def rag_query_pdf_ai(ctx: inngest.Context):

    question = ctx.event.data["question"]
    top_k = int(ctx.event.data.get("top_k", 5))

    # SAFETY CHECK
    if not is_safe_input(question):
        send_slack_message(f"🚨 Unsafe query detected: {question}", "#alerts")
        return {"answer": "[Rejected] Unsafe prompt.", "sources": [], "num_contexts": 0}

    # ------------------- CACHE CHECK -------------------
    cache_key = f"rag_q:{question}"
    cached = await redis_cache.cache_get(cache_key)
    if cached:
        return cached

    # ------------------- VECTOR SEARCH -------------------
    async def _search():
        store = QdrantStorage()
        vec = (await embed_texts([question]))[0]  # <-- await embeddings
        return store.search(vec, top_k)

    found = await ctx.step.run("embed-and-search", lambda: _search(), output_type=RAGSearchResult)

    # ------------------- COMPRESSED PROMPT -------------------
    context_block = "\n\n---\n\n".join(found.contexts)

    prompt = (
        "You are an expert assistant. Use the context below to answer the question in a "
        "clear, detailed, and well-structured way. Include explanations if needed.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )



    # ------------------- RETRY LOGIC -------------------
    async def retry_llm(prompt):
        for attempt in range(3):
            try:
                resp = await asyncio.to_thread(
                    _gemini_model.generate_content,
                    prompt,
                    generation_config={"temperature": 0, "max_output_tokens": 1024}
                )
                return resp.text.strip()
            except Exception:
                await asyncio.sleep(0.5 * (attempt + 1))
        return "LLM failed after retries."

    answer = await retry_llm(prompt)
    answer = sanitize_output(answer)

    send_slack_message(
        f"📘 *New RAG Query*\n"
        f"*Question:* {question}\n"
        f"*Answer:* {answer[:200]}...",
        channel="#general"
    )

    result = {
        "answer": answer,
        "sources": found.sources,
        "num_contexts": len(found.contexts),
    }

    await redis_cache.cache_set(cache_key, result, ttl=600)
    return result

# ================================
# RAG: SUMMARIZE PDF
# ================================
@inngest_client.create_function(
    fn_id="RAG: Summarize PDF",
    trigger=[
        inngest.TriggerEvent(event="rag/ingest_pdf.complete"),
        inngest.TriggerEvent(event="rag/summarize_pdf"),
    ],
    rate_limit=inngest.RateLimit(limit=1, period=datetime.timedelta(hours=4), key="event.data.source_id"),
)
@measure
async def rag_summarize_pdf(ctx: inngest.Context):

    pdf_path = ctx.event.data["pdf_path"]
    source_id = ctx.event.data.get("source_id", pdf_path)

    async def _load_text():
        chunks = await load_and_chunk_pdf(pdf_path)  # <-- await async load
        return "\n".join(chunks[:50])  # compress large PDFs

    text = await ctx.step.run("load-text", lambda: _load_text(), output_type=str)

    prompt = f"Summarize clearly:\n{text}"

    summary = await asyncio.to_thread(
        _gemini_model.generate_content,
        prompt,
        generation_config={"temperature": 0.1, "max_output_tokens": 2048}
    )

    summary = summary.text.strip()

    send_slack_message(f"PDF Summary for {source_id}:\n{summary[:400]}", "#summary")

    return {"summary": summary, "summary_length": len(summary), "source_id": source_id}


# ================================
# FASTAPI SERVER
# ================================
app = FastAPI()
inngest.fast_api.serve(app, inngest_client, [
    rag_ingest_pdf,
    rag_query_pdf_ai,
    rag_summarize_pdf,
    daily_report
])
