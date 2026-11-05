from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload

from backend.models import Post, Tag, Bookmark
from backend.models.vote import PostVote
from backend.repository.base import BaseRepository
from backend.repository.mixins import (
    AddRepositoryMixin,
    RetrieveRepositoryMixin,
    UpdateRepositoryMixin,
    DeleteRepositoryMixin,
    ListRepositoryMixin
)
from backend.schemas.pagination import PaginationParams, Page


class PostRepository(
    BaseRepository[Post],
    AddRepositoryMixin[Post],
    RetrieveRepositoryMixin[Post],
    UpdateRepositoryMixin[Post],
    DeleteRepositoryMixin[Post],
    ListRepositoryMixin[Post],
):
    model = Post
    base_query = (
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.category),
            selectinload(Post.tags),
        )
        .order_by(Post.created_at.desc(), Post.id.desc())
    )

    async def get_by_slug(self, slug: str) -> Post | None:
        stmt = self.base_query.where(Post.slug == slug)
        result = await self.session.execute(stmt)
        post = result.scalar_one_or_none()
        return post

    async def get_published_by_slug(self, slug: str) -> Post | None:
        stmt = self.base_query.where(
            Post.slug == slug,
            Post.is_published.is_(True),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_tags_by_ids(self, tag_ids: list[int]) -> list[Tag]:
        if not tag_ids:
            return []
        stmt = select(Tag).where(Tag.id.in_(tag_ids))
        result = await self.session.execute(stmt)
        tags = result.scalars().all()
        return tags

    async def get_user_interactions(
            self,
            user_id: int,
            post_ids: list[int],
    ) -> tuple[set[int], set[int]]:
        # IMPROVED: Голоса и закладки загружаются пакетно, без запроса на каждый пост.
        if not post_ids:
            return set(), set()

        voted_post_ids = set((await self.session.scalars(
            select(PostVote.post_id).where(
                PostVote.user_id == user_id,
                PostVote.post_id.in_(post_ids),
            )
        )).all())
        bookmarked_post_ids = set((await self.session.scalars(
            select(Bookmark.post_id).where(
                Bookmark.user_id == user_id,
                Bookmark.post_id.in_(post_ids),
            )
        )).all())
        return voted_post_ids, bookmarked_post_ids

    async def increment_views(self, post: Post) -> None:
        await self.session.execute(
            update(Post)
            .where(Post.id == post.id)
            .values(view_count=Post.view_count + 1)
        )
        await self.session.refresh(post, attribute_names=["view_count"])

    async def get_bookmarked_user_posts(
            self,
            user_id : int,
            pagination: PaginationParams
    ):
        stmt = self.base_query.join(
            Post.bookmarks
        ).where(
            Bookmark.user_id == user_id,
            Post.is_published.is_(True),
        )
        count_stmt = select(
            func.count()
        ).select_from(stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = stmt.offset(pagination.offset).limit(pagination.limit)

        result = await self.session.execute(stmt)
        objs = result.scalars().all()

        return Page.create(
            items=objs,
            total=total,
            params=pagination
        )