"""replace waste bins with 50 per area (750 total)

Revision ID: 7b5c3d1e8a40
Revises: 6a4f2e9b8c30
Create Date: 2026-05-20 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b5c3d1e8a40"
down_revision: Union[str, Sequence[str], None] = "6a4f2e9b8c30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# fmt: off
# Each area: (area_code, area_name, min_lng, max_lng, min_lat, max_lat)
AREAS = [
    ("AG_GIORGIS",  "Αγ. Γεώργης",       23.6120, 23.6240, 37.9580, 37.9650),
    ("TAMBOYRIA",   "Ταμπούρια",          23.6240, 23.6305, 37.9580, 37.9650),
    ("KOKKINO",     "Κοκκινόβραχος",      23.6215, 23.6295, 37.9700, 37.9760),
    ("D1",          "Δ1",                  23.6220, 23.6285, 37.9460, 37.9525),
    ("D2",          "Δ2",                  23.6280, 23.6360, 37.9480, 37.9540),
    ("CHARAUGI",    "Χαραυγή",            23.6100, 23.6200, 37.9490, 37.9580),
    ("AG_ANTONIOS", "Αγ. Αντώνιος",       23.6190, 23.6280, 37.9710, 37.9780),
    ("ANALYPSI",    "Ανάληψη",            23.6225, 23.6300, 37.9505, 37.9580),
    ("D3",          "Δ3",                  23.6225, 23.6300, 37.9430, 37.9490),
    ("PAN_VLACH",   "Παν. Βλαχερνών",     23.6205, 23.6335, 37.9635, 37.9720),
    ("EVGENIA",     "Ευγένεια",           23.6165, 23.6235, 37.9505, 37.9590),
    ("D5",          "Δ5",                  23.6165, 23.6230, 37.9475, 37.9525),
    ("ASTRO",       "Άστρο Αμφιάλης",     23.6125, 23.6240, 37.9625, 37.9720),
    ("D4",          "Δ4",                  23.6275, 23.6355, 37.9445, 37.9500),
    ("AG_MINAS",    "Αγ. Μηνάς",          23.6075, 23.6195, 37.9645, 37.9755),
]
BINS_PER_AREA = 50
COLS, ROWS = 10, 5  # 10×5 grid = 50 positions


def _type_for(idx: int) -> tuple[str, int]:
    """Returns (type, capacity) — 65% mixed, 20% recycling, 15% organic."""
    r = idx % 20
    if r in (0, 1, 2, 3):
        return "recycling", 2500
    if r in (4, 5, 6):
        return "organic", 240
    return "mixed", 1100


def _fill_for(area_idx: int, bin_idx: int) -> int:
    """Pseudo-random fill 0–96, varied per area + bin."""
    return (area_idx * 37 + bin_idx * 13 + 7) % 97


def _status_for(idx: int) -> str:
    """88% normal, 8% issue, 4% offline."""
    r = idx % 25
    if r == 24:
        return "offline"
    if r in (10, 20):
        return "issue"
    return "normal"


def generate_bins() -> list[dict]:
    bins = []
    serial = 1
    for area_idx, (area_code, area_name, min_lng, max_lng, min_lat, max_lat) in enumerate(AREAS):
        lng_step = (max_lng - min_lng) / (COLS + 1)
        lat_step = (max_lat - min_lat) / (ROWS + 1)
        for row in range(ROWS):
            for col in range(COLS):
                bin_idx = row * COLS + col
                lng = round(min_lng + lng_step * (col + 1), 6)
                lat = round(min_lat + lat_step * (row + 1), 6)
                bin_type, capacity = _type_for(area_idx * 7 + bin_idx)
                fill = _fill_for(area_idx, bin_idx)
                status = _status_for(area_idx * 3 + bin_idx)
                bins.append({
                    "bin_code": f"KHR-{serial:04d}",
                    "type": bin_type,
                    "capacity": capacity,
                    "area_code": area_code,
                    "area_name": area_name,
                    "lng": lng,
                    "lat": lat,
                    "fill_level": fill,
                    "status": status,
                })
                serial += 1
    return bins
# fmt: on


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM waste_bin"))
    for b in generate_bins():
        conn.execute(
            sa.text("""
                INSERT INTO waste_bin
                    (bin_code, type, capacity, location, area_code, area_name,
                     fill_level, status, is_active)
                VALUES (
                    :bin_code, :type, :capacity,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
                    :area_code, :area_name,
                    :fill_level, :status, TRUE
                )
            """),
            b,
        )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM waste_bin"))
