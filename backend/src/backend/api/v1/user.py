from fastapi import APIRouter, Depends

from backend.dependencies.auth import CurrentUserDep, AuthServiceDep
from backend.dependencies.user import UserServiceDep
from backend.schemas.pagination import Page, PaginationParams
from backend.schemas.post import PostRead, PostBrief
from backend.schemas.user import UserBrief, UserRead, UserFilter, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/me/bookmarks",
    response_model=Page[PostBrief]
)
async def get_my_bookmarks(
        current_user: CurrentUserDep,
        service: UserServiceDep,
        pagination: PaginationParams = Depends(),
):
    posts = await service.get_bookmarked_posts(current_user,pagination)
    return posts


@router.get(
    "/",
    response_model=Page[UserBrief]
)
async def list_users(
        service: UserServiceDep,
        filters: UserFilter = Depends(),
        pagination: PaginationParams = Depends(),
):
    user = await service.list_users(
        filters=filters,
        pagination=pagination
    )
    return user


@router.get("/me", response_model=UserRead)
async def get_me(
        current_user: CurrentUserDep
):
    return current_user


@router.patch("/me", )
async def update_me(
        body: UserUpdate,
        current_user: CurrentUserDep,
        service: UserServiceDep,
):
    await service.update_me(
        user=current_user,
        body=body
    )


@router.get(
    "/{user_id}",
    response_model=UserRead
)
async def get_user(
        user_id: int,
        service: UserServiceDep,
):
    user = await service.get_user(user_id)
    return user


@router.get(
    "/{user_id}/posts",
    response_model=Page[PostRead]
)
async def list_user_posts(
        user_id: int,
        service: UserServiceDep,
        pagination: PaginationParams = Depends(),
):
    posts = await service.get_user_posts(pagination=pagination, user_id=user_id)
    return posts
