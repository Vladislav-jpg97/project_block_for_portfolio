from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from backend.core.cache import CacheService
from backend.core.config import settings


async def get_redis_client() -> Redis:
    return Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )

RedisDep = Annotated[
    Redis,
    Depends(get_redis_client),
]

async def get_cache_service(
        redis: Redis,
) -> CacheService:
    return CacheService(redis)

CacheServiceDep = Annotated[
    CacheService,
    Depends(get_cache_service),
]