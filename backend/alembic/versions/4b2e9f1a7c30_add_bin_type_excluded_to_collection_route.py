"""add bin_type and excluded_bin_ids to collection_route

Revision ID: 4b2e9f1a7c30
Revises: 3a1f5c8b9d20
Create Date: 2026-05-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4b2e9f1a7c30"
down_revision: Union[str, Sequence[str], None] = ("8c6d4f2a1b50", "3a1f5c8b9d20")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("collection_route", sa.Column("bin_type", sa.String(40), nullable=True))
    op.add_column("collection_route", sa.Column("excluded_bin_ids", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("collection_route", "excluded_bin_ids")
    op.drop_column("collection_route", "bin_type")
