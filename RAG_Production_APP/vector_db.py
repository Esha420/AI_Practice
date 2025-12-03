# vector_db.py

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from logger import log_event


class QdrantStorage:
    def __init__(self, url="http://localhost:6333", collection="docs", dim=3072):
        self.client = QdrantClient(url=url, timeout=30)
        self.collection = collection
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
            )

    def upsert(self, ids, vectors, payloads):
        points = [PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
        # qdrant client expects upsert with collection name and points
        self.client.upsert(self.collection, points=points)
        log_event("qdrant_upsert", {"count": len(points), "collection": self.collection})

    def search(self, query_vector, top_k: int = 5):
        response = self.client.query_points(
            collection_name=self.collection,
            query=query_vector,   # must be 'query'
            with_payload=True,
            limit=top_k
        )

        contexts = []
        sources = set()

        for r in response.points:  # access 'points' attribute
            payload = getattr(r, "payload", None) or {}
            if isinstance(payload, dict):
                text = payload.get("text", "")
                source = payload.get("source", "")
            else:
                text = getattr(payload, "text", "")
                source = getattr(payload, "source", "")

            if text:
                contexts.append(text)
                sources.add(source)

        log_event("qdrant_search", {"top_k": top_k, "results": len(contexts), "collection": self.collection})
        return {"contexts": contexts, "sources": list(sources)}
