from sqlalchemy import select
from backend.models import Category
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    RetrieveRepositoryMixin,
    UpdateRepositoryMixin,
    DeleteRepositoryMixin,
    ListRepositoryMixin
)


class CategoryRepository(
    BaseRepository[Category],
    AddRepositoryMixin[Category],
    RetrieveRepositoryMixin[Category],
    UpdateRepositoryMixin[Category],
    DeleteRepositoryMixin[Category],
    ListRepositoryMixin[Category],
):
    model = Category
    base_query = select(Category)

    async def get_by_slug(
            self,
            slug: str
    ) -> Category | None:
        stmt = self.base_query.where(Category.slug == slug)
        result = await self.session.execute(stmt)
        category = result.scalar_one_or_none()
        return category

