from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models import Base


class PostVote(Base):
    __tablename__ = "post_votes"

    __table_args__ = (
        UniqueConstraint(
            "user_id", "post_id"
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
    )

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"),
    )

    value: Mapped[float] = mapped_column()

    user: Mapped["User"] = relationship(
        back_populates="post_votes",
    )

    post: Mapped["Post"] = relationship(
        back_populates="post_votes",
    )