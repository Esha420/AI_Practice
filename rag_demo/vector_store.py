# vectorstore.py
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

class VectorStore:
    def __init__(self, collection_name="rag_collection", model_name="all-MiniLM-L6-v2"):
        # Embedding model
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=model_name)

        # Chroma client
        self.client = chromadb.Client()
        # Delete if collection exists
        if collection_name in [c.name for c in self.client.list_collections()]:
            self.client.delete_collection(name=collection_name)
        self.collection = self.client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_fn
        )

    def add_chunks(self, chunks):
        """
        Add preprocessed chunks to ChromaDB collection.
        """
        ids = [chunk["id"] for chunk in chunks]
        documents = [chunk["text"] for chunk in chunks]
        metadatas = [chunk.get("metadata", {}) for chunk in chunks]
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        print(f"Added {len(chunks)} chunks to ChromaDB collection")

    def query(self, query_text, top_k=3):
        """
        Retrieve top-k similar chunks from the vector store.
        Returns: documents (text), metadatas
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=top_k
        )
        return results['documents'][0], results['metadatas'][0]
