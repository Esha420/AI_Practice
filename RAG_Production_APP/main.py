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
from logger import log_event
from daily_report import daily_report

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
        log_event("rag_ingest", {"source_id": source_id, "chunks": len(chunks)})
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
        log_event("unsafe_query", {"input": question})
        # Send alert to dedicated Slack alerts channel
        send_slack_message(
            f"🚨 *Unsafe RAG Query Detected*\n"
            f"*User attempted input:* {question}",
            channel="#alerts"  # make sure you create this channel in Slack
        )
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
    log_event("rag_query", {"question": question, "num_contexts": len(found.contexts), "sources": found.sources})

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

# ----------------------- SUMMARIZE PDF -----------------------
@inngest_client.create_function(
    fn_id="RAG: Summarize PDF",
    trigger=[
        inngest.TriggerEvent(event="rag/ingest_pdf.complete"),
        inngest.TriggerEvent(event="rag/summarize_pdf"),
    ],
    rate_limit=inngest.RateLimit(limit=1, period=datetime.timedelta(hours=4), key="event.data.source_id"),
)
async def rag_summarize_pdf(ctx: inngest.Context):
    pdf_path = ctx.event.data["pdf_path"]
    source_id = ctx.event.data.get("source_id", os.path.basename(pdf_path))
    
    # 1. Load and chunk the PDF text
    def _load_all_text(path: str) -> str:
        # Re-use the data_loader function, then join the chunks
        chunks = load_and_chunk_pdf(path)
        return "\n\n---\n\n".join(chunks)

    all_text = await ctx.step.run("load-all-text", lambda: _load_all_text(pdf_path), output_type=str)

    # 2. Build the summarization prompt
    user_content = (
        "You are an expert summarizer. Generate a concise, yet comprehensive summary "
        "of the following document text. Structure your answer with clear headings or bullet points.\n\n"
        f"Document Text:\n{all_text}"
    )
    
    # 3. Call the LLM (wrapped in thread for async safety)
    def _summarize_llm(prompt: str) -> str:
        # Increase max output tokens for a full summary
        resp = _gemini_model.generate_content(
            prompt,
            generation_config={"temperature": 0.1, "max_output_tokens": 2048}
        )
        if hasattr(resp, "text"):
            return resp.text.strip()
        return str(resp)
        
    summary = await asyncio.to_thread(_summarize_llm, user_content)
    log_event("rag_summary", {"source_id": source_id, "summary_length": len(summary)})
    
    # 5. Send a Slack Notification with the summary
    send_slack_message(
        f"📄 *PDF Summarized*\n"
        f"*Source:* {source_id}\n"
        f"*Summary:* {summary[:400]}...", # Truncate for Slack preview
        channel="#summary"
    )

    return {
        "source_id": source_id,
        "summary": summary,
        "summary_length": len(summary)
    }

# ----------------------- FASTAPI SERVER -----------------------
app = FastAPI()
inngest.fast_api.serve(app, inngest_client, [rag_ingest_pdf, rag_query_pdf_ai, rag_summarize_pdf, daily_report])
