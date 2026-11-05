from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from starlette import status

from backend.dependencies.auth import CurrentUserDep
from backend.dependencies.user import UserServiceDep
from backend.schemas.pagination import Page, PaginationParams
from backend.schemas.post import PostRead, PostBrief
from backend.schemas.user import UserBrief, UserRead, UserFilter, UserUpdate
from backend.services.avatar import MAX_AVATAR_SIZE_BYTES

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


@router.patch("/me", response_model=UserRead)
async def update_me(
        body: UserUpdate,
        current_user: CurrentUserDep,
        service: UserServiceDep,
):
    return await service.update_me(
        user=current_user,
        body=body
    )


@router.post("/me/avatar", response_model=UserRead)
async def upload_my_avatar(
        current_user: CurrentUserDep,
        service: UserServiceDep,
        file: UploadFile = File(...),
):
    content = bytearray()
    try:
        while chunk := await file.read(1024 * 1024):
            content.extend(chunk)
            if len(content) > MAX_AVATAR_SIZE_BYTES:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail="Максимальный размер аватара — 5 МБ.",
                )
    finally:
        await file.close()
    return await service.upload_avatar(current_user, bytes(content))


@router.delete("/me/avatar", response_model=UserRead)
async def delete_my_avatar(
        current_user: CurrentUserDep,
        service: UserServiceDep,
):
    return await service.remove_avatar(current_user)


@router.get(
    "/{user_id}",
    # FIXED: Публичный профиль использует схему без приватного email.
    response_model=UserBrief,
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
