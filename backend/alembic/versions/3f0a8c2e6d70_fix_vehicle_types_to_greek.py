"""fix existing vehicle codes and types to Greek names

Revision ID: 3f0a8c2e6d70
Revises: 2e9f7a1d5b60
Create Date: 2026-05-20 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "3f0a8c2e6d70"
down_revision: Union[str, Sequence[str], None] = "2e9f7a1d5b60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Map plate → (new vehicle_code, new type, correct status)
UPDATES = [
    ("KHP-4132", "Απορριμματοφόρο 1", "Απορριμματοφόρο", "available"),
    ("KHP-5521", "Απορριμματοφόρο 2", "Απορριμματοφόρο", "available"),
    ("KHP-6018", "Σάρωθρο 1",         "Σάρωθρο",         "available"),
    ("KHP-7744", "Εποπτικό Pick-up",   "Εποπτικό",        "maintenance"),
    ("KHP-8890", "Υδροφόρα",           "Υδροφόρα",        "offline"),
]


def upgrade() -> None:
    for plate, code, vtype, status in UPDATES:
        op.execute(
            f"UPDATE vehicle "
            f"SET vehicle_code = '{code}', type = '{vtype}', status = '{status}' "
            f"WHERE plate_number = '{plate}'"
        )


def downgrade() -> None:
    # Restore original English values
    originals = [
        ("KHP-4132", "VEH-001", "garbage_truck",   "available"),
        ("KHP-5521", "VEH-002", "garbage_truck",   "available"),
        ("KHP-6018", "VEH-003", "street_sweeper",  "available"),
        ("KHP-7744", "VEH-004", "pickup",           "available"),
        ("KHP-8890", "VEH-005", "water_truck",      "available"),
    ]
    for plate, code, vtype, status in originals:
        op.execute(
            f"UPDATE vehicle "
            f"SET vehicle_code = '{code}', type = '{vtype}', status = '{status}' "
            f"WHERE plate_number = '{plate}'"
        )
