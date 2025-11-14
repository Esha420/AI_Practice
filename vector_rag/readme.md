# Vector RAG with LangChain & GeminiChat

A **Retrieval-Augmented Generation (RAG)** system that answers user queries based on contextual documents using vector search and Gemini LLM.  

---

## Table of Contents
- [Overview](#overview)  
- [Features](#features)  
- [Architecture & Flow](#architecture--flow)  
- [Installation](#installation)  
- [Usage](#usage)   

---

## Overview
This project enables AI-powered question answering over a custom set of documents. It uses:  
- **Chroma**: Vector database for document embeddings.  
- **all-mpnet-base-v2**: Embedding model from sentence-transformers.  
- **GeminiChat**: Google Gemini LLM wrapped for LangChain.  
- **FastAPI**: Exposes a `/query` API endpoint for querying.  

**Goal:** Provide accurate, context-aware answers based on the knowledge base.  

---

## Features
- Retrieve relevant documents for a query using vector search.  
- Generate answers using Gemini LLM with context.  
- Flexible prompts for summarization, translation, and reasoning.  
- Easy API-based querying with JSON responses.  

---

## Architecture & Flow

1. **Load documents** → Embed using `all-mpnet-base-v2` → Store in Chroma.  
2. **User sends query** → Embed query → Retrieve top N similar docs.  
3. **Create context** → Pass to GeminiChat via LangChain pipeline.  
4. **Return answer** along with retrieved documents.  

**Components:**
- `app/api_server.py` → FastAPI server + query endpoint  
- `src/langchain_chain.py` → LangChain pipeline with prompts and LLM  
- `src/gemini_client.py` → Gemini LLM wrapper for LangChain  
- `db/chroma_client.py` → Chroma collection management  
- `embeddings/embedding_utils.py` → Embedding generation  

---

## Installation
 Clone the repo:  
```bash
git clone <repo_url>
cd vector_rag
pip install -r requirements.txt
```
Create a .env file in the project root:
```
GOOGLE_API_KEY=your_gemini_api_key_here
```

Start the FastAPI server:
```
uvicorn app.api_server:app --reload --port 8000
```
Query via HTTP GET or Swagger UI:
```
curl "http://127.0.0.1:8000/query?query=What%20is%20AI"
```
