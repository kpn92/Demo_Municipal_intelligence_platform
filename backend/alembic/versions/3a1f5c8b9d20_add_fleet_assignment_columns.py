"""add fleet assignment columns to collection_route

Revision ID: 3a1f5c8b9d20
Revises: 2b7d9f6a4c10
Create Date: 2026-05-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3a1f5c8b9d20"
down_revision: Union[str, Sequence[str], None] = "2b7d9f6a4c10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("collection_route", sa.Column("area_codes", sa.JSON(), nullable=True))
    op.add_column("collection_route", sa.Column("area_names", sa.JSON(), nullable=True))
    op.add_column("collection_route", sa.Column("estimated_km", sa.Numeric(8, 2), nullable=True))
    op.add_column("collection_route", sa.Column("total_bins", sa.Integer(), nullable=True))
    op.add_column("collection_route", sa.Column("total_trips", sa.SmallInteger(), nullable=True))
    op.add_column("collection_route", sa.Column("red_count", sa.SmallInteger(), nullable=True))
    op.add_column("collection_route", sa.Column("yellow_count", sa.SmallInteger(), nullable=True))
    op.add_column("collection_route", sa.Column("green_count", sa.SmallInteger(), nullable=True))
    op.add_column("collection_route", sa.Column("road_coordinates", sa.JSON(), nullable=True))
    op.add_column("collection_route", sa.Column("vehicle_plate", sa.String(length=20), nullable=True))
    op.add_column("collection_route", sa.Column("vehicle_name", sa.String(length=160), nullable=True))
    op.add_column("collection_route", sa.Column("vehicle_frontend_id", sa.String(length=40), nullable=True))

    op.create_index(
        "ix_collection_route_vehicle_frontend_id",
        "collection_route",
        ["vehicle_frontend_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_collection_route_vehicle_frontend_id", table_name="collection_route")
    op.drop_column("collection_route", "vehicle_frontend_id")
    op.drop_column("collection_route", "vehicle_name")
    op.drop_column("collection_route", "vehicle_plate")
    op.drop_column("collection_route", "road_coordinates")
    op.drop_column("collection_route", "green_count")
    op.drop_column("collection_route", "yellow_count")
    op.drop_column("collection_route", "red_count")
    op.drop_column("collection_route", "total_trips")
    op.drop_column("collection_route", "total_bins")
    op.drop_column("collection_route", "estimated_km")
    op.drop_column("collection_route", "area_names")
    op.drop_column("collection_route", "area_codes")
