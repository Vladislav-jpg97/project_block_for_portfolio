from typing import Generic
from uuid import UUID

from sqlalchemy import Select, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from backend.repository.base import M
from backend.schemas.filters import BaseFilter
from backend.schemas.pagination import PaginationParams, Page


class AddRepositoryMixin(Generic[M]):
    model: M
    session: AsyncSession

    async def add(self, obj: M) -> M:
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj


class UpdateRepositoryMixin(Generic[M]):
    model: M
    session: AsyncSession

    async def update(self, obj: M) -> None:
        await self.session.merge(obj)
        await self.session.flush()


class DeleteRepositoryMixin(Generic[M]):
    model: M
    session: AsyncSession

    async def delete(self, obj: M) -> None:
        await self.session.delete(obj)
        await self.session.flush()


class RetrieveRepositoryMixin(Generic[M]):
    model: M
    session: AsyncSession
    base_query: Select

    async def get_by_id(self, obj_id: int | UUID) -> M | None:
        stmt = self.base_query.where(self.model.id == obj_id)
        result = await self.session.execute(stmt)
        obj = result.scalar_one_or_none()
        return obj


class ListRepositoryMixin(Generic[M]):
    model: M
    session: AsyncSession
    base_query: Select

    async def get_all(
            self,
            filters: BaseFilter | None = None,
            pagination: PaginationParams | None = None,
    ):
        stmt = self.base_query

        if filters:
            stmt = filters.filter(stmt)

        if pagination:
            # Пагинация
            count_stmt = select(
                func.count()
            ).select_from(stmt.subquery())
            total = (await self.session.execute(count_stmt)).scalar_one()

            stmt = stmt.offset(pagination.offset).limit(pagination.limit)

            result = await self.session.execute(stmt)
            objs = result.scalars().all()

            return Page.create(
                items=objs,
                total=total,
                params=pagination
            )

        result = await self.session.execute(stmt)
        objs = result.scalars().all()
        return objs
