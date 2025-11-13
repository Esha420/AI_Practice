import chromadb

def get_chroma_collection(collection_name="knowledge-base"):
    # Initialize the new default Chroma client (persistent by default)
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Create or load collection
    collection = client.get_or_create_collection(collection_name)
    return collection
