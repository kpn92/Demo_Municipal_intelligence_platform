"""remove legacy waste_bin rows with numeric area_code

Revision ID: 6a4f2e9b8c30
Revises: 5d3e8b1c4f20
Create Date: 2026-05-20 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "6a4f2e9b8c30"
down_revision: Union[str, Sequence[str], None] = "5d3e8b1c4f20"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove bins whose area_code is a plain integer string (legacy GIS import artefacts).
    # Fleet module uses named codes (e.g. "AG_GIORGIS", "D1") — numeric ones are orphaned.
    op.execute(
        sa.text("DELETE FROM waste_bin WHERE area_code ~ '^[0-9]+$'")
    )


def downgrade() -> None:
    # Legacy data is not recoverable from migrations — no-op.
    pass
