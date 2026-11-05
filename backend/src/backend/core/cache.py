import json
from typing import Any

from fastapi.encoders import jsonable_encoder
from redis.asyncio import Redis


class CacheService:
    def __init__(self, client: Redis):
        self.client = client

    async def get(
            self,
            key: str
    ) -> Any | None:
        value = await self.client.get(key)
        if value is not None:
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
            json.dumps(jsonable_encoder(value))
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
        keys: list[str] = []
        async for key in self.client.scan_iter(match=pattern, count=100):
            keys.append(key)
            if len(keys) == 100:
                await self.client.delete(*keys)
                keys.clear()
        if keys:
            await self.client.delete(*keys)

    async def close(self):
        await self.client.aclose()
