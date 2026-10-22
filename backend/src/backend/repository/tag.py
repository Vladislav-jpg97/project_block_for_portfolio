from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Tag, post_tags
from backend.schemas.pagination import PaginationParams, Page


class TagRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
            self,
            pagination: PaginationParams
    ):
        stmt = select(Tag).order_by(Tag.name)

        count_stmt = select(
            func.count()
        ).select_from(stmt.subquery())

        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.offset(pagination.offset).limit(pagination.limit)

        result = await self.session.execute(stmt)
        tags = result.scalars().all()
        return Page.create(
            items=tags,
            total=total,
            params=pagination,
        )

    async def get_by_id(self, tag_id: int) -> Tag | None:
        stmt = select(Tag).where(Tag.id == tag_id)
        result = await self.session.execute(stmt)
        tag = result.scalar_one_or_none()
        return tag

    async def get_by_slug(self, slug: str) -> Tag | None:
        stmt = select(Tag).where(Tag.slug == slug)
        result = await self.session.execute(stmt)
        tag = result.scalar_one_or_none()
        return tag

    async def add(self, tag: Tag) -> Tag:
        self.session.add(tag)
        await self.session.flush()
        await self.session.refresh(tag)
        return tag

    async def delete(self, tag: Tag) -> None:
        await self.session.delete(tag)
        await self.session.flush()

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
