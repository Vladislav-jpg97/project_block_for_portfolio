from fastapi import APIRouter, Depends

from backend.dependencies.tag import TagServiceDep
from backend.schemas.pagination import Page, PaginationParams
from backend.schemas.tag import TagCreate, TagRead

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
)


@router.post("/", )
async def create_tag(
        body: TagCreate,
        service: TagServiceDep
):
    tag = await service.create(body)
    return tag


@router.get(
    "/",
    response_model=Page[TagRead],
)
async def list_tags(
        service: TagServiceDep,
        pagination: PaginationParams = Depends(),
):
    tags = service.get_all(
        pagination=pagination,
    )
    return tags


@router.get(
    "{tag_id}",
    response_model=TagRead,
)
async def get_tag(
        tag_id: int,
        service: TagServiceDep,
):
    tag = await service.get_or_404(tag_id)
    return tag


@router.delete("/{tag_id}", )
async def delete_tag(
        tag_id: int,
        service: TagServiceDep,
):
    await service.delete(tag_id)
