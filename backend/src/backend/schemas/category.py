from pydantic import BaseModel, Field
from pydantic import ConfigDict


class CategoryBase(BaseModel):
    name: str = Field(
        max_length=100,
    )
    description: str = Field(
        max_length=512,
    )


class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    description: str | None = None
