from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import Category


class CategoryRepository:
    def __init__(
            self,
            session: AsyncSession,
    ):
        self.session = session

    async def add(
            self,
            name: str,
            slug: str,
            description: str | None = None,
    ) -> Category:
        category = Category(
            name=name,
            slug=slug,
            description=description,
        )
        self.session.add(category)
        await self.session.flush()
        await self.session.refresh(category)
        return category

    async def get_by_id(
            self,
            category_id: int
    ) -> Category | None:
        stmt = select(Category).where(Category.id == category_id)
        result = await self.session.execute(stmt)
        category = result.scalar_one_or_none()
        return category

    async def get_by_slug(
            self,
            slug: str
    ) -> Category | None:
        stmt = select(Category).where(Category.slug == slug)
        result = await self.session.execute(stmt)
        category = result.scalar_one_or_none()
        return category

    async def get_all(
            self
    ) -> list[Category]:
        stmt = select(Category)
        result = await self.session.execute(stmt)
        categories = result.scalars().all()
        return categories

    async def update(
            self,
            category_id: int,
            name: str,
            description: str | None
    ):
        stmt = update(Category).where(Category.id == category_id).values(name=name, description=description)
        await self.session.execute(stmt)
        await self.session.flush()

    async def delete(
            self,
            category_id: int,
    ):
        stmt = delete(Category).where(Category.id == category_id)
        await self.session.execute(stmt)
        await self.session.flush()
