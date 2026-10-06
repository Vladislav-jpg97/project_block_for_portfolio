from fastapi import APIRouter

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/{user_id}/posts"
)
async def list_user_posts(
        user_id: int,
        page: int = 1,
        size: int = 10,
):
    return {
        "user_id": user_id,
        "page": page,
        "size": size,
        "posts": []
    }


@router.get("{user_id}/posts/{post_id}")
async def get_user_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}
