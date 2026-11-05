from sqlalchemy import select
from backend.models.vote import PostVote
from backend.repository.base import BaseRepository
from backend.repository.mixins import AddRepositoryMixin, DeleteRepositoryMixin


class PostVoteRepository(
    BaseRepository[PostVote],
    AddRepositoryMixin[PostVote],
    DeleteRepositoryMixin[PostVote],
):
    model = PostVote

    async def get_vot_by_post_user(
            self,
            post_id: int,
            user_id: int
    ) -> PostVote | None:
        stmt = select(
            PostVote
        ).where(
            PostVote.post_id == post_id,
            PostVote.user_id == user_id
        )
        result = await self.session.execute(stmt)
        post_vote = result.scalar_one_or_none()
        return post_vote
