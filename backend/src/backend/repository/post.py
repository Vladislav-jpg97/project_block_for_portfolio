from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models import Post, Tag


class PostRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _base_query(self):
        return select(Post).options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags)
        )

    async def add(self, post: Post):
        self.session.add(post)
        await self.session.flush()
        await self.session.refresh(post)
        return post

    async def get_by_id(self, post_id: int) -> Post | None:
        stmt = self._base_query().where(Post.id == post_id)
        result = await self.session.execute(stmt)
        post = result.scalar_one_or_none()
        return post

    async def get_by_slug(self, slug: str) -> Post | None:
        stmt = self._base_query().where(Post.slug == slug)
        result = await self.session.execute(stmt)
        post = result.scalar_one_or_none()
        return post

    async def get_all(self):
        stmt = self._base_query()
        result = await self.session.execute(stmt)
        post = result.scalars().all()
        return post

    async def delete(self, post: Post):
        await self.session.delete(post)
        await self.session.flush()
        await self.session.refresh(post)

    async def get_tags_by_ids(self, tag_ids: list[int]) -> list[Tag]:
        if not tag_ids:
            return []
        stmt = select(Tag).where(Tag.id.in_(tag_ids))
        result = await self.session.execute(stmt)
        tags = result.scalars.all()
        return tags

    async def update(self, post: Post) -> None:
        await self.session.merge(post)
        await self.session.flush()
        await self.session.refresh(post)

    async def increment_views(self,post: Post) -> None:
        post.votes_count += 1
        await self.session.flush()
