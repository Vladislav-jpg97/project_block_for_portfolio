from fastapi import APIRouter, Depends
from starlette import status

from backend.dependencies.auth import CurrentUserDep, OptionalCurrentUserDep
from backend.dependencies.post import PostServiceDep, CurrentPostDep, PublishedPostDep
from backend.schemas.pagination import Page, PaginationParams
from backend.schemas.post import PostCreate, PostBrief, PostUpdate, PostFilters, PostRead

router = APIRouter(
    prefix="/posts",
    tags=["Posts"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=PostRead,
)
async def create_post(
        body: PostCreate,
        current_user: CurrentUserDep,
        service: PostServiceDep
):
    post = await service.create(body, current_user.id)
    return post


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=Page[PostBrief],
)
async def list_posts(
        service: PostServiceDep,
        current_user: OptionalCurrentUserDep,
        filters: PostFilters = Depends(),
        pagination: PaginationParams = Depends(),

):
    return await service.get_all(
        filters,
        pagination,
        user_id=current_user.id if current_user else None,
    )


@router.get(
    "/{slug}",
    response_model=PostRead
)
async def get_post(
        slug: str,
        current_user: OptionalCurrentUserDep,
        service: PostServiceDep
):
    return await service.view_or_404(
        slug,
        user_id=current_user.id if current_user else None,
    )


@router.patch(
    "/{post_id}",
    response_model=PostRead,
)
async def update_post(
        post_id: int,
        body: PostUpdate,
        current_user: CurrentUserDep,
        service: PostServiceDep
):
    return await service.update(post_id, body, current_user.id)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_post(
        post_id: int,
        service: PostServiceDep,
        current_user: CurrentUserDep
):
    await service.delete(
        post_id,
        current_user.id
    )


@router.patch(
    "/{post_id}/publish",
)
async def publish_post(
        post: CurrentPostDep,
        service: PostServiceDep,
        current_user: CurrentUserDep,
):
    await service.publish(current_user.id, post)


@router.post(
    "/{post_id}/vote",
    status_code=status.HTTP_201_CREATED,
)
async def vote_post(
        post_id: int,
        post: PublishedPostDep,
        current_user: CurrentUserDep,
        service: PostServiceDep
):
    await service.vote_post(post, current_user)


@router.delete(
    "/{post_id}/vote",
    status_code=status.HTTP_204_NO_CONTENT
)
async def unvote_post(
        post_id: int,
        post: PublishedPostDep,
        current_user: CurrentUserDep,
        service: PostServiceDep
):
    await service.unvote_post(post, current_user)


@router.post(
    "/{post_id}/bookmark",
    status_code=status.HTTP_201_CREATED, )
async def bookmark_post(
        post_id: int,
        post: PublishedPostDep,
        current_user: CurrentUserDep,
        service: PostServiceDep
):
    await service.add_bookmark(post, current_user)


@router.delete(
    "/{post_id}/bookmark",
    status_code=status.HTTP_204_NO_CONTENT
)
async def unbookmark_post(
        post_id: int,
        post: PublishedPostDep,
        current_user: CurrentUserDep,
        service: PostServiceDep
):
    await service.remove_bookmark(post, current_user)
