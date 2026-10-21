from datetime import datetime

from pydantic import BaseModel, Field


class AuthorBriefResponse(BaseModel):
    id: int
    username: str


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=512)
    parent_id: int | None = None


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=512)


class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    parent_id: int | None
    author: AuthorBriefResponse
    created_at: datetime
    updated_at: datetime
    replies: list["CommentResponse"] = []

CommentResponse.model_rebuild()
