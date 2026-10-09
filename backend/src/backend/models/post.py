from sqlalchemy import String, Text, ForeignKey, Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.base import Base
from backend.models.mixins import TimeStampMixin, SlugMixin

post_tags = Table(
    "post_tags",
    Base.metadata,
    Column(
        "post_id",
        ForeignKey("posts.id", ondelete='CASCADE'),
        primary_key=True
    ),
    Column(
        "tag_id",
        ForeignKey("tags.id", ondelete='CASCADE'),
        primary_key=True
    ),
)


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

    category_id: Mapped[int] = mapped_column(
        ForeignKey('categories.id', ondelete='RESTRICT')
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
        back_populates="posts",
        lazy="select",
    )

    tags: Mapped[list["Tag"]] = relationship(
        secondary=post_tags,
        back_populates="posts"
    )

    comments: Mapped[list["Comment"]] = relationship(
        back_populates="post",
    )

    post_votes: Mapped[list["PostVote"]] = relationship(
        back_populates="post",
    )

    bookmarks: Mapped[list["Bookmark"]] = relationship(
        back_populates="post",
    )

    category: Mapped["Category"] = relationship(
        back_populates="posts",
    )
