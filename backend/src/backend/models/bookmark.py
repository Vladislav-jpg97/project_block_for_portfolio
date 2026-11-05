from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import Base
from backend.models.mixins import TimeStampMixin


class Bookmark(TimeStampMixin, Base):
    __tablename__ = "bookmarks"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
    )

    user: Mapped["User"] = relationship(
        back_populates="bookmarks",
    )

    post: Mapped["Post"] = relationship(
        back_populates="bookmarks",
    )
