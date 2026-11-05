from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from backend.dependencies.cache import CacheServiceDep
from backend.models import Category, Post, User, Bookmark
from backend.models.vote import PostVote
from backend.repository.bookmark import BookMarkRepository
from backend.repository.post import PostRepository
from backend.repository.post_vote import PostVoteRepository
from backend.repository.tag import TagRepository
from backend.repository.user import UserRepository
from backend.schemas.pagination import Page, PaginationParams
from backend.schemas.post import PostBrief, PostCreate, PostUpdate, PostFilters
from backend.utils.slug import slug_generate


class PostService:
    def __init__(
            self,
            session: AsyncSession,
            post_repo: PostRepository,
            tag_repo: TagRepository,
            post_vote_repo: PostVoteRepository,
            user_repo: UserRepository,
            bookmark_repo: BookMarkRepository,
            cache_service: CacheServiceDep,
    ):
        self.session = session
        self.post_repo = post_repo
        self.tag_repo = tag_repo
        self.post_vote_repo = post_vote_repo
        self.user_repo = user_repo
        self.bookmark_repo = bookmark_repo
        self.cache_service = cache_service

    async def _make_unique_slug(
            self,
            base_slug: str,
            exclude_post_id: int | None = None,
    ) -> str:
        slug = base_slug
        count = 1
        while (post := await self.post_repo.get_by_slug(slug)) is not None:
            if post.id == exclude_post_id:
                return slug
            slug = f"{base_slug}-{count}"
            count += 1
        return slug

    async def create(self, body: PostCreate, author_id: int) -> Post:
        base_slug = slug_generate.generate(body.title)
        slug = await self._make_unique_slug(base_slug)
        if await self.session.get(Category, body.category_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена",
            )
        tags = await self.post_repo.get_tags_by_ids(body.tags_ids)
        if len(tags) != len(set(body.tags_ids)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Один или несколько тегов не найдены",
            )
        post = Post(
            slug=slug,
            title=body.title,
            content=body.content,
            author_id=author_id,
            category_id=body.category_id,
            is_published=body.is_published,
            tags=tags
        )
        post = await self.post_repo.add(post)

        for tag in tags:
            await self.tag_repo.sync_posts_count(tag.id)

        # FIXED: Инвалидируем кеш до commit, чтобы сбой Redis не скрывал уже сохранённую запись за HTTP 500.
        await self.cache_service.delete_pattern("posts:list:*")
        await self.session.commit()
        created_post = await self.post_repo.get_by_id(post.id)
        if created_post is None:
            raise RuntimeError("Created post could not be reloaded")
        return created_post

    async def update(
            self,
            post_id: int,
            body: PostUpdate,
            current_user_id: int

    ) -> Post:
        post = await self.get_or_404(post_id)
        if post.author_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы можете изменять только свои посты")

        update_data = body.model_dump(exclude_unset=True)

        if update_data.get("title"):
            base_slug = slug_generate.generate(update_data["title"])
            update_data["slug"] = await self._make_unique_slug(
                base_slug,
                exclude_post_id=post.id,
            )

        if (
            update_data.get("category_id") is not None
            and await self.session.get(Category, update_data["category_id"]) is None
        ):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Категория не найдена",
            )

        previous_tag_ids = {tag.id for tag in post.tags}
        tags_ids = update_data.pop("tags_ids", None)
        if tags_ids is not None:
            tags = await self.post_repo.get_tags_by_ids(tags_ids)
            if len(tags) != len(set(tags_ids)):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Один или несколько тегов не найдены",
                )
            post.tags = tags

        for field, value in update_data.items():
            if value is not None:
                setattr(post, field, value)
        await self.post_repo.update(post)
        for tag_id in previous_tag_ids | {tag.id for tag in post.tags}:
            await self.tag_repo.sync_posts_count(tag_id)
        await self.cache_service.delete_pattern("posts:list:*")
        await self.session.commit()

        updated_post = await self.post_repo.get_by_id(post.id)
        if updated_post is None:
            raise RuntimeError("Updated post could not be reloaded")
        return updated_post

    async def get_or_404(
            self,
            post_id: int
    ) -> Post:

        post = await self.post_repo.get_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пост не найден"
            )

        return post

    async def get_published_by_id_or_404(self, post_id: int) -> Post:
        post = await self.get_or_404(post_id)
        if not post.is_published:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пост не найден",
            )
        return post

    async def delete(self, post_id: int, current_user_id) -> None:

        post = await self.get_or_404(post_id)
        if post.author_id != current_user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Вы можете удалять только свои посты")
        tag_ids = [tag.id for tag in post.tags]
        await self.post_repo.delete(post)
        for tag_id in tag_ids:
            await self.tag_repo.sync_posts_count(tag_id)
        await self.cache_service.delete_pattern("posts:list:*")
        await self.session.commit()

    async def view_or_404(
            self,
            slug: str,
            user_id: int | None = None,
    ) -> Post:
        post = await self.post_repo.get_published_by_slug(slug)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пост не найден"
            )
        await self.post_repo.increment_views(post)
        await self.cache_service.delete_pattern("posts:list:*")
        await self.session.commit()
        if user_id is not None:
            await self._set_user_interactions([post], user_id)
        return post

    def _post_list_key(
            self,
            filters: PostFilters,
            pagination: PaginationParams
    ) -> str:
        return (
            f"posts:list:"
            f"schema=v2:"
            f"page={pagination.page}:"
            f"size={pagination.size}:"
            f"q={filters.q}:"
            f"category_id={filters.category_id}:"
            f"author_id={filters.author_id}:"
            f"sort={filters.sort}:"
            f"date_from={filters.date_from}:"
            f"date_to={filters.date_to}"
        )

    async def get_all(
            self,
            filters: PostFilters,
            pagination: PaginationParams,
            user_id: int | None = None,
    ) -> Page[PostBrief]:
        cache_key = self._post_list_key(filters, pagination)
        cached_posts = await self.cache_service.get(cache_key)
        if cached_posts is not None:
            page = Page[PostBrief].model_validate(cached_posts)
        else:
            posts = await self.post_repo.get_all(filters, pagination)
            page = Page[PostBrief].model_validate(posts, from_attributes=True)
            await self.cache_service.set(cache_key, page.model_dump(mode="json"))
        # IMPROVED: Персональные поля накладываются после кеша, поэтому кеш не смешивает состояния пользователей.
        if user_id is not None:
            await self._set_user_interactions(page.items, user_id)
        return page

    async def _set_user_interactions(
            self,
            posts: list[Post] | list[PostBrief],
            user_id: int,
    ) -> None:
        voted_ids, bookmarked_ids = await self.post_repo.get_user_interactions(
            user_id,
            [post.id for post in posts],
        )
        for post in posts:
            post.user_vote = 1 if post.id in voted_ids else None
            post.is_bookmarked = post.id in bookmarked_ids

    async def publish(self, current_user_id: int, post: Post):
        if post.author_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете публиковать только свои посты"
            )
        post.is_published = True
        await self.post_repo.update(post)
        await self.cache_service.delete_pattern("posts:list:*")
        await self.session.commit()

    async def vote_post(
            self,
            post: Post,
            user: User
    ):
        post_vote = await self.post_vote_repo.get_vot_by_post_user(post.id, user.id)

        if post_vote:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы уже голосовали"
            )

        post_vote = PostVote(
            post_id=post.id,
            user_id=user.id
        )

        author = await self.user_repo.get_by_id(post.author_id)
        if author is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Автор публикации не найден",
            )
        author.karma += 1
        post.votes_count += 1

        await self.post_vote_repo.add(post_vote)
        await self.user_repo.update(author)
        await self.post_repo.update(post)
        await self.cache_service.delete_pattern("posts:list:*")
        await self.session.commit()

    async def unvote_post(
            self,
            post: Post,
            user: User
    ):
        post_vote = await self.post_vote_repo.get_vot_by_post_user(post.id, user.id)

        if not post_vote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Голос не найден",
            )

        author = await self.user_repo.get_by_id(post.author_id)
        if author is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Автор публикации не найден",
            )
        author.karma = max(0, author.karma - 1)
        post.votes_count = max(0, post.votes_count - 1)

        await self.post_vote_repo.delete(post_vote)
        await self.user_repo.update(author)
        await self.post_repo.update(post)
        await self.cache_service.delete_pattern("posts:list:*")
        await self.session.commit()

    async def add_bookmark(
            self,
            post: Post,
            user: User
    ):
        bookmark = await self.bookmark_repo.get_bookmark_by_post_user(post.id, user.id)

        if bookmark:
            return
        bookmark = Bookmark(
            post_id=post.id,
            user_id=user.id
        )

        await self.bookmark_repo.add(bookmark)
        await self.session.commit()

    async def remove_bookmark(self, post: Post, user: User):
        bookmark = await self.bookmark_repo.get_bookmark_by_post_user(post.id, user.id)
        if not bookmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Избранное не найдено"
            )
        await self.bookmark_repo.delete(bookmark)
        await self.session.commit()
