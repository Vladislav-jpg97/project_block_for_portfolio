from enum import StrEnum

from fastapi import APIRouter

router = APIRouter(
    prefix="/feed",
    tags=["Feed"],
)


class FeedType(StrEnum):
    new = "new"
    top = "top"
    hot = "hot"


@router.get("/")
async def root_feet(feed_type: FeedType):
   return {"feed_type": feed_type, "posts": []}