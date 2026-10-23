from fastapi import APIRouter
from starlette import status

from backend.dependencies.auth import AuthServiceDep, CurrentUserDep
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
        service: AuthServiceDep
):
    user = await service.register(body=body)
    return user


@router.post(
    "/login",
    response_model=Token,
)
async def login_user(
        body: UserLogin,
        service: AuthServiceDep

):
    token = await service.login(body=body)
    return token


@router.post(
    "/refresh",
    response_model=Token,
)
async def refresh_token(
        body: RefreshToken,
        service: AuthServiceDep
):
    token = await service.refresh(body=body)
    return token


@router.get("/me", response_model=UserRead)
async def get_me(
        current_user: CurrentUserDep
):
    return current_user


@router.patch("/me", )
async def update_me(
        body: UserUpdate,
        current_user: CurrentUserDep,
        service: AuthServiceDep,
):
    await service.update_me(
        user=current_user,
        body=body
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
        body: ChangePassword,
        current_user: CurrentUserDep,
        service: AuthServiceDep
):
    await service.change_password(
        user=current_user,
        body=body
    )
