from pydantic import BaseModel, field_validator, model_validator, ValidationError, EmailStr

from backend.schemas.user import validate_password

class RefreshToken(BaseModel):
    refresh_token: str

class Token(RefreshToken):
    access_token: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str

    @field_validator("old_password", "new_password", mode='after')
    @classmethod
    def password_validator(cls, v):
        return validate_password(v)

    @model_validator(mode='after')
    def password_mathc(self):
        if self.old_password != self.new_password:
            raise ValidationError("Старый пароль не должен совападать с новым")
        return self
