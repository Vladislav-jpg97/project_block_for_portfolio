from ast import stmt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.models import Comment, Post


class CommentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, comment_id: int) -> Comment | None:
        stmt = select(Comment).where(Comment.id == comment_id).options(
            selectinload(Comment.autor)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add(self, comment: Comment) -> Comment:
        self.session.add(comment)
        await self.session.flush()
        await self.session.refresh(comment)
        return comment

    async def delete(self, comment: Comment) -> None:
        await self.session.delete(comment)
        await self.session.flush()

    async def get_by_post(self, post_id: int) -> list[Comment]:
        stmt = select(Comment).where(Comment.post_id == post_id).options(
            selectinload(Comment.autor)
        ).order_by(Comment.created_at.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def update(self, comment: Comment) -> None:
        await self.session.merge(comment)
        await self.session.flush()
