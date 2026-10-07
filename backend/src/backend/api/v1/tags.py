from fastapi import APIRouter

from backend.schemas.pagination import PaginatedResponse
from backend.schemas.tag import TagCreate, TagRead

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
)


@router.post("/", )
async def create_tag(
        body: TagCreate,
):
    pass


@router.get(
    "/",
    response_model=PaginatedResponse[TagRead],
)
async def list_tags():
    pass


@router.get(
    "{tag_id}",
    response_model=TagRead,
)
async def get_tag(
        tag_id: int,
):
    pass
