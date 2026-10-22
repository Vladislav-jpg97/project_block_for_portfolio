from fastapi import APIRouter
from starlette import status

from backend.dependencies.comment import CommentServiceDep
from backend.dependencies.post import CurrentPostDep
from backend.schemas.comment import CommentResponse, CommentCreate, CommentUpdate

router = APIRouter(
    prefix="/posts/{post_id}/comments}",
    tags=["Comments"],
)

TEMP_USER_ID = 1


@router.get("/", response_model=list[CommentResponse])
async def get_comments(
        post: CurrentPostDep,
        service: CommentServiceDep
):
    comments = await service.get_tree(post.id)
    return comments


@router.post("/")
async def create_comment(
        post: CurrentPostDep,
        body: CommentCreate,
        service: CommentServiceDep
):
    comment = await service.create(post.id, TEMP_USER_ID, body)
    return comment


@router.get("/{comment_id}")
async def get_comment(
        post: CurrentPostDep,
        comment_id: int,
        service: CommentServiceDep
):
    comment = await service.get_or_404(post.id, comment_id)
    return comment


@router.put("/{comment_id}", status_code=status.HTTP_200_OK)
async def update_comment(
        post: CurrentPostDep,
        comment_id: int,
        body: CommentUpdate,
        service: CommentServiceDep
):
    await service.update(post.id, comment_id, TEMP_USER_ID, body)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        post: CurrentPostDep,
        comment_id: int,
        service: CommentServiceDep
):
    await service.delete(post.id, comment_id, TEMP_USER_ID)
