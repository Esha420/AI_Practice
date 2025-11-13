# Vector Search with Chroma & Sentence Transformers

A simple **semantic search system** using **vector embeddings** stored in a **Chroma vector database**.  
This project allows you to query a collection of documents and retrieve semantically similar content efficiently using **sentence embeddings**.

The system uses the **best-performing embedding model (`all-mpnet-base-v2`)** for high-quality semantic retrieval.

---

## Features

- Embed documents using Sentence Transformers (`all-mpnet-base-v2`)  
- Store embeddings in a **local Chroma vector database**  
- Perform **semantic search** with cosine similarity  
- FastAPI endpoint for live search queries  
- Automatic data loading if the database is empty  

---

## Setup

1. **Clone the repository**

```bash
git clone <your-repo-url>
pip install -r requirements.txt
cd genai/vector_search
uvicorn app.main:app --reload
```
## Query Example
```curl "http://127.0.0.1:8000/search?query=What%20is%20reinforcement%20learning?"```

## Comparing Embedding Models
```python -m scripts.compare_models```

Generates ```outputs/model_comparison_results.csv```