"""seed vehicles

Revision ID: 1c7e5b9d3f40
Revises: 4b2e9f1a7c30
Create Date: 2026-05-20 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "1c7e5b9d3f40"
down_revision: Union[str, Sequence[str], None] = "4b2e9f1a7c30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (vehicle_code, type, plate_number, capacity_tonnes, status)
VEHICLES = [
    ("Απορριμματοφόρο 1", "Απορριμματοφόρο", "KHP-4132", 10, "available"),
    ("Απορριμματοφόρο 2", "Απορριμματοφόρο", "KHP-5521", 10, "available"),
    ("Ανακύκλωση 1",      "Ανακύκλωση",      "KHP-2201",  8, "available"),
    ("Ανακύκλωση 2",      "Ανακύκλωση",      "KHP-2202",  8, "available"),
    ("Ανακύκλωση 3",      "Ανακύκλωση",      "KHP-2203",  8, "available"),
    ("Οργανικά 1",        "Οργανικά",        "KHP-3308",  6, "available"),
    ("Οργανικά 2",        "Οργανικά",        "KHP-3309",  6, "available"),
    ("Σάρωθρο 1",         "Σάρωθρο",         "KHP-6018", None, "available"),
    ("Εποπτικό Pick-up",  "Εποπτικό",        "KHP-7744", None, "maintenance"),
    ("Υδροφόρα",          "Υδροφόρα",        "KHP-8890", None, "offline"),
]


def upgrade() -> None:
    # ON CONFLICT DO NOTHING (no column spec) silently skips rows that
    # violate ANY unique constraint (vehicle_code or plate_number).
    for code, vtype, plate, cap, status in VEHICLES:
        cap_sql  = str(cap) if cap is not None else "NULL"
        unit_sql = "'τόνοι'" if cap is not None else "NULL"
        op.execute(
            f"INSERT INTO vehicle "
            f"(vehicle_code, type, plate_number, capacity, capacity_unit, status, is_active) "
            f"VALUES ('{code}', '{vtype}', '{plate}', {cap_sql}, {unit_sql}, '{status}', true) "
            f"ON CONFLICT DO NOTHING"
        )


def downgrade() -> None:
    plates = ", ".join(f"'{code}'" for _, _, code, _, _ in VEHICLES)
    op.execute(f"DELETE FROM vehicle WHERE plate_number IN ({plates})")
