from enum import StrEnum

from fastapi import APIRouter, Depends

from backend.dependencies.auth import OptionalCurrentUserDep
from backend.dependencies.post import PostServiceDep
from backend.schemas.pagination import Page, PaginationParams
from backend.schemas.post import PostBrief, PostFilters

router = APIRouter(
    prefix="/feed",
    tags=["Feed"],
)


class FeedType(StrEnum):
    new = "new"
    top = "top"
    hot = "hot"


@router.get("/", response_model=Page[PostBrief])
async def get_feed(
        service: PostServiceDep,
        current_user: OptionalCurrentUserDep,
        feed_type: FeedType = FeedType.new,
        pagination: PaginationParams = Depends(),
):
    # ADDED: Существующая лента использует реальную выдачу публикаций и пагинацию.
    filters = PostFilters(sort=feed_type.value)
    return await service.get_all(
        filters,
        pagination,
        user_id=current_user.id if current_user else None,
    )