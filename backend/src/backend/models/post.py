from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.mixins import TimeStampMixin, SlugMixin


class Post(TimeStampMixin, SlugMixin, Base):
    __tablename__ = 'posts'

    title: Mapped[str] = mapped_column(
        String(200),
    )

    content: Mapped[str] = mapped_column(
        Text
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE')

    )

    is_published: Mapped[bool] = mapped_column(
        default=False,
    )

    view_count: Mapped[int] = mapped_column(
        default=0
    )

    votes_count: Mapped[int] = mapped_column(
        default=0
    )

    author: Mapped["User"] = relationship(
        back_populates="posts"
    )
