# app/api_server.py

from fastapi import FastAPI, Query
from db.chroma_client import get_chroma_collection
from embeddings.embedding_utils import get_embedding
from src.langchain_chain import create_chain, run_chain

import os, json
from dotenv import load_dotenv

# Load .env inside vector_rag/
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # up 1 level from app/
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

app = FastAPI()

MODEL_NAME = "all-mpnet-base-v2"
collection = get_chroma_collection()

DATA_PATH = os.path.join(BASE_DIR, "data", "sample_docs.json")

# Load sample data if Chroma collection is empty
def ensure_data_loaded():
    if collection.count() == 0:
        with open(DATA_PATH, "r") as f:
            docs = json.load(f)

        for doc in docs:
            emb = get_embedding(doc["text"], MODEL_NAME)
            collection.add(
                ids=[doc["id"]],
                embeddings=[emb],
                documents=[doc["text"]],
                metadatas=[doc["metadata"]],
            )

ensure_data_loaded()

@app.get("/query")
def query_rag(query: str = Query(...)):
    # 1 — Embed query
    query_emb = get_embedding(query, MODEL_NAME)

    # 2 — Retrieve docs
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=3,
        include=["documents", "distances", "metadatas"]
    )

    retrieved_docs = results["documents"][0]
    context = "\n".join(retrieved_docs)

    # 3 — Create chain
    chain = create_chain()

    # 4 — Run chain
    answer = run_chain(chain, query=query, context=context)

    return {
        "query": query,
        "answer": answer,
        "retrieved_docs": retrieved_docs
    }
