import asyncio
from pathlib import Path
import time
import nest_asyncio
import streamlit as st
import inngest
from dotenv import load_dotenv
import os
import requests

load_dotenv()
nest_asyncio.apply()

st.set_page_config(page_title="RAG PDF App", page_icon="📄", layout="centered")


# ---------------------- Inngest Client ----------------------
@st.cache_resource
def get_inngest_client() -> inngest.Inngest:
    return inngest.Inngest(app_id="rag_app", is_production=False)


def save_uploaded_pdf(file) -> Path:
    uploads_dir = Path("uploads")
    uploads_dir.mkdir(parents=True, exist_ok=True)
    file_path = uploads_dir / file.name
    file_path.write_bytes(file.getbuffer())
    return file_path


async def send_rag_ingest_event(pdf_path: Path) -> str:
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/ingest_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )
    return result[0]  # return event_id


async def send_summary_event(pdf_path: Path) -> str:
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/summarize_pdf",
            data={
                "pdf_path": str(pdf_path.resolve()),
                "source_id": pdf_path.name,
            },
        )
    )
    return result[0]


async def send_rag_query_event(question: str, top_k: int) -> str:
    client = get_inngest_client()
    result = await client.send(
        inngest.Event(
            name="rag/query_pdf_ai",
            data={"question": question, "top_k": top_k},
        )
    )
    return result[0]


# ---------------------- Helpers ----------------------
def _inngest_api_base() -> str:
    return os.getenv("INNGEST_API_BASE", "http://127.0.0.1:8288/v1")


def fetch_runs(event_id: str) -> list[dict]:
    url = f"{_inngest_api_base()}/events/{event_id}/runs"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json().get("data", [])


def wait_for_run_output(event_id: str, timeout_s: float = 120, poll_interval_s: float = 0.5) -> dict:
    start = time.time()
    last_status = None
    
    while True:
        runs = fetch_runs(event_id)
        if runs:
            run = runs[0]
            status = run.get("status")
            last_status = status or last_status

            if status in ("Completed", "Succeeded", "Success", "Finished"):
                return run.get("output", {})
            if status in ("Failed", "Cancelled"):
                raise RuntimeError(f"Function run {status}")
        
        if time.time() - start > timeout_s:
            raise TimeoutError(f"Timed out (last status: {last_status})")

        time.sleep(poll_interval_s)


# ============================================================
# ---------------------- UI SECTION ---------------------------
# ============================================================

st.title("📄 RAG PDF Assistant")

# -------------------------------------------------------------
# 1. PDF Upload + Ingest
# -------------------------------------------------------------
st.header("📥 Ingest a PDF")

uploaded = st.file_uploader("Upload a PDF", type=["pdf"], accept_multiple_files=False)

if uploaded:
    with st.spinner("Uploading and triggering ingestion..."):
        pdf_path = save_uploaded_pdf(uploaded)
        event_id = asyncio.run(send_rag_ingest_event(pdf_path))

    st.success(f"Triggered ingestion for: {pdf_path.name}")
    st.caption("Summary will auto-generate after ingestion completes.")

    # Manual summary trigger
    if st.button("🔍 Generate Summary Manually"):
        with st.spinner("Triggering summary workflow..."):
            sum_event_id = asyncio.run(send_summary_event(pdf_path))
            output = wait_for_run_output(sum_event_id)
            summary = output.get("summary", "")
            st.subheader("PDF Summary")
            st.write(summary if summary else "(No summary returned)")


st.divider()

# -------------------------------------------------------------
# 2. Query Section
# -------------------------------------------------------------
st.header("💬 Ask a question about your PDFs")

with st.form("rag_query_form"):
    question = st.text_input("Enter your question:")
    top_k = st.number_input("How many chunks to retrieve?", min_value=1, max_value=20, value=5)
    submitted = st.form_submit_button("Ask")

    if submitted and question.strip():
        with st.spinner("Querying your ingested PDFs..."):
            event_id = asyncio.run(send_rag_query_event(question.strip(), top_k))
            output = wait_for_run_output(event_id)

        st.subheader("Answer")
        st.write(output.get("answer", "(No answer)"))

        sources = output.get("sources", [])
        if sources:
            st.caption("📚 Sources")
            for src in sources:
                st.write(f"- {src}")
