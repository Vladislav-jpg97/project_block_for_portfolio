from typing import Annotated

from fastapi import Depends, Request
from redis.asyncio import Redis

from backend.core.cache import CacheService


async def get_redis_client(request: Request) -> Redis:
    redis_client: Redis | None = getattr(request.app.state, "redis", None)
    if redis_client is None:
        raise RuntimeError("Redis client was not initialized by the application lifespan")
    return redis_client

RedisDep = Annotated[
    Redis,
    Depends(get_redis_client),
]


async def get_cache_service(
        redis: RedisDep,
) -> CacheService:
    return CacheService(redis)

CacheServiceDep = Annotated[
    CacheService,
    Depends(get_cache_service),
]