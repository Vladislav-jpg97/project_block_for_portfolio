from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.models import User
from backend.repository.post import PostRepository
from backend.repository.user import UserRepository
from backend.schemas.pagination import PaginationParams
from backend.schemas.post import PostFilters
from backend.schemas.user import UserFilter, UserUpdate
from backend.services.avatar import delete_avatar, store_avatar


class UserService:
    def __init__(self, session: AsyncSession, user_repo: UserRepository, post_repo: PostRepository):
        self.session = session
        self.user_repo = user_repo
        self.post_repo = post_repo

    async def list_users(
            self,
            filters: UserFilter,
            pagination: PaginationParams,

    ):
        user = await self.user_repo.get_all(
            filters=filters,
            pagination=pagination
        )
        return user

    async def get_user(self, user_id):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
        return user

    async def get_user_posts(self, user_id: int, pagination: PaginationParams):
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        posts = await self.post_repo.get_all(filters=PostFilters(author_id=user_id), pagination=pagination)
        return posts

    async def update_me(
            self,
            user: User,
            body: UserUpdate,
    ) -> User:
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
        return user

    async def upload_avatar(self, user: User, content: bytes) -> User:
        new_url = await store_avatar(content)
        old_url = user.avatar_url
        user.avatar_url = new_url
        try:
            await self.user_repo.update(user)
            await self.session.commit()
        except Exception:
            await self.session.rollback()
            await delete_avatar(new_url)
            raise
        await delete_avatar(old_url)
        return user

    async def remove_avatar(self, user: User) -> User:
        old_url = user.avatar_url
        user.avatar_url = None
        await self.user_repo.update(user)
        await self.session.commit()
        await delete_avatar(old_url)
        return user

    async def get_bookmarked_posts(
            self,
            user: User,
            pagination: PaginationParams,
    ):
        posts = await self.post_repo.get_bookmarked_user_posts(user.id, pagination)
        voted_ids, _ = await self.post_repo.get_user_interactions(
            user.id,
            [post.id for post in posts.items],
        )
        for post in posts.items:
            post.is_bookmarked = True
            post.user_vote = 1 if post.id in voted_ids else None
        return posts
