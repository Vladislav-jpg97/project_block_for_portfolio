from sqlalchemy import select, func
from backend.models import Tag, post_tags
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    RetrieveRepositoryMixin,
    UpdateRepositoryMixin,
    DeleteRepositoryMixin,
    ListRepositoryMixin
)

class TagRepository(
    BaseRepository[Tag],
    AddRepositoryMixin[Tag],
    RetrieveRepositoryMixin[Tag],
    UpdateRepositoryMixin[Tag],
    DeleteRepositoryMixin[Tag],
    ListRepositoryMixin[Tag],
):
    base_query = select(Tag)

    async def get_by_slug(self, slug: str) -> Tag | None:
        stmt = self.base_query.where(Tag.slug == slug)
        result = await self.session.execute(stmt)
        tag = result.scalar_one_or_none()
        return tag


    async def sync_posts_count(self, tag_id: int) -> None:
        result = await self.session.execute(
            select(func.count())
            .select_from(post_tags)
            .where(post_tags.c.id == tag_id)
        )
        count = result.scalar_one()
        tag = await self.get_by_id(tag_id)
        if tag:
            tag.posts_count = count
            await self.session.flush()
