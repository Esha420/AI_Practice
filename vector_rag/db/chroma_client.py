import chromadb

def get_chroma_collection(collection_name="knowledge-base"):
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection(collection_name)
    return collection
