# vector_db.py

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from .logger import log_event
import asyncio, time

class QdrantStorage:
    def __init__(self, url="http://localhost:6333", collection="docs", dim=3072):
        self.client = QdrantClient(url=url, timeout=30)
        self.collection = collection

        if not self.client.collection_exists(collection):
            self.client.create_collection(
                collection_name=collection,
                vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
            )

    # ---------------------------
    # UPSERT WITH RETRY
    # ---------------------------
    async def upsert(self, ids, vectors, payloads):
        points = [
            PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i])
            for i in range(len(ids))
        ]

        for attempt in range(3):
            try:
                self.client.upsert(self.collection, points=points)
                break
            except Exception:
                await asyncio.sleep(0.5 * (attempt + 1))

        log_event("qdrant_upsert", {"count": len(points)})

    # ---------------------------
    # SEARCH WITH RETRY
    # ---------------------------
    def search(self, query_vector, top_k=5):
        for attempt in range(3):
            try:
                resp = self.client.query_points(
                    collection_name=self.collection,
                    query=query_vector,
                    with_payload=True,
                    limit=top_k
                )
                break
            except Exception:
                time.sleep(0.2 * (attempt + 1))

        contexts, sources = [], set()

        for r in resp.points:
            payload = r.payload or {}
            text = payload.get("text", "")
            source = payload.get("source", "")
            if text:
                contexts.append(text)
                sources.add(source)

        log_event("qdrant_search", {"results": len(contexts), "top_k": top_k})
        return {"contexts": contexts, "sources": list(sources)}
