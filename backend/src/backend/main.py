from fastapi import FastAPI

from backend.api.v1.feed import router as feeds_router
from backend.api.v1.posts import router as posts_router
from backend.api.v1.user import router as user_router
from backend.api.v1.auth import router as auth_router



app = FastAPI(
    title="DevTalks",
    description="Платформа для технических статей",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "DevTalks API is running"}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


app.include_router(posts_router, prefix="/api.v1")
app.include_router(feeds_router, prefix="/api.v1")
app.include_router(user_router, prefix="/api.v1")
app.include_router(auth_router, prefix="/api.v1")