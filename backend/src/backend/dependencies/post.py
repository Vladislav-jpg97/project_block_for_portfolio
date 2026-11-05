from typing import Annotated

from fastapi import Depends

from backend.dependencies.auth import UserRepoDep
from backend.dependencies.bookmark import BookmarkRepoDep
from backend.dependencies.cache import CacheServiceDep
from backend.dependencies.database import SessionDep
from backend.dependencies.tag import TagRepoDep
from backend.models import Post
from backend.repository.post import PostRepository
from backend.repository.post_vote import PostVoteRepository
from backend.services.post import PostService


async def get_post_repo(
        session: SessionDep,
) -> PostRepository:
    return PostRepository(session)


PostRepoDep = Annotated[PostRepository, Depends(get_post_repo)]


async def get_post_vote_repo(
        session: SessionDep,
) -> PostVoteRepository:
    return PostVoteRepository(session)


PostVoteRepoDep = Annotated[
    PostVoteRepository,
    Depends(get_post_vote_repo),
]


async def get_post_service(
        session: SessionDep,
        post_repo: PostRepoDep,
        tag_repo: TagRepoDep,
        user_repo: UserRepoDep,
        post_vote_repo: PostVoteRepoDep,
        bookmark_repo: BookmarkRepoDep,
        cache_service: CacheServiceDep,
) -> PostService:
    return PostService(
        session=session,
        post_repo=post_repo,
        tag_repo=tag_repo,
        user_repo=user_repo,
        post_vote_repo=post_vote_repo,
        bookmark_repo=bookmark_repo,
        cache_service=cache_service,
    )


PostServiceDep = Annotated[PostService, Depends(get_post_service)]


async def get_current_post(
        post_id: int,
        service: PostServiceDep,
) -> Post:
    post = await service.get_or_404(post_id)
    return post


async def get_published_post(
        post_id: int,
        service: PostServiceDep,
) -> Post:
    return await service.get_published_by_id_or_404(post_id)


CurrentPostDep = Annotated[
    Post,
    Depends(get_current_post),
]

PublishedPostDep = Annotated[
    Post,
    Depends(get_published_post),
]
