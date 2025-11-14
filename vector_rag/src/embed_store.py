import json
from db.chroma_client import get_chroma_collection
from embeddings.embedding_utils import get_embedding

DATA_PATH = "data/sample_docs.json"
MODEL_NAME = "all-mpnet-base-v2"

def load_data_into_chroma():
    collection = get_chroma_collection()

    if collection.count() == 0:
        print("Loading documents into Chroma...")
        with open(DATA_PATH, "r") as f:
            docs = json.load(f)

        for doc in docs:
            emb = get_embedding(doc["text"], MODEL_NAME)
            collection.add(
                ids=[doc["id"]],
                embeddings=[emb],
                documents=[doc["text"]],
                metadatas=[doc.get("metadata", {})]
            )

        print(f"Loaded {len(docs)} documents.")
    else:
        print(f"Chroma contains {collection.count()} documents.")
