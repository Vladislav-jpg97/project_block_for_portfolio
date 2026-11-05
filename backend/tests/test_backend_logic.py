import json
import unittest
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi import HTTPException
from PIL import Image
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects import postgresql

from backend.core.cache import CacheService
from backend.models import Comment, Post
from backend.schemas.comment import CommentCreate, CommentResponse
from backend.schemas.auth import ChangePassword
from backend.schemas.pagination import Page, PaginationParams
from backend.schemas.post import PostBrief, PostCreate, PostFilters, PostUpdate
from backend.schemas.user import UserBrief
from backend.services.comment import CommentService
from backend.services.avatar import (
    AVATAR_URL_PREFIX,
    _delete_avatar,
    _store_avatar,
)
from backend.services.post import PostService
from backend.utils.comment_tree import build_comment_tree


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def get(self, key: str) -> str | None:
        return self.values.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        self.values[key] = value

    async def delete(self, *keys: str) -> None:
        for key in keys:
            self.values.pop(key, None)

    async def scan_iter(self, match: str, count: int):
        prefix = match.removesuffix("*")
        for key in tuple(self.values):
            if key.startswith(prefix):
                yield key


class BackendLogicTests(unittest.IsolatedAsyncioTestCase):
    async def test_avatar_upload_reencodes_image_and_remove_deletes_file(self) -> None:
        image_bytes = BytesIO()
        Image.new("RGB", (96, 64), color="teal").save(image_bytes, format="PNG")

        with TemporaryDirectory() as directory:
            storage_dir = Path(directory)
            avatar_url = _store_avatar(image_bytes.getvalue(), storage_dir)
            avatar_path = storage_dir / avatar_url.removeprefix(AVATAR_URL_PREFIX)

            self.assertTrue(avatar_path.is_file())
            with Image.open(avatar_path) as saved_image:
                self.assertEqual(saved_image.format, "WEBP")
                self.assertEqual(saved_image.size, (512, 512))

            _delete_avatar(avatar_url, storage_dir)
            self.assertFalse(avatar_path.exists())

    async def test_avatar_upload_rejects_non_image_files(self) -> None:
        with TemporaryDirectory() as directory:
            with self.assertRaises(HTTPException) as raised:
                _store_avatar(b"not an image", Path(directory))

        self.assertEqual(raised.exception.status_code, 400)

    async def test_post_deletion_cascades_dependent_records(self) -> None:
        for relationship_name in ("comments", "post_votes", "bookmarks"):
            relationship = Post.__mapper__.relationships[relationship_name]
            self.assertTrue(relationship.passive_deletes)
            self.assertTrue(relationship.cascade.delete_orphan)

        replies = Comment.__mapper__.relationships["replies"]
        self.assertTrue(replies.passive_deletes)
        self.assertTrue(replies.cascade.delete_orphan)

    async def test_cache_get_awaits_redis_and_decodes_json(self) -> None:
        redis = FakeRedis()
        redis.values["feed"] = json.dumps({"items": []})

        result = await CacheService(redis).get("feed")

        self.assertEqual(result, {"items": []})

    async def test_cache_encodes_models_and_deletes_matching_keys(self) -> None:
        redis = FakeRedis()
        cache = CacheService(redis)
        await cache.set("posts:list:1", {"items": [1]})
        await cache.set("users:list:1", {"items": [2]})

        await cache.delete_pattern("posts:list:*")

        self.assertIsNone(await cache.get("posts:list:1"))
        self.assertEqual(await cache.get("users:list:1"), {"items": [2]})

    async def test_post_brief_reads_model_view_count(self) -> None:
        post = self._post()

        result = PostBrief.model_validate(post)

        self.assertEqual(result.views_count, 17)
        self.assertEqual(result.content, "A story from the feed")

    async def test_post_page_round_trips_through_cache_shape(self) -> None:
        page = Page.create(
            items=[self._post()],
            total=1,
            params=PaginationParams(),
        )

        validated = Page[PostBrief].model_validate(page, from_attributes=True)
        cached = validated.model_dump(mode="json")
        restored = Page[PostBrief].model_validate(cached)

        self.assertEqual(restored.items[0].views_count, 17)

    @staticmethod
    def _post():
        return SimpleNamespace(
            id=3,
            slug="async-post",
            title="Async posts",
            content="A story from the feed",
            is_published=True,
            view_count=17,
            votes_count=2,
            created_at="2026-11-05T12:00:00",
            author=SimpleNamespace(id=1, username="developer", karma=4),
            category=None,
            tags=[],
        )

    async def test_comment_response_reads_nested_author(self) -> None:
        comment = SimpleNamespace(
            id=5,
            content="Useful explanation",
            post_id=3,
            parent_id=None,
            author=SimpleNamespace(id=1, username="developer"),
            created_at="2026-11-05T12:00:00",
            updated_at="2026-11-05T12:00:00",
            replies=[],
        )

        result = CommentResponse.model_validate(comment)

        self.assertEqual(result.author.username, "developer")

    async def test_comment_tree_initializes_replies_without_lazy_loading(self) -> None:
        parent = Comment(
            id=1,
            content="Первый комментарий",
            post_id=3,
            author_id=7,
            parent_id=None,
        )
        reply = Comment(
            id=2,
            content="Ответ",
            post_id=3,
            author_id=8,
            parent_id=1,
        )

        roots = build_comment_tree([parent, reply])

        self.assertEqual(roots, [parent])
        self.assertEqual(parent.replies, [reply])
        self.assertEqual(reply.replies, [])

    async def test_public_post_filter_excludes_drafts(self) -> None:
        statement = PostFilters().filter(select(Post))
        sql = str(statement.compile(dialect=postgresql.dialect()))

        self.assertIn("is_published IS true", sql)

    async def test_change_password_rejects_reusing_old_password(self) -> None:
        with self.assertRaises(ValidationError):
            ChangePassword(
                old_password="OldPassword1",
                new_password="OldPassword1",
            )

    async def test_post_update_accepts_partial_fields(self) -> None:
        update = PostUpdate(title=None, content="Короткий текст")

        self.assertEqual(update.model_dump(exclude_unset=True), {
            "title": None,
            "content": "Короткий текст",
        })

    async def test_post_creation_accepts_short_content_and_rejects_blank(self) -> None:
        post = PostCreate(
            title="Короткий пост",
            content="  Короткий текст  ",
            category_id=1,
        )

        self.assertEqual(post.content, "Короткий текст")
        with self.assertRaises(ValidationError):
            PostCreate(
                title="Короткий пост",
                content="   ",
                category_id=1,
            )

    async def test_public_user_schema_does_not_expose_email(self) -> None:
        self.assertNotIn("email", UserBrief.model_fields)

    async def test_draft_post_is_not_available_by_public_id(self) -> None:
        service = PostService.__new__(PostService)
        service.post_repo = SimpleNamespace(
            get_by_id=AsyncMock(
                return_value=SimpleNamespace(id=4, is_published=False)
            )
        )

        with self.assertRaises(HTTPException) as raised:
            await service.get_published_by_id_or_404(4)

        self.assertEqual(raised.exception.status_code, 404)

    async def test_unvote_removes_existing_vote_and_adjusts_counters(self) -> None:
        vote = SimpleNamespace(id=9)
        author = SimpleNamespace(id=8, karma=3)
        post = SimpleNamespace(id=4, author_id=8, votes_count=2)
        service = PostService.__new__(PostService)
        service.post_vote_repo = SimpleNamespace(
            get_vot_by_post_user=AsyncMock(return_value=vote),
            delete=AsyncMock(),
        )
        service.user_repo = SimpleNamespace(
            get_by_id=AsyncMock(return_value=author),
            update=AsyncMock(),
        )
        service.post_repo = SimpleNamespace(update=AsyncMock())
        service.session = SimpleNamespace(commit=AsyncMock())
        service.cache_service = SimpleNamespace(delete_pattern=AsyncMock())

        await service.unvote_post(post, SimpleNamespace(id=5))

        self.assertEqual(post.votes_count, 1)
        self.assertEqual(author.karma, 2)
        service.post_vote_repo.delete.assert_awaited_once_with(vote)

    async def test_authenticated_feed_populates_vote_and_bookmark_state(self) -> None:
        posts = [SimpleNamespace(id=1), SimpleNamespace(id=2)]
        service = PostService.__new__(PostService)
        service.post_repo = SimpleNamespace(
            get_user_interactions=AsyncMock(return_value=({1}, {2}))
        )

        await service._set_user_interactions(posts, user_id=7)

        self.assertEqual(posts[0].user_vote, 1)
        self.assertFalse(posts[0].is_bookmarked)
        self.assertIsNone(posts[1].user_vote)
        self.assertTrue(posts[1].is_bookmarked)

    async def test_comment_reply_uses_parent_comment_id(self) -> None:
        class FakeSession:
            async def commit(self) -> None:
                return None

        class FakeCommentRepository:
            def __init__(self) -> None:
                self.comments = {
                    1: SimpleNamespace(id=1, post_id=7),
                }

            async def get_by_id(self, comment_id: int):
                return self.comments.get(comment_id)

            async def add(self, comment) -> None:
                comment.id = 2
                self.comments[2] = comment

        repository = FakeCommentRepository()
        service = CommentService(FakeSession(), repository)

        reply = await service.create(
            post_id=7,
            author_id=3,
            body=CommentCreate(content="Ответ", parent_id=1),
        )

        self.assertEqual(reply.parent_id, 1)


if __name__ == "__main__":
    unittest.main()
