import json
from db.chroma_client import get_chroma_collection
from embeddings.embedding_utils import get_embedding

collection = get_chroma_collection()

with open("data/sample_docs.json", "r") as f:
    docs = json.load(f)

for doc in docs:
    emb = get_embedding(doc["text"])
    collection.add(
        ids=[doc["id"]],
        embeddings=[emb],
        documents=[doc["text"]],
        metadatas=[doc["metadata"]]
    )

print("✅ Documents successfully stored in ChromaDB!")
