# embeddings/embedding_utils.py
from sentence_transformers import SentenceTransformer
from functools import lru_cache

@lru_cache(maxsize=None)
def load_model(model_name: str):
    """Load a sentence transformer model once and cache it."""
    print(f"🔹 Loading model: {model_name}")
    return SentenceTransformer(model_name)

def get_embedding(text: str, model_name: str):
    """Generate an embedding for a given text using the specified model."""
    model = load_model(model_name)
    return model.encode(text).tolist()
