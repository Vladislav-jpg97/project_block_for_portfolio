from fastapi import APIRouter
from starlette import status

from backend.dependencies.category import CategoryServiceDep
from backend.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(
    prefix="/category",
    tags=["category"],
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
        body: CategoryCreate,
        service: CategoryServiceDep
):
    category = await service.create(body)
    return category


@router.get("/")
async def list_categories(service: CategoryServiceDep):
    categories = await service.get_all()
    return categories


@router.get(
    "/{category_slug}",
    status_code=status.HTTP_200_OK,
    response_model=CategoryRead
)
async def get_category(
        category_slug: str,
        service: CategoryServiceDep
):
    category = await service.get_or_404(category_slug)
    return category


@router.put(
    "/{category_id}",
    status_code=status.HTTP_200_OK,

)
async def update_category(
        category_id: int,
        body: CategoryUpdate,
        service: CategoryServiceDep
):
    await service.update(category_id, body)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
        category_id: int,
        service: CategoryServiceDep
):
    await service.delete(category_id)
