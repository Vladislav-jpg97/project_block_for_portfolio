from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.models import Post, Tag
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    RetrieveRepositoryMixin,
    UpdateRepositoryMixin,
    DeleteRepositoryMixin,
    ListRepositoryMixin
)


class PostRepository(
    BaseRepository[Post],
    AddRepositoryMixin[Post],
    RetrieveRepositoryMixin[Post],
    UpdateRepositoryMixin[Post],
    DeleteRepositoryMixin[Post],
    ListRepositoryMixin[Post],
):
    base_query = select(Post).options(
        selectinload(Post.author),
        selectinload(Post.category),
        selectinload(Post.tags)
    )

    async def get_by_slug(self, slug: str) -> Post | None:
        stmt = self.base_query.where(Post.slug == slug)
        result = await self.session.execute(stmt)
        post = result.scalar_one_or_none()
        return post

    async def get_tags_by_ids(self, tag_ids: list[int]) -> list[Tag]:
        if not tag_ids:
            return []
        stmt = select(Tag).where(Tag.id.in_(tag_ids))
        result = await self.session.execute(stmt)
        tags = result.scalars.all()
        return tags

    async def increment_views(self, post: Post) -> None:
        post.votes_count += 1
        await self.session.flush()
