from datetime import datetime, date

from pydantic import BaseModel, Field, field_validator, ConfigDict
from dataclasses import dataclass
from fastapi import Query

from backend.schemas.tag import TagRead
from backend.schemas.user import UserBrief


@dataclass(frozen=True)
class PostFilters:
    q: str | None = Query(
        default=None,
    )
    category_id: int | None = Query(
        default=None,
        ge=1,
    )
    author_id: int | None = Query(
        default=None,
        ge=1,
    )

    date_from : date | None = Query(
        default=None,
    )
    date_to: date | None = Query(
        default=None,
    )


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
    def no_leading_trailing_spaces(cls, v: str):
        return v.strip()


class PostCreate(PostBase):
    content: str = Field(
        min_length=100,
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


class PostUpdate(PostBase):
    content: str = Field(
        min_length=100,
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


class PostBrief(PostBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
    id: int
    is_published: bool
    views_count: int = 0
    votes_count: int = 0
    created_at: datetime


class PostRead(PostBrief):
    content: str
    author: UserBrief
    tags: list[TagRead]
