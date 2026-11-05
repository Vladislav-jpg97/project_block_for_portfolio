from sqlalchemy import select

from backend.models import Bookmark
from backend.repository.base import BaseRepository
from backend.repository.mixins import AddRepositoryMixin, DeleteRepositoryMixin


class BookMarkRepository(
    BaseRepository[Bookmark],
    AddRepositoryMixin[Bookmark],
    DeleteRepositoryMixin[Bookmark],
):
    model = Bookmark

    async def get_bookmark_by_post_user(
            self,
            post_id: int,
            user_id: int
    ) -> Bookmark | None:
        stmt = select(
            Bookmark
        ).where(
            Bookmark.post_id == post_id,
            Bookmark.user_id == user_id
        )
        result = await self.session.execute(stmt)
        post_vote = result.scalar_one_or_none()
        return post_vote
