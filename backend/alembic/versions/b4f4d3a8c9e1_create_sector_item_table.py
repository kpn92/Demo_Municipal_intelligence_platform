"""create sector item table

Revision ID: b4f4d3a8c9e1
Revises: 6701cee1cffe
Create Date: 2026-04-18 23:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b4f4d3a8c9e1"
down_revision: Union[str, Sequence[str], None] = "6701cee1cffe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sector_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("sector_id", sa.Integer(), nullable=False),
        sa.Column("item_type", sa.String(length=30), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["sector_id"], ["sector.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_sector_item_sector_id",
        "sector_item",
        ["sector_id"],
        unique=False,
    )
    op.create_index(
        "ix_sector_item_item_type",
        "sector_item",
        ["item_type"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_sector_item_item_type", table_name="sector_item")
    op.drop_index("ix_sector_item_sector_id", table_name="sector_item")
    op.drop_table("sector_item")
