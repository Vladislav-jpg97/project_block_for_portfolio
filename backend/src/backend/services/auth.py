from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.core.security import hash_password, verify_password, create_access_token, create_refresh_token, \
    decode_token
from backend.models import User
from backend.repository.user import UserRepository
from backend.schemas.auth import UserLogin, Token, RefreshToken, ChangePassword
from backend.schemas.user import UserCreate, UserUpdate


class AuthService:
    def __init__(
            self,
            session: AsyncSession,
            user_repo: UserRepository,
    ):
        self.session = session
        self.user_repo = user_repo

    async def register(
            self,
            body: UserCreate,
    ) -> User:
        exists_username = await self.user_repo.get_by_username(body.username)
        if exists_username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким именем уже существует.",
            )

        exists_email = await self.user_repo.get_by_email(body.email)
        if exists_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким эмаилом уже существует."
            )
        user = User(
            username=body.username,
            email=body.email,
            hashed_password=hash_password(body.password),
        )
        await self.user_repo.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def login(
            self,
            body: UserLogin,
    ) -> Token:
        user = await self.user_repo.get_by_username(body.username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не верное имя пользователя или пароль"
            )
        if not verify_password(body.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не верное имя пользователя или пароль"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Пользователь не активен"
            )
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return Token(access_token=access_token, refresh_token=refresh_token)

    async def refresh(
            self,
            body: RefreshToken,
    ) -> Token:
        user_id = decode_token(body.refresh_token, "refresh")

        user = await self.user_repo.get_by_id(user_id)

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

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return Token(access_token=access_token, refresh_token=refresh_token)

    async def change_password(
            self,
            user: User,
            body: ChangePassword,
    ) -> None:
        if not verify_password(body.old_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Не верное имя пользователя или пароль"
            )

        hashed_password = hash_password(body.new_password)
        user.hashed_password = hashed_password

        await self.user_repo.update(user)
        await self.session.commit()


    async def update_me(
            self,
            user: User,
            body: UserUpdate,
    ):
        exists_username = await self.user_repo.get_by_username(body.username)
        if exists_username and exists_username.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким именем уже существует.",
            )

        exists_email = await self.user_repo.get_by_email(body.email)
        if exists_email and exists_email.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Пользователь с таким эмаилом уже существует."
            )

        user.username = body.username
        user.email = body.email
        user.bio = body.bio
        await self.user_repo.update(user)
        await self.session.commit()