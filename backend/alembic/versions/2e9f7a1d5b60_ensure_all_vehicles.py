"""ensure all fleet vehicles exist

Revision ID: 2e9f7a1d5b60
Revises: 1c7e5b9d3f40
Create Date: 2026-05-20 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "2e9f7a1d5b60"
down_revision: Union[str, Sequence[str], None] = "1c7e5b9d3f40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Complete vehicle fleet.  Uses WHERE NOT EXISTS on both unique keys so it is
# safe to run even if a vehicle already exists under either code or plate.
VEHICLES = [
    ("Απορριμματοφόρο 1", "Απορριμματοφόρο", "KHP-4132", "10", "'τόνοι'", "available"),
    ("Απορριμματοφόρο 2", "Απορριμματοφόρο", "KHP-5521", "10", "'τόνοι'", "available"),
    ("Ανακύκλωση 1",      "Ανακύκλωση",      "KHP-2201",  "8", "'τόνοι'", "available"),
    ("Ανακύκλωση 2",      "Ανακύκλωση",      "KHP-2202",  "8", "'τόνοι'", "available"),
    ("Ανακύκλωση 3",      "Ανακύκλωση",      "KHP-2203",  "8", "'τόνοι'", "available"),
    ("Οργανικά 1",        "Οργανικά",        "KHP-3308",  "6", "'τόνοι'", "available"),
    ("Οργανικά 2",        "Οργανικά",        "KHP-3309",  "6", "'τόνοι'", "available"),
    ("Σάρωθρο 1",         "Σάρωθρο",         "KHP-6018", "NULL", "NULL",  "available"),
    ("Εποπτικό Pick-up",  "Εποπτικό",        "KHP-7744", "NULL", "NULL",  "maintenance"),
    ("Υδροφόρα",          "Υδροφόρα",        "KHP-8890", "NULL", "NULL",  "offline"),
]


def upgrade() -> None:
    for code, vtype, plate, cap, unit, status in VEHICLES:
        op.execute(
            f"INSERT INTO vehicle "
            f"(vehicle_code, type, plate_number, capacity, capacity_unit, status, is_active) "
            f"SELECT '{code}', '{vtype}', '{plate}', {cap}, {unit}, '{status}', true "
            f"WHERE NOT EXISTS ("
            f"  SELECT 1 FROM vehicle WHERE vehicle_code = '{code}' OR plate_number = '{plate}'"
            f")"
        )


def downgrade() -> None:
    plates = ", ".join(f"'{p}'" for _, _, p, *_ in VEHICLES)
    op.execute(f"DELETE FROM vehicle WHERE plate_number IN ({plates})")
