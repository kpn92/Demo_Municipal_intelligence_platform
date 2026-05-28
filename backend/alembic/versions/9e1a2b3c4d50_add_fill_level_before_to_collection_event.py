"""add fill_level_before to collection_execution_event

Revision ID: 9e1a2b3c4d50
Revises: 3f0a8c2e6d70
Create Date: 2026-05-25 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "9e1a2b3c4d50"
down_revision: Union[str, Sequence[str], None] = "3f0a8c2e6d70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "collection_execution_event",
        sa.Column("fill_level_before", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("collection_execution_event", "fill_level_before")
