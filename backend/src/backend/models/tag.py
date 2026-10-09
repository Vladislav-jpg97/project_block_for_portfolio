from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import Base
from backend.models.mixins import SlugMixin


class Tag(SlugMixin,Base):
    __tablename__ = 'tags'

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
    )

    posts_count : Mapped[int] = mapped_column(
        default=0
    )

    posts : Mapped[list["Post"]] = relationship(
        secondary="posts_tag",
        back_populates="tags",
    )