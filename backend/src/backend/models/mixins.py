from datetime import datetime

from sqlalchemy import func, String
from sqlalchemy.orm import Mapped, mapped_column


class IdentityMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class TimeStampMixin:
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now()
    )


class SlugMixin:
    slug: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True
    )
