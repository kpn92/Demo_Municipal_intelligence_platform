"""add employee contracts and assignment items

Revision ID: c21a8c4b92f0
Revises: b4f4d3a8c9e1
Create Date: 2026-04-18 23:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c21a8c4b92f0"
down_revision: Union[str, Sequence[str], None] = "b4f4d3a8c9e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "employee",
        sa.Column(
            "employment_type",
            sa.String(length=20),
            server_default="permanent",
            nullable=False,
        ),
    )
    op.add_column(
        "employee",
        sa.Column("contract_start_date", sa.Date(), nullable=True),
    )
    op.add_column(
        "employee",
        sa.Column("contract_end_date", sa.Date(), nullable=True),
    )

    op.create_table(
        "daily_assignment_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("daily_assignment_id", sa.Integer(), nullable=False),
        sa.Column("sector_item_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["daily_assignment_id"], ["daily_assignment.id"]),
        sa.ForeignKeyConstraint(["sector_item_id"], ["sector_item.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "daily_assignment_id",
            "sector_item_id",
            name="uq_daily_assignment_item_assignment_sector_item",
        ),
    )
    op.create_index(
        "ix_daily_assignment_item_daily_assignment_id",
        "daily_assignment_item",
        ["daily_assignment_id"],
        unique=False,
    )
    op.create_index(
        "ix_daily_assignment_item_sector_item_id",
        "daily_assignment_item",
        ["sector_item_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_daily_assignment_item_sector_item_id",
        table_name="daily_assignment_item",
    )
    op.drop_index(
        "ix_daily_assignment_item_daily_assignment_id",
        table_name="daily_assignment_item",
    )
    op.drop_table("daily_assignment_item")
    op.drop_column("employee", "contract_end_date")
    op.drop_column("employee", "contract_start_date")
    op.drop_column("employee", "employment_type")
