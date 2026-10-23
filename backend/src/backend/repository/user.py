from sqlalchemy import select

from backend.models import User
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    UpdateRepositoryMixin,
    DeleteRepositoryMixin,
    ListRepositoryMixin,
    RetrieveRepositoryMixin
)


class UserRepository(
    BaseRepository[User],
    AddRepositoryMixin[User],
    UpdateRepositoryMixin[User],
    RetrieveRepositoryMixin[User],
    DeleteRepositoryMixin[User],
    ListRepositoryMixin[User],
):
    model = User
    base_query = select(User)

    async def get_by_username(
            self,
            username: str,
    ) -> User | None:
        stmt = self.base_query.where(User.username == username)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user

    async def get_by_email(
            self,
            email: str,
    ) -> User | None:
        stmt = self.base_model.where(User.email == email)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()
        return user
