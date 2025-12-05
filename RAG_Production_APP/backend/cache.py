# cache.py
import redis.asyncio as aioredis
import json
from typing import Any, Optional


class RedisCache:
    def __init__(self, redis_url: str = "redis://localhost:6379/0", ttl: int = 3600):
        self.redis_url = redis_url
        self.ttl = ttl
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self):
        if self.redis is None:
            self.redis = await aioredis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )

    async def cache_get(self, key: str) -> Optional[Any]:
        """Get and decode JSON value from Redis safely."""
        await self.connect()
        result = await self.redis.get(key)
        if result is None:
            return None
        # Ensure we only call json.loads on strings
        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return result
        return result

    async def cache_set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Encode dicts/lists as JSON before storing."""
        await self.connect()
        ttl = ttl or self.ttl
        # Always serialize dict or list to JSON string
        if isinstance(value, (dict, list)):
            value_to_store = json.dumps(value)
        else:
            value_to_store = value
        await self.redis.set(key, value_to_store, ex=ttl)

    async def exists(self, key: str) -> bool:
        await self.connect()
        return await self.redis.exists(key) == 1

    async def delete(self, key: str):
        await self.connect()
        await self.redis.delete(key)

    async def close(self):
        if self.redis:
            await self.redis.close()
            self.redis = None
