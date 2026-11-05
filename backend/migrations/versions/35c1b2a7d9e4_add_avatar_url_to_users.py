"""Add persistent avatar URL to user profiles.

Revision ID: 35c1b2a7d9e4
Revises: 7e84c2a16f30
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "35c1b2a7d9e4"
down_revision: Union[str, Sequence[str], None] = "7e84c2a16f30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "avatar_url")
