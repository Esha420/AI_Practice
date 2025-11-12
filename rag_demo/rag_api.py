# rag_api.py
from fastapi import FastAPI
from pydantic import BaseModel
from loader import ChunkLoader
from vector_store import VectorStore
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    raise EnvironmentError("GOOGLE_API_KEY not found. Check your .env file or environment variables.")

# Configure Gemini
genai.configure(api_key=api_key)


# Initialize FastAPI app
app = FastAPI(title="RAG API with Gemini")

# Load preprocessed chunks and initialize vector store
loader = ChunkLoader("embeddings_ready.jsonl")
chunks = loader.load()
vector_store = VectorStore()
vector_store.add_chunks(chunks)

class Query(BaseModel):
    question: str
    top_k: int = 3

@app.post("/query")
def query_rag(q: Query):
    """Main RAG query endpoint"""
    # Retrieve top-k most relevant chunks
    retrieved_texts, retrieved_metas = vector_store.query(q.question, top_k=q.top_k)
    context = "\n\n".join(retrieved_texts)
    sources = [meta.get("source", "unknown") for meta in retrieved_metas]

    # Compose the RAG prompt
    prompt = f"""
    You are a helpful AI assistant. 
    Use the following context to answer the question concisely.
    
    Context:
    {context}

    Question: {q.question}
    Answer:
    """

    # Generate response using Gemini
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        answer = response.text.strip()
    except Exception as e:
        answer = f"[Error generating response: {e}]"

    return {
        "answer": answer,
        "sources": list(set(sources))
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rag_api:app", host="0.0.0.0", port=8000, reload=True)
