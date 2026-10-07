from fastapi import APIRouter
from starlette import status

from backend.schemas.auth import UserLogin, ChangePassword, Token, RefreshToken
from backend.schemas.user import UserCreate, UserUpdate, UserRead

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
        body: UserCreate,
):
    pass


@router.post(
    "/login",
    response_model=Token,
)
async def login_user(
        body: UserLogin,
):
    pass


@router.post(
    "/refresh",
    response_model=Token,
)
async def refresh_token(
        body: RefreshToken,
):
    pass


@router.get("/me")
async def get_me():
    pass


@router.patch("/me")
async def update_me(
        body: UserUpdate
):
    pass


@router.post("/change-password")
async def change_password(
        body: ChangePassword,
):
    pass
