from typing import Annotated

from fastapi import Depends

from backend.dependencies.database import SessionDep
from backend.repository.post import PostRepository
from backend.services.post import PostService


async def get_post_repo(
        session: SessionDep,
) -> PostRepository:
    return PostRepository(session)


PostRepoDep = Annotated[PostRepository, Depends(get_post_repo)]


async def get_post_service(
        session: SessionDep,
        post_repo: PostRepoDep
) -> PostService:
    return PostService(session, post_repo)


PostServiceDep = Annotated[PostService, Depends(get_post_service)]
