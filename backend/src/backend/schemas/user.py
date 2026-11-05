from dataclasses import dataclass
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from sqlalchemy import Select
from backend.models import User
from backend.schemas.filters import BaseFilter


def validate_password(password: str) -> str:
    errors_msg = []
    if not (any(c.islower() for c in password)):
        errors_msg.append("Хотя бы одна маленькая буква")
    if not (any(c.isupper() for c in password)):
        errors_msg.append("Хотя бы одна большая буква")
    if not (any(c.isdigit() for c in password)):
        errors_msg.append("Хотя бы одна цифра")
    if errors_msg:
        raise ValueError(f"Пароль должен содержать : {', '.join(errors_msg)}")
    return password


class UserBase(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z0-9-_]+$"
    )
    @field_validator("password",mode="after")
    @classmethod
    def to_lowercase_username(cls,v:str):
        return v.lower()


class UserCreate(UserBase):
    password: str = Field(min_length=8)
    email: EmailStr

    @field_validator("password", mode='after')
    @classmethod
    def password_validator(cls, v):
        return validate_password(v)


class UserUpdate(UserBase):
    email: EmailStr
    bio: str | None = Field(default=None, max_length=512)


class UserBrief(UserBase):
    model_config = ConfigDict(
        from_attributes=True,
    )
    id: int
    karma: int
    avatar_url: str | None = None


class UserRead(UserBrief):
    email: EmailStr
    bio: str | None = None
    created_at: datetime


@dataclass(frozen=True)
class UserFilter(BaseFilter):
    q: str | None = None

    def filter(self, stmt: Select) -> Select:
        if self.q is not None:
            stmt = stmt.where(User.username.ilike(f"%{self.q}%"))
        return stmt
