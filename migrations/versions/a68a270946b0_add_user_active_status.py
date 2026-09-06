"""add user active status

Revision ID: a68a270946b0
Revises: 5e29786c2265
Create Date: 2026-09-06 21:07:41.067628
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a68a270946b0"
down_revision: Union[str, Sequence[str], None] = "5e29786c2265"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_active", sa.Boolean(), server_default="1", nullable=False))


def downgrade() -> None:
    op.drop_column("users", "is_active")