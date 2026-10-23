from typing import Annotated

from fastapi import Depends, HTTPException
from starlette import status

from backend.core.security import decode_token
from backend.dependencies.database import SessionDep
from backend.models import User
from backend.repository.user import UserRepository
from backend.services.auth import AuthService
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

oauth2_scheme = HTTPBearer()


async def get_user_repo(
        session: SessionDep
) -> UserRepository:
    return UserRepository(session)


UserRepoDep = Annotated[
    UserRepository,
    Depends(get_user_repo),
]


async def get_auth_service(
        session: SessionDep,
        user_repo: UserRepoDep
) -> AuthService:
    return AuthService(
        session=session,
        user_repo=user_repo
    )


AuthServiceDep = Annotated[
    AuthService,
    Depends(get_auth_service),
]


# TODO : аутентификация пользователя по токену , Защита эндпоинтов

async def get_current_user(
        user_repo: UserRepoDep,
        credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
) -> User:
    token = credentials.credentials

    user_id = decode_token(token)

    user = await user_repo.get_by_id(user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не активен"
        )

    return user


CurrentUserDep = Annotated[
    User,
    Depends(get_current_user),
]


async def verify_superuser(
        current_user: CurrentUserDep,
) -> None:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У Вас нет прав!"
        )

