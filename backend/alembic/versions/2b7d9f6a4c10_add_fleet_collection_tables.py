"""add fleet collection tables

Revision ID: 2b7d9f6a4c10
Revises: f4c3d9b2a1e0
Create Date: 2026-05-05 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.db.geometry import Geometry


# revision identifiers, used by Alembic.
revision: str = "2b7d9f6a4c10"
down_revision: Union[str, Sequence[str], None] = "f4c3d9b2a1e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vehicle",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("vehicle_code", sa.String(length=40), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("plate_number", sa.String(length=20), nullable=False),
        sa.Column("capacity", sa.Numeric(10, 2), nullable=True),
        sa.Column("capacity_unit", sa.String(length=20), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("current_location", Geometry("POINT", 4326), nullable=True),
        sa.Column("area_code", sa.String(length=80), nullable=True),
        sa.Column("area_name", sa.String(length=160), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sector_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["sector_id"], ["sector.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("plate_number", name="uq_vehicle_plate_number"),
        sa.UniqueConstraint("vehicle_code", name="uq_vehicle_vehicle_code"),
    )
    op.create_index("ix_vehicle_status", "vehicle", ["status"], unique=False)
    op.create_index("ix_vehicle_area_code", "vehicle", ["area_code"], unique=False)

    op.create_table(
        "waste_bin",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bin_code", sa.String(length=80), nullable=False),
        sa.Column("type", sa.String(length=40), nullable=False),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("location", Geometry("POINT", 4326), nullable=False),
        sa.Column("area_code", sa.String(length=80), nullable=True),
        sa.Column("area_name", sa.String(length=160), nullable=True),
        sa.Column("road_segment_code", sa.String(length=120), nullable=True),
        sa.Column("fill_level", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("last_collection_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("sector_id", sa.Integer(), nullable=True),
        sa.Column("road_segment_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["road_segment_id"], ["road_segment.id"]),
        sa.ForeignKeyConstraint(["sector_id"], ["sector.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("bin_code", name="uq_waste_bin_bin_code"),
    )
    op.create_index("ix_waste_bin_area_code", "waste_bin", ["area_code"], unique=False)
    op.create_index("ix_waste_bin_road_segment_code", "waste_bin", ["road_segment_code"], unique=False)
    op.create_index("ix_waste_bin_status", "waste_bin", ["status"], unique=False)
    op.create_index("ix_waste_bin_type", "waste_bin", ["type"], unique=False)

    op.create_table(
        "collection_route",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("route_code", sa.String(length=60), nullable=False),
        sa.Column("route_date", sa.Date(), nullable=False),
        sa.Column("area_code", sa.String(length=80), nullable=True),
        sa.Column("area_name", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("estimated_duration_min", sa.Integer(), nullable=True),
        sa.Column("route_geometry", Geometry("LINESTRING", 4326), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("shift_id", sa.Integer(), nullable=True),
        sa.Column("sector_id", sa.Integer(), nullable=True),
        sa.Column("vehicle_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["sector_id"], ["sector.id"]),
        sa.ForeignKeyConstraint(["shift_id"], ["shift.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicle.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("route_code", name="uq_collection_route_route_code"),
    )
    op.create_index("ix_collection_route_area_code", "collection_route", ["area_code"], unique=False)
    op.create_index("ix_collection_route_date", "collection_route", ["route_date"], unique=False)
    op.create_index("ix_collection_route_status", "collection_route", ["status"], unique=False)

    op.create_table(
        "collection_route_bin",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("collection_route_id", sa.Integer(), nullable=False),
        sa.Column("waste_bin_id", sa.Integer(), nullable=False),
        sa.Column("sequence_order", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("collection_time", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["collection_route_id"], ["collection_route.id"]),
        sa.ForeignKeyConstraint(["waste_bin_id"], ["waste_bin.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("collection_route_id", "waste_bin_id", name="uq_collection_route_bin"),
    )
    op.create_index("ix_collection_route_bin_route_id", "collection_route_bin", ["collection_route_id"], unique=False)
    op.create_index("ix_collection_route_bin_status", "collection_route_bin", ["status"], unique=False)

    op.create_table(
        "collection_route_crew_assignment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("collection_route_id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.ForeignKeyConstraint(["collection_route_id"], ["collection_route.id"]),
        sa.ForeignKeyConstraint(["employee_id"], ["employee.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("collection_route_id", "employee_id", name="uq_collection_route_crew_employee"),
    )
    op.create_index(
        "ix_collection_route_crew_assignment_route_id",
        "collection_route_crew_assignment",
        ["collection_route_id"],
        unique=False,
    )

    op.create_table(
        "collection_execution_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("collection_route_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=30), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("location", Geometry("POINT", 4326), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("waste_bin_id", sa.Integer(), nullable=True),
        sa.Column("vehicle_id", sa.Integer(), nullable=True),
        sa.Column("employee_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["collection_route_id"], ["collection_route.id"]),
        sa.ForeignKeyConstraint(["employee_id"], ["employee.id"]),
        sa.ForeignKeyConstraint(["vehicle_id"], ["vehicle.id"]),
        sa.ForeignKeyConstraint(["waste_bin_id"], ["waste_bin.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_collection_execution_event_route_id", "collection_execution_event", ["collection_route_id"], unique=False)
    op.create_index("ix_collection_execution_event_type", "collection_execution_event", ["event_type"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_collection_execution_event_type", table_name="collection_execution_event")
    op.drop_index("ix_collection_execution_event_route_id", table_name="collection_execution_event")
    op.drop_table("collection_execution_event")
    op.drop_index("ix_collection_route_crew_assignment_route_id", table_name="collection_route_crew_assignment")
    op.drop_table("collection_route_crew_assignment")
    op.drop_index("ix_collection_route_bin_status", table_name="collection_route_bin")
    op.drop_index("ix_collection_route_bin_route_id", table_name="collection_route_bin")
    op.drop_table("collection_route_bin")
    op.drop_index("ix_collection_route_status", table_name="collection_route")
    op.drop_index("ix_collection_route_date", table_name="collection_route")
    op.drop_index("ix_collection_route_area_code", table_name="collection_route")
    op.drop_table("collection_route")
    op.drop_index("ix_waste_bin_type", table_name="waste_bin")
    op.drop_index("ix_waste_bin_status", table_name="waste_bin")
    op.drop_index("ix_waste_bin_road_segment_code", table_name="waste_bin")
    op.drop_index("ix_waste_bin_area_code", table_name="waste_bin")
    op.drop_table("waste_bin")
    op.drop_index("ix_vehicle_area_code", table_name="vehicle")
    op.drop_index("ix_vehicle_status", table_name="vehicle")
    op.drop_table("vehicle")
