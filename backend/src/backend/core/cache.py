import json
from typing import Any

from redis.asyncio import Redis


class CacheService:
    def __init__(self, client: Redis):
        self.client = client

    async def get(
            self,
            key: str
    ):
        value = self.client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(
            self,
            key: str,
            value: Any,
            ttl: int = 300
    ):
        await self.client.setex(
            key,
            ttl,
            json.dumps(value, default=str)
        )

    async def delete(
            self,
            key: str
    ):
        await self.client.delete(key)

    async def delete_pattern(
            self,
            pattern: str
    ):
        keys = await self.client.keys(pattern)
        if keys:
            await self.client.delete(*keys)

    async def close(self):
        await self.client.aclose()
