from datetime import datetime, date

from pydantic import BaseModel, Field, field_validator, ConfigDict, AliasChoices
from dataclasses import dataclass
from typing import Literal
from sqlalchemy import Select, or_

from backend.models import Post
from backend.schemas.filters import BaseFilter
from backend.schemas.tag import TagRead
from backend.schemas.user import UserBrief
from backend.schemas.category import CategoryRead


@dataclass(frozen=True)
class PostFilters(BaseFilter):
    q: str | None = None
    category_id: int | None = None
    author_id: int | None = None
    sort: Literal["new", "top", "hot"] = "new"

    date_from: date | None = None
    date_to: date | None = None

    def filter(self, stmt: Select) -> Select:
        # FIXED: Черновики больше не попадают в публичные ленты и поиск.
        stmt = stmt.where(Post.is_published.is_(True))

        if self.q:
            pattern = f"%{self.q}%"
            stmt = stmt.where(
                or_(
                    Post.title.ilike(pattern),
                    Post.content.ilike(pattern)
                ),
            )

        if self.category_id is not None:
            stmt = stmt.where(
                Post.category_id == self.category_id
            )

        if self.author_id is not None:
            stmt = stmt.where(
                Post.author_id == self.author_id
            )

        if self.date_from:
            stmt = stmt.where(
                Post.created_at >= datetime.combine(self.date_from, datetime.min.time())
            )
        if self.date_to:
            stmt = stmt.where(
                Post.created_at <= datetime.combine(self.date_to, datetime.max.time())
            )

        stmt = stmt.order_by(None)
        if self.sort == "top":
            stmt = stmt.order_by(Post.votes_count.desc(), Post.created_at.desc(), Post.id.desc())
        elif self.sort == "hot":
            stmt = stmt.order_by(
                (Post.votes_count * 2 + Post.view_count).desc(),
                Post.created_at.desc(),
                Post.id.desc(),
            )
        else:
            stmt = stmt.order_by(Post.created_at.desc(), Post.id.desc())

        return stmt


class PostBase(BaseModel):
    title: str = Field(
        min_length=5,
        max_length=200,
        description="Заголовок поста",
        examples=[
            "Как работает pydantic?"
        ]
    )

    @field_validator("title", mode='after')
    @classmethod
    def no_leading_trailing_spaces(cls, v: str | None) -> str | None:
        if v is None:
            return None
        value = v.strip()
        if not value:
            raise ValueError("Заголовок не должен быть пустым")
        return value


class PostCreate(PostBase):
    content: str = Field(
        min_length=1,
        description="Содержимое поста в формате Markdown"
    )
    tags_ids: list[int] = Field(
        default_factory=list,
        max_length=5,
        description="ID Тегов"
    )
    is_published: bool = Field(
        default=False,
    )
    category_id: int = Field(
        ge=1
    )

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str) -> str:
        content = value.strip()
        if not content:
            raise ValueError("Текст публикации не должен быть пустым")
        return content


class PostUpdate(PostBase):
    title: str | None = Field(default=None, min_length=5, max_length=200)
    content: str | None = Field(default=None, min_length=1)
    tags_ids: list[int] | None = Field(
        default=None,
        max_length=5,
        description="ID Тегов"
    )
    is_published: bool | None = None
    category_id: int | None = Field(
        default=None,
        ge=1
    )

    @field_validator("content")
    @classmethod
    def content_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None:
            return None
        content = value.strip()
        if not content:
            raise ValueError("Текст публикации не должен быть пустым")
        return content


class PostBrief(PostBase):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    id: int
    slug: str
    content: str
    is_published: bool
    views_count: int = Field(
        default=0,
        validation_alias=AliasChoices("view_count", "views_count"),
    )
    votes_count: int = 0
    created_at: datetime

    author: UserBrief
    category: CategoryRead | None = None
    tags: list[TagRead] = Field(default_factory=list)
    is_bookmarked: bool = False
    user_vote: int | None = None

class PostRead(PostBrief):
    content: str