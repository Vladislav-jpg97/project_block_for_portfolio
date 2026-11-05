from typing import Annotated

from fastapi import Depends

from backend.dependencies.database import SessionDep
from backend.repository.bookmark import BookMarkRepository


async def get_bookmark_repo(
        session: SessionDep
):
    return BookMarkRepository(session)


BookmarkRepoDep = Annotated[
    BookMarkRepository,
    Depends(get_bookmark_repo),
]
