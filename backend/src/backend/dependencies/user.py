from typing import Annotated

from fastapi import Depends

from backend.dependencies.auth import UserRepoDep
from backend.dependencies.database import SessionDep
from backend.dependencies.post import PostRepoDep
from backend.services.user import UserService


async def get_user_service(
        session: SessionDep,
        user_repo: UserRepoDep,
        post_repo: PostRepoDep
) -> UserService:
    return UserService(
        session=session,
        user_repo=user_repo,
        post_repo=post_repo
    )


UserServiceDep = Annotated[
    UserService,
    Depends(get_user_service)
]
