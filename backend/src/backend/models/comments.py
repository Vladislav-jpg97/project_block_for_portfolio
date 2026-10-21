from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.models import Base
from backend.models.mixins import TimeStampMixin


class Comment(TimeStampMixin, Base):
    __tablename__ = "comments"

    content: Mapped[str] = mapped_column(
        String(512),
    )

    author_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
    )

    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"),
    )

    votes_count: Mapped[int] = mapped_column(
        default=0
    )

    autor: Mapped["User"] = relationship(
        back_populates="comments",
        lazy="select",
    )

    post: Mapped["Post"] = relationship(
        back_populates="comments",
    )

    replies: Mapped[list["Comment"]] = relationship(
        back_populates="parent",
    )

    parent: Mapped["Comment | None"] = relationship(
        back_populates="replies",
        remote_side="Comment.id",
    )
