# scripts/compare_models.py
import os
import time
import numpy as np
import pandas as pd
from tabulate import tabulate
from db.chroma_client import get_chroma_collection
from embeddings.embedding_utils import get_embedding

# ---------------------------------------------------
# Helper function
# ---------------------------------------------------
def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# ---------------------------------------------------
# Models to compare
# ---------------------------------------------------
models = [
    "all-MiniLM-L6-v2",
    "all-mpnet-base-v2",
    "paraphrase-MiniLM-L12-v2"
]

# ---------------------------------------------------
# Sample documents (can expand later)
# ---------------------------------------------------
docs = [
    {
        "id": "1",
        "text": "Artificial Intelligence enables machines to learn from data.",
        "source": "ai_intro.txt"
    },
    {
        "id": "2",
        "text": "Reinforcement learning teaches agents to make decisions using rewards and penalties.",
        "source": "rl_notes.pdf"
    },
    {
        "id": "3",
        "text": "Deep learning uses neural networks with many layers to process data.",
        "source": "deep_learning.txt"
    }
]

query = "What is reinforcement learning?"
records = []  # to store results for CSV + summary

# ---------------------------------------------------
# Ensure outputs folder exists
# ---------------------------------------------------
os.makedirs("outputs", exist_ok=True)

# ---------------------------------------------------
# Run comparison
# ---------------------------------------------------
for model_name in models:
    print("\n==============================================")
    print(f"🔹 Testing model: {model_name}")

    # Create a collection for each model
    collection_name = f"compare_{model_name.replace('/', '_')}"
    collection = get_chroma_collection(collection_name)

    # Clear existing docs
    try:
        if collection.count() > 0:
            all_ids = collection.get(include=[])["ids"]
            if all_ids:
                collection.delete(ids=all_ids)
    except Exception:
        pass

    # ----------------- Indexing --------------------
    start_time = time.time()
    for doc in docs:
        emb = get_embedding(doc["text"], model_name)
        collection.add(
            ids=[doc["id"]],
            embeddings=[emb],
            documents=[doc["text"]],
            metadatas=[{"source": doc["source"], "id": doc["id"]}]
        )
    indexing_time = round(time.time() - start_time, 2)

    # ----------------- Query -----------------------
    start_time = time.time()
    query_emb = get_embedding(query, model_name)
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=2,
        include=["documents", "distances", "metadatas"]
    )
    query_time = round(time.time() - start_time, 2)

    # ----------------- Output ----------------------
    print(f"  Indexing time: {indexing_time}s | Query time: {query_time}s")

    for doc, dist, meta in zip(results["documents"][0], results["distances"][0], results["metadatas"][0]):
        # Retrieve the stored embedding using the ID in metadata
        doc_emb = collection.get(ids=[meta["id"]], include=["embeddings"])["embeddings"][0]

        # Compute cosine similarity
        similarity = round(cosine_similarity(query_emb, doc_emb), 3)
        print(f"   → {meta['source']} | Similarity: {similarity}")
        print(f"     {doc[:100]}...")

    # Log top result
    top_id = results["metadatas"][0][0]["id"]
    top_emb = collection.get(ids=[top_id], include=["embeddings"])["embeddings"][0]
    top_similarity = round(cosine_similarity(query_emb, top_emb), 3)
    top_result = results["metadatas"][0][0]["source"]

    records.append({
        "model": model_name,
        "embedding_dim": len(query_emb),
        "index_time(s)": indexing_time,
        "query_time(s)": query_time,
        "top_source": top_result,
        "top_similarity": top_similarity
    })

# ---------------------------------------------------
# Save results
# ---------------------------------------------------
df = pd.DataFrame(records)
df.to_csv("outputs/model_comparison_results.csv", index=False)

# Pretty print summary
print("\n\n Summary of Model Performance")
print(tabulate(df, headers="keys", tablefmt="rounded_outline"))
print("\n Results saved to: outputs/model_comparison_results.csv")
