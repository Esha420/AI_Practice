from db.chroma_client import get_chroma_collection
from embeddings.embedding_utils import get_embedding

MODEL_NAME = "all-mpnet-base-v2"

def get_context(query: str, top_k=3):
    collection = get_chroma_collection()
    query_emb = get_embedding(query, MODEL_NAME)
    
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=top_k,
        include=["documents"]
    )

    context = " ".join(results["documents"][0])
    return context
