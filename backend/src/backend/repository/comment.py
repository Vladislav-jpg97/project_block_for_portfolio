from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.models import Comment
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    RetrieveRepositoryMixin,
    UpdateRepositoryMixin,
    DeleteRepositoryMixin
)

class CommentRepository(
    BaseRepository[Comment],
    AddRepositoryMixin[Comment],
    RetrieveRepositoryMixin[Comment],
    UpdateRepositoryMixin[Comment],
    DeleteRepositoryMixin[Comment],
):
    model = Comment
    base_query = select(Comment)

    async def get_by_post(self, post_id: int) -> list[Comment]:
        stmt = self.base_query.where(Comment.post_id == post_id).options(
            selectinload(Comment.autor)
        ).order_by(Comment.created_at.asc())
        result = await self.session.execute(stmt)
        return result.scalars().all()

