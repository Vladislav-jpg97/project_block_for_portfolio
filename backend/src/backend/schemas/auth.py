from pydantic import BaseModel, Field, EmailStr, field_validator, ValidationError, model_validator


class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=100,
        pattern=r"^[a-zA-Z0-9-]+$"
    )
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("password", mode='after')
    @classmethod
    def password_validator(cls, v):
        errors_msg = []
        if not (any(c.islower() for c in v)):
            errors_msg.append("Хотя бы одна маленькая буква")
        if not (any(c.isupper() for c in v)):
            errors_msg.append("Хотя бы одна большая буква")
        if not (any(c.isdigit() for c in v)):
            errors_msg.append("Хотя бы одна цифра")
        if errors_msg:
            raise ValidationError(f"Пароль должен содержать : {', '.join(errors_msg)}")
        return v


class ChangePassword(BaseModel):
    old_password: str
    new_password: str

    @model_validator(mode='after')
    def password_mathc(self):
        if self.old_password != self.new_password:
            raise ValidationError("Старый пароль не должен совападать с новым")
        return self

class UserBrief(BaseModel):
    username: str
    email: EmailStr