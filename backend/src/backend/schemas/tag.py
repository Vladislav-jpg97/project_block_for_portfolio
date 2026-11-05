from pydantic import BaseModel, Field, ConfigDict


class TagBase(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=50,
    )


class TagCreate(TagBase):
    pass


class TagRead(TagBase):
    model_config = ConfigDict(
        from_attributes=True
    )
    id: int
    posts_count: int = Field(
        default=0,
    )
    slug: str
