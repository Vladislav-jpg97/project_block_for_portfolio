from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.mixins import TimeStampMixin
from backend.models.post import Post
from backend.models.vote import PostVote


class User(TimeStampMixin, Base):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
    )
    bio: Mapped[str | None] = mapped_column(
        String(512),
    )
    karma:Mapped[int] = mapped_column(
        default=0
    )
    is_active: Mapped[bool] = mapped_column(
        default=True
    )
    is_superuser: Mapped[bool] = mapped_column(
        default=False
    )

    posts : Mapped[list[Post]] = relationship(
        back_populates="author"
    )

    post_votes: Mapped[list["PostVote"]] = relationship(
        back_populates="user"
    )

    bookmarks: Mapped[list["Bookmark"]] = relationship(
        back_populates="user"
    )
