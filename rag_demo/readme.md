# Retrieval-Augmented Generation (RAG) API using ChromaDB + Gemini + MiniLM

This module implements a **modular RAG (Retrieval-Augmented Generation)** system that connects the preprocessed text data to **Google Gemini** via **FastAPI**.  
It uses **SentenceTransformer embeddings** and **ChromaDB** as the vector store to retrieve relevant context for a given query.

---


## Overview

This system allows us to query our own knowledge base using a **retrieval + generation** approach.

**Workflow:**
1. Load preprocessed chunks from `embeddings_ready.jsonl`.
2. Embed and store them into **ChromaDB** using `all-MiniLM-L6-v2`.
3. When a query is received:
   - Retrieve the **top-k most relevant chunks** from the vector database.
   - Combine them as **context** for the **Gemini model**.
   - Generate a final **context-aware answer**.
4. Return both the generated answer and the **source documents** used.

---

## Components

### 1. `loader.py`
**Purpose:** Loads preprocessed text chunks from a `.jsonl` file into memory.

- **Input:** `embeddings_ready.jsonl`
- **Output:** Python list of dictionaries with keys — `id`, `text`, and `metadata`.

**Key Features:**
- Optionally filter chunks by their source (e.g., only from a specific file).
- Retrieve a specific chunk by its unique ID.

### 2. `vector_store.py`
**Purpose:** Handles all embedding and retrieval operations via ChromaDB.
- **Embedding model:** all-MiniLM-L6-v2
- **Vector database:** ChromaDB

### Responsibilities:
- Convert text chunks into vector embeddings.
- Store them in a ChromaDB collection.
- Perform similarity search for a query to find the most relevant chunks.

### 3. `rag_api.py`
**Purpose:** Provides a FastAPI interface to query the RAG pipeline.
- Loads chunks and initializes the vector store on startup.
- Accepts user questions and retrieves context dynamically.
- Uses Google Gemini (via google.generativeai) to generate answers.

## To run the server:
`uvicorn rag_api:app --host 0.0.0.0 --port 8000 --reload`

**Send a sample query:**
`curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -d '{"question": "What is artificial intelligence?", "top_k": 3}'
`


