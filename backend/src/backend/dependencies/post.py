from typing import Annotated

from fastapi import Depends
from sqlalchemy.util import await_

from backend.dependencies.database import SessionDep
from backend.dependencies.tag import TagRepoDep
from backend.models import Post
from backend.repository.post import PostRepository
from backend.services.post import PostService


async def get_post_repo(
        session: SessionDep,
) -> PostRepository:
    return PostRepository(session)


PostRepoDep = Annotated[PostRepository, Depends(get_post_repo)]


async def get_post_service(
        session: SessionDep,
        post_repo: PostRepoDep,
        tag_repo: TagRepoDep
) -> PostService:
    return PostService(session, post_repo, tag_repo)


PostServiceDep = Annotated[PostService, Depends(get_post_service)]


async def get_current_post(
        post_id: int,
        service: PostServiceDep,
) -> Post:
    post = await service.get_or_404(post_id)
    return post


CurrentPostDep = Annotated[
    Post,
    Depends(get_current_post),
]
