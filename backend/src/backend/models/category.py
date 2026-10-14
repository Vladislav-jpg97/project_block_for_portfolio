from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models import Base
from backend.models.mixins import SlugMixin, TimeStampMixin


class Category(SlugMixin, Base, TimeStampMixin):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    description: Mapped[str | None] = mapped_column(
        String(512),
    )

    posts : Mapped[list["Post"]] = relationship(
        back_populates="category",
    )
