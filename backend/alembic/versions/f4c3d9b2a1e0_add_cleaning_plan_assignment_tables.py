"""add cleaning plan assignment tables

Revision ID: f4c3d9b2a1e0
Revises: e42a7d91c3f5
Create Date: 2026-04-22 23:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f4c3d9b2a1e0"
down_revision: Union[str, Sequence[str], None] = "e42a7d91c3f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cleaning_plan_assignment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("assignment_date", sa.Date(), nullable=False),
        sa.Column("area_code", sa.String(length=80), nullable=False),
        sa.Column("area_name", sa.String(length=160), nullable=False),
        sa.Column("crew_code", sa.String(length=40), nullable=False),
        sa.Column("crew_label", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("estimated_length_km", sa.Numeric(10, 2), nullable=True),
        sa.Column("estimated_duration_min", sa.Integer(), nullable=True),
        sa.Column("required_personnel", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("shift_id", sa.Integer(), nullable=True),
        sa.Column("cleaning_zone_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["cleaning_zone_id"], ["cleaning_zone.id"]),
        sa.ForeignKeyConstraint(["shift_id"], ["shift.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_cleaning_plan_assignment_assignment_date",
        "cleaning_plan_assignment",
        ["assignment_date"],
        unique=False,
    )
    op.create_index(
        "ix_cleaning_plan_assignment_area_code",
        "cleaning_plan_assignment",
        ["area_code"],
        unique=False,
    )
    op.create_index(
        "ix_cleaning_plan_assignment_crew_code",
        "cleaning_plan_assignment",
        ["crew_code"],
        unique=False,
    )

    op.create_table(
        "cleaning_plan_assignment_employee",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cleaning_plan_assignment_id", sa.Integer(), nullable=False),
        sa.Column("employee_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["cleaning_plan_assignment_id"], ["cleaning_plan_assignment.id"]),
        sa.ForeignKeyConstraint(["employee_id"], ["employee.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "cleaning_plan_assignment_id",
            "employee_id",
            name="uq_cleaning_plan_assignment_employee",
        ),
    )
    op.create_index(
        "ix_cleaning_plan_assignment_employee_assignment_id",
        "cleaning_plan_assignment_employee",
        ["cleaning_plan_assignment_id"],
        unique=False,
    )
    op.create_index(
        "ix_cleaning_plan_assignment_employee_employee_id",
        "cleaning_plan_assignment_employee",
        ["employee_id"],
        unique=False,
    )

    op.create_table(
        "cleaning_plan_assignment_road",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cleaning_plan_assignment_id", sa.Integer(), nullable=False),
        sa.Column("segment_code", sa.String(length=120), nullable=False),
        sa.Column("road_name", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("planned_order", sa.Integer(), nullable=True),
        sa.Column("priority", sa.Integer(), nullable=True),
        sa.Column("estimated_duration_min", sa.Integer(), nullable=True),
        sa.Column("road_length_km", sa.Numeric(10, 3), nullable=True),
        sa.Column("road_segment_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["cleaning_plan_assignment_id"], ["cleaning_plan_assignment.id"]),
        sa.ForeignKeyConstraint(["road_segment_id"], ["road_segment.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "cleaning_plan_assignment_id",
            "segment_code",
            name="uq_cleaning_plan_assignment_road_segment_code",
        ),
    )
    op.create_index(
        "ix_cleaning_plan_assignment_road_assignment_id",
        "cleaning_plan_assignment_road",
        ["cleaning_plan_assignment_id"],
        unique=False,
    )
    op.create_index(
        "ix_cleaning_plan_assignment_road_segment_code",
        "cleaning_plan_assignment_road",
        ["segment_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_cleaning_plan_assignment_road_segment_code", table_name="cleaning_plan_assignment_road")
    op.drop_index("ix_cleaning_plan_assignment_road_assignment_id", table_name="cleaning_plan_assignment_road")
    op.drop_table("cleaning_plan_assignment_road")
    op.drop_index("ix_cleaning_plan_assignment_employee_employee_id", table_name="cleaning_plan_assignment_employee")
    op.drop_index("ix_cleaning_plan_assignment_employee_assignment_id", table_name="cleaning_plan_assignment_employee")
    op.drop_table("cleaning_plan_assignment_employee")
    op.drop_index("ix_cleaning_plan_assignment_crew_code", table_name="cleaning_plan_assignment")
    op.drop_index("ix_cleaning_plan_assignment_area_code", table_name="cleaning_plan_assignment")
    op.drop_index("ix_cleaning_plan_assignment_assignment_date", table_name="cleaning_plan_assignment")
    op.drop_table("cleaning_plan_assignment")
