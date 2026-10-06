from fastapi import APIRouter

from backend.api.v1.feed import FeedType

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.get("/")
async def list_posts(
        page: int = 1,
        size: int = 10,
        q: str | None = None,
        tag: str | None = None,
        feed: FeedType = FeedType.new,
):
    return {
        "posts": [],
        "page": page,
        "size": size,
        "q": q,
        "feed": feed,
        "tag": tag,
    }


@router.get("/popular")
async def get_popular_posts():
    return {"popular_posts": []}


@router.get("/{post_id}")
async def get_post(post_id: int):
    return {"post_id": post_id, "title": f"Post : #{post_id}"}
