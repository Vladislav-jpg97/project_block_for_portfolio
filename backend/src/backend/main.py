from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from redis.asyncio import Redis

from backend.api.v1.feed import router as feeds_router
from backend.api.v1.posts import router as posts_router
from backend.api.v1.user import router as user_router
from backend.api.v1.auth import router as auth_router
from backend.api.v1.tags import router as tags_router
from backend.api.v1.category import router as categories_router
from backend.api.v1.comments import router as comments_router
from backend.core.config import settings
from backend.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ADDED: Один Redis-пул на приложение закрывается вместе с SQLAlchemy engine.
    redis = Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )
    app.state.redis = redis
    try:
        yield
    finally:
        await redis.aclose()
        await engine.dispose()


app = FastAPI(
    title="DevTalks",
    description="Платформа для технических статей",
    version="0.1.0",
    lifespan=lifespan,
)

# Настройка CORS для работы с Next.js и другими клиентами
origins = [
    "http://localhost:3000",  # Стандартный порт Next.js
    "http://127.0.0.1:3000",
    "http://localhost:3001",  # Альтернативный порт для Docker при занятом 3000
    "http://127.0.0.1:3001",
    "http://localhost:5173",  # Vite (если пригодится)
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST, PUT, DELETE, PATCH и т.д.)
    allow_headers=["*"],  # Разрешаем любые заголовки (включая Authorization для JWT)
)


@app.get("/")
async def root():
    return {"message": "DevTalks API is running"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


app.include_router(posts_router, prefix="/api/v1")
app.include_router(feeds_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(tags_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.mount(
    "/api/v1/media/avatars",
    StaticFiles(directory=str(settings.avatar_storage_dir), check_dir=False),
    name="avatars",
)