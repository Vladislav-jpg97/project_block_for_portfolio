from fastapi import HTTPException
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.models import Category
from backend.repository.category import CategoryRepository
from backend.schemas.category import CategoryCreate, CategoryUpdate
from backend.utils.slug import slug_generate


class CategoryService:
    def __init__(
            self,
            session: AsyncSession,
            category_repo: CategoryRepository
    ):
        self.session = session
        self.category_repo = category_repo

    async def get_all(
            self,
    ) -> list[Category]:
        categories = await self.category_repo.get_all()
        return categories

    async def get_or_404(
            self,
            slug: str
    ) -> Category:
        category = await self.category_repo.get_by_slug(slug)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категории с таким слагом {slug} не существует"
            )

        return category

    async def create(
            self,
            body: CategoryCreate
    ) -> Category:
        slug = slug_generate.generate(body.name)
        existing = await self.category_repo.get_by_slug(slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Категория с название слага : {slug} уже существует"
            )
        category = Category(
            name=body.name,
            slug=slug,
            description=body.description,
        )
        await self.session.commit()
        return category

    async def update(
            self,
            category_id: int,
            body: CategoryUpdate
    ) -> None:
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категории с ID {category_id} не существует"
            )
        category.name = body.name
        category.description = body.description

        await self.category_repo.update(
            category
        )
        await self.session.commit()

    async def delete(
            self,
            category_id: int
    ):
        category = await self.category_repo.get_by_id(category_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Категории с ID {category_id} не существует"
            )
        await self.category_repo.delete(category)
        await self.session.commit()
