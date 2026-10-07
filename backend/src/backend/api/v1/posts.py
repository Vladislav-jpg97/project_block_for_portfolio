from fastapi import APIRouter
from starlette import status
from backend.api.v1.feed import FeedType
from backend.schemas.pagination import PaginatedResponse
from backend.schemas.post import PostCreate, PostBrief, PostRead, PostUpdate

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_post(body: PostCreate):
    return {
        "msg": "post created",
    }


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[PostBrief],
)
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


@router.get(
    "/{post_id}",
    response_model=PostRead
)
async def get_post(slug: str):
    return {
        "id": slug,
        "title": f"Post : #{slug}",
        "slug": f"post_{slug}",
        "hashed_password": "secret",
        "internal_id": 12345
    }


@router.patch(
    "/{post_id}",
)
async def update_post(
        post_id: int,
        body: PostUpdate,
):
    pass


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(post_id: int):
    return None


@router.patch(
    "/{post_id}/publish",
)
async def publish_post(
        post_id: int,
):
    pass


@router.post(
    "/{post_id}/vote",
    status_code=status.HTTP_201_CREATED,
)
async def vote_post(
        post_id: int,
):
    pass


@router.delete(
    "/{post_id}/vote",
    status_code=status.HTTP_204_NO_CONTENT
)
async def unvote_post(post_id: int):
    pass


@router.post(
    "/{post_id}/bookmark",
    status_code=status.HTTP_201_CREATED, )
async def bookmark_post(
        post_id: int
):
    pass


@router.delete(
    "/{post_id}/bookmark",
    status_code=status.HTTP_204_NO_CONTENT
)
async def unbookmark_post(post_id: int):
    pass
