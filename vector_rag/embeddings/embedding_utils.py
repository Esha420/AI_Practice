from sentence_transformers import SentenceTransformer
from functools import lru_cache

@lru_cache(maxsize=None)
def load_model(model_name="all-mpnet-base-v2"):
    print(f"🔹 Loading embedding model: {model_name}")
    return SentenceTransformer(model_name)

def get_embedding(text: str, model_name="all-mpnet-base-v2"):
    model = load_model(model_name)
    return model.encode(text).tolist()
