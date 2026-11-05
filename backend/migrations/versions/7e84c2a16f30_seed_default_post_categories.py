"""Seed the default categories required for creating posts.

Revision ID: 7e84c2a16f30
Revises: 5a9ca92ee479
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7e84c2a16f30"
down_revision: Union[str, Sequence[str], None] = "5a9ca92ee479"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


DEFAULT_CATEGORIES = (
    ("Python", "Python-разработка и экосистема языка.", "python"),
    ("JavaScript", "JavaScript, TypeScript и веб-разработка.", "javascript"),
    ("Backend", "Серверная разработка, API и базы данных.", "backend"),
    ("Frontend", "Интерфейсы, браузеры и клиентские приложения.", "frontend"),
    ("DevOps", "Инфраструктура, CI/CD и облачные технологии.", "devops"),
    ("Career", "Карьера, обучение и профессиональный рост.", "career"),
)


def upgrade() -> None:
    # ADDED: Fresh installations need selectable categories before users can publish.
    bind = op.get_bind()
    for name, description, slug in DEFAULT_CATEGORIES:
        bind.execute(
            sa.text(
                """
                INSERT INTO categories (name, description, slug)
                SELECT :name, :description, :slug
                WHERE NOT EXISTS (
                    SELECT 1 FROM categories
                    WHERE name = :name OR slug = :slug
                )
                """
            ).bindparams(
                name=name,
                description=description,
                slug=slug,
            )
        )


def downgrade() -> None:
    # Keep seed topics on downgrade: user posts may reference them.
    pass
