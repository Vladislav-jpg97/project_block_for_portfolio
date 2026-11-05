from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AuthorBriefResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=512)
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=512)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    content: str
    post_id: int
    parent_id: int | None
    author: AuthorBriefResponse
    created_at: datetime
    updated_at: datetime
    replies: list["CommentResponse"] = Field(default_factory=list)

CommentResponse.model_rebuild()
