from fastapi import FastAPI, Query
import json
from db.chroma_client import get_chroma_collection
from embeddings.embedding import get_embedding

app = FastAPI()
collection = get_chroma_collection()

DATA_PATH = "data/sample_docs.json"

def ensure_data_loaded():
    """Load data into Chroma if the collection is empty."""
    count = collection.count()
    if count == 0:
        print(" No data found in Chroma. Loading from dataset...")
        with open(DATA_PATH, "r") as f:
            docs = json.load(f)
        for doc in docs:
            emb = get_embedding(doc["text"])
            collection.add(
                ids=[doc["id"]],
                embeddings=[emb],
                documents=[doc["text"]],
                metadatas=[doc["metadata"]],
            )
        print(f" Loaded {len(docs)} documents into Chroma.")
    else:
        print(f" Found {count} existing documents in Chroma.")

# Load automatically when the API starts
ensure_data_loaded()

@app.get("/search")
def search(query: str = Query(...)):
    query_emb = get_embedding(query)
    results = collection.query(query_embeddings=[query_emb], n_results=3)
    output = [
        {
            "text": doc,
            "score": round(1 - score, 2),
            "source": meta["source"]
        }
        for doc, score, meta in zip(results['documents'][0], results['distances'][0], results['metadatas'][0])
    ]
    return {"query": query, "results": output}
