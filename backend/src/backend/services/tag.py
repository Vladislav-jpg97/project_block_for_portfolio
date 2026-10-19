from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.models import Tag
from backend.repository.tag import TagRepository
from backend.schemas.tag import TagCreate
from backend.utils.slug import slug_generate


class TagService:
    def __init__(self, session: AsyncSession, tag_repo: TagRepository):
        self.session = session
        self.tag_repo = tag_repo

    async def get_all(self) -> list[Tag]:
        tags = self.tag_repo.get_all()
        return tags

    async def get_or_404(self, tag_id: int) -> Tag:
        tag = await self.tag_repo.get_by_id(tag_id)
        if not tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Тег не найден")

        return tag

    async def create(self, body: TagCreate):
        slug = slug_generate.generate(body.name)
        existing = await self.tag_repo.get_by_slug(slug)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Такой тег уже существует"
            )
        tag = Tag(name=body.name, slug=slug)
        tag = await self.tag_repo.add(tag)
        await self.session.commit()
        return tag

    async def delete(self,tag_id: int) -> None:
        tag = await self.get_or_404(tag_id)
        await self.session.delete(tag)
        await self.session.commit()