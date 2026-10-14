from pydantic import BaseModel, Field


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
    id: int
