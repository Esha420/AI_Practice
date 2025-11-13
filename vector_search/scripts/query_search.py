import sys
from db.chroma_client import get_chroma_collection
from embeddings.embedding_utils import get_embedding

collection = get_chroma_collection()

def search(query: str):
    query_emb = get_embedding(query)
    results = collection.query(query_embeddings=[query_emb], n_results=3)
    
    print(f"\n🔍 Query: {query}")
    for doc, score, meta in zip(results['documents'][0], results['distances'][0], results['metadatas'][0]):
        print({
            "text": doc,
            "score": round(1 - score, 2),
            "source": meta["source"]
        })

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/query_search.py 'your query'")
    else:
        search(sys.argv[1])
