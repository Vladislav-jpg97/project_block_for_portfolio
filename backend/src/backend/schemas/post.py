from pydantic import BaseModel, Field, field_validator, ConfigDict

from backend.schemas.auth import UserBrief


class PostCreate(BaseModel):
    title: str = Field(
        min_length=5,
        max_length=200,
        description="Заголовок поста",
        examples=[
            "Как работает pydantic?"
        ]
    )
    slug: str = Field(
        min_length=3,
        max_length=220,
        pattern=r"^[a-z0-9-]+$",
        description="URL-friendly идентификатор"
    )
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

    @field_validator("slug", mode='after')
    @classmethod
    def slug_validator(cls, v: str):
        if not v.islower():
            raise ValueError("Слаг должен быть с маленькими буквами")
        return v

    @field_validator("title", "slug", mode='after')
    @classmethod
    def no_leading_trailing_spaces(cls, v: str):
        return v.strip()

    @field_validator("slug", mode='after')
    @classmethod
    def autogenerate_slug(cls, v: str):
        if isinstance(v, str):
            return v.lower().replace(" ", "-")
        return v


class PostBrief(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
    id: int
    title: str
    slug: str
    is_published: bool


class PostRead(PostBrief):
    content: str
    author: UserBrief