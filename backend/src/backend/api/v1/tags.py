from fastapi import APIRouter, Depends
from starlette import status

from backend.dependencies.auth import verify_superuser
from backend.dependencies.tag import TagServiceDep
from backend.schemas.pagination import Page, PaginationParams
from backend.schemas.tag import TagCreate, TagRead

router = APIRouter(
    prefix="/tags",
    tags=["tags"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=TagRead,
    dependencies=[Depends(verify_superuser)],
)
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
    tags = await service.get_all(
        pagination=pagination,
    )
    return tags


@router.get(
    "/{tag_id}",
    response_model=TagRead,
)
async def get_tag(
        tag_id: int,
        service: TagServiceDep,
):
    tag = await service.get_or_404(tag_id)
    return tag


@router.delete(
    "/{tag_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_superuser)],
)
async def delete_tag(
        tag_id: int,
        service: TagServiceDep,
):
    await service.delete(tag_id)