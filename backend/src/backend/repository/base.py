from typing import TypeVar, Generic, Type

from sqlalchemy.ext.asyncio import AsyncSession

M = TypeVar("M")

class BaseRepository(Generic[M]):

    model: Type[M]

    def __init__(self, session: AsyncSession):
        self.session = session
