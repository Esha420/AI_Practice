# RAG Production App: Gemini + Qdrant + Inngest + FastAPI

A fully production-ready **Retrieval-Augmented Generation (RAG)** pipeline designed for reliable, scalable document processing and querying. This application is built with modern, asynchronous Python tools to deliver fast, context-grounded answers from uploaded PDF documents.

## Features

* **PDF Ingestion & Chunking:** Uses the **LlamaIndex sentence splitter** to create manageable, overlapping text chunks, optimizing retrieval.
* **Gemini Embeddings:** Utilizes the high-quality **`gemini-embedding-001`** model (3072-dimensional) for converting text to precise vectors.
* **Qdrant Vector Storage:** Stores vectorized chunks efficiently with critical metadata (`text` and `source`).
* **Semantic Search:** Queries the Qdrant vector database using vector similarity to find the most relevant document passages.
* **Gemini LLM Answering:** Generates highly accurate, context-grounded answers by passing only the retrieved text to the **Gemini 2.5 Flash** model.
* **Inngest-Managed Workflows:** Ensures that both the data ingestion and RAG querying processes execute **reliably, observably, and at scale** in the background.
* **FastAPI Server:** Provides a clean, modern public API layer for triggering the Inngest functions and serving the application.

---

##  Architecture & How It Works

This application operates using two reliable, decoupled workflows managed by Inngest.

### 1 Ingestion Pipeline (Triggered by `rag/ingest_pdf` event)

1.  **Load PDF:** Reads the document path specified in the event.
2.  **Split into Chunks:** Processes the text using a `SentenceSplitter`.
3.  **Generate Embeddings:** Calls the **Gemini API** to create a vector for each chunk.
4.  **Store Vectors:** Upserts the vectors, original text, and source metadata into the **Qdrant** database.

### 2️ Query Pipeline (Triggered by `rag/query_pdf_ai` event)

1.  **Embed the Question:** The user's question is vectorized using the same **Gemini embedding model**.
2.  **Search Nearest Chunks:** The query vector searches the **Qdrant** index for the top `k` most similar document chunks.
3.  **Format Context:** The retrieved text chunks are assembled into a coherent prompt.
4.  **Pass Context to Gemini LLM:** The prompt (including the question and retrieved context) is sent to **Gemini 2.5 Flash** for answer generation.
5.  **Return Response:** The final, context-grounded answer and sources are returned to the user.

---

##  Setup and Running

### Requirements

* **Python 3.10+** (Virtual environment recommended)
* **Docker** (Required for running Qdrant)

### Step 1: Install Dependencies & Set Key

```bash
# 1. Install project dependencies
pip install -r requirements.txt

# 2. Set your Gemini API Key as an environment variable
export GEMINI_API_KEY="your-key-here"
```
### Step 2: Run Qdrant Vector Database
Start the persistent Qdrant service using Docker. This command maps port 6333 and mounts a local volume for persistent storage.
```
docker run -d \
  --name qdrantRagDB \
  -p 6333:6333 \
  -v "./qdrant_storage:/qdrant/storage" \
  qdrant/qdrant
```
Verify Qdrant Status:
```
curl http://localhost:6333/collections
```

### Step 3: Run FastAPI + Inngest Server
Start the core application server. This will register the Inngest functions and expose the public API endpoints.
```
uvicorn main:app --reload --port 8000
```

### Step 4: Frontend (Streamlit)
Run the Streamlit
```
streamlit run streamlit_app.py
```