# main.py

import logging
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai
from dotenv import load_dotenv
import uuid
import os
import datetime
import asyncio

from data_loader import load_and_chunk_pdf, embed_texts
from vector_db import QdrantStorage
from custom_types import RAQQueryResult, RAGSearchResult, RAGUpsertResult, RAGChunkAndSrc
from safety import is_safe_input, sanitize_output
from slack import send_slack_message

import google.generativeai as genai

load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

_gemini_model = genai.GenerativeModel("models/gemini-2.0-flash")

inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer()
)

# ----------------------- INGEST PDF -----------------------
@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/ingest_pdf"),
    throttle=inngest.Throttle(limit=2, period=datetime.timedelta(minutes=1)),
    rate_limit=inngest.RateLimit(limit=1, period=datetime.timedelta(hours=4), key="event.data.source_id"),
)
async def rag_ingest_pdf(ctx: inngest.Context):
    def _load(ctx: inngest.Context) -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

    def _upsert(chunks_and_src: RAGChunkAndSrc) -> RAGUpsertResult:
        chunks = chunks_and_src.chunks
        source_id = chunks_and_src.source_id
        vecs = embed_texts(chunks)

        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]

        QdrantStorage().upsert(ids, vecs, payloads)
        return RAGUpsertResult(ingested=len(chunks))

    chunks_and_src = await ctx.step.run("load-and-chunk", lambda: _load(ctx), output_type=RAGChunkAndSrc)
    ingested = await ctx.step.run("embed-and-upsert", lambda: _upsert(chunks_and_src), output_type=RAGUpsertResult)
    
    return ingested.model_dump()

# ----------------------- QUERY PDF -----------------------
@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai")
)
async def rag_query_pdf_ai(ctx: inngest.Context):

    # SEARCH FUNCTION
    def _search(question: str, top_k: int = 5) -> RAGSearchResult:
        query_vec = embed_texts([question])[0]
        store = QdrantStorage()
        found = store.search(query_vec, top_k)
        return RAGSearchResult(contexts=found["contexts"], sources=found["sources"])

    question = ctx.event.data["question"]
    
    # SAFETY CHECK BEFORE RAG
    if not is_safe_input(question):
        return {"answer": "[Rejected] Unsafe or malicious prompt.", "sources": [], "num_contexts": 0}

    top_k = int(ctx.event.data.get("top_k", 5))

    # Retrieve contexts
    found = await ctx.step.run("embed-and-search", lambda: _search(question, top_k), output_type=RAGSearchResult)

    # Build LLM prompt
    context_block = "\n\n".join(f"- {c}" for c in found.contexts)

    user_content = (
        "Use the following context to answer the question.\n\n"
        f"Context:\n{context_block}\n\n"
        f"Question: {question}\n"
        "Answer concisely using the context above."
    )

    # Synchronous Gemini call wrapped in thread
    def _answer_llm(prompt: str) -> str:
        resp = _gemini_model.generate_content(
            prompt,
            generation_config={"temperature": 0, "max_output_tokens": 1024}
        )
        if hasattr(resp, "text"):
            return resp.text.strip()
        return str(resp)

    # Run model
    raw_answer = await asyncio.to_thread(_answer_llm, user_content)

    # Sanitize output
    safe_answer = sanitize_output(raw_answer)

    # Send Slack Notification
    send_slack_message(
        f"📘 *New RAG Query*\n"
        f"*Question:* {question}\n"
        f"*Answer:* {safe_answer[:200]}..."
    )

    return {
        "answer": safe_answer,
        "sources": found.sources,
        "num_contexts": len(found.contexts)
    }

# ----------------------- FASTAPI SERVER -----------------------
app = FastAPI()
inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf, rag_query_pdf_ai])
