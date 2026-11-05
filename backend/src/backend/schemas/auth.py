from pydantic import BaseModel, field_validator, model_validator

from backend.schemas.user import validate_password

class RefreshToken(BaseModel):
    refresh_token: str

class Token(RefreshToken):
    access_token: str


class UserLogin(BaseModel):
    username: str
    password: str

    @field_validator("username", mode="after")
    @classmethod
    def to_lowercase_username(cls, v: str):
        return v.lower()


class ChangePassword(BaseModel):
    old_password: str
    new_password: str

    @field_validator("old_password", "new_password", mode='after')
    @classmethod
    def password_validator(cls, v):
        return validate_password(v)

    @model_validator(mode='after')
    def passwords_must_differ(self):
        if self.old_password == self.new_password:
            raise ValueError("Новый пароль должен отличаться от старого")
        return self
