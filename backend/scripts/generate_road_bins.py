"""
Generate 50 waste bin positions per area, placed on actual road coordinates.
Reads: data/gis_exports/urban_units.geojson (area polygons)
       data/gis_exports/line_roads.geojson  (road network)
Outputs: Python list of bin dicts, ready for an Alembic migration.
"""
import json
import math
import sys
from pathlib import Path

try:
    from shapely.geometry import shape, MultiLineString, LineString, Point
    from shapely.ops import unary_union
except ImportError:
    sys.exit("shapely not installed — run: pip install shapely")

ROOT = Path(__file__).resolve().parents[2]
URBAN_UNITS = ROOT / "data" / "gis_exports" / "urban_units.geojson"
ROADS_FILE  = ROOT / "data" / "gis_exports" / "line_roads.geojson"

# Exact perigrafi values from the GeoJSON (Greek uppercase as stored)
PERIGRAFI_TO_AREA = {
    "Δ1":                 ("D1",          "Δ1"),
    "Δ2":                 ("D2",          "Δ2"),
    "Δ3":                 ("D3",          "Δ3"),
    "Δ4":                 ("D4",          "Δ4"),
    "Δ5":                 ("D5",          "Δ5"),
    "ΑΓ. ΓΙΩΡΓΗΣ":   ("AG_GIORGIS",  "Αγ. Γεώργης"),
    "ΤΑΜΠΟΥΡΙΑ":      ("TAMBOYRIA",   "Ταμπούρια"),
    "ΚΟΚΚΙΝΟΒΡΑΧΟΣ": ("KOKKINO", "Κοκκινόβραχος"),
    "ΧΑΡΑΥΓΗ":                  ("CHARAUGI",    "Χαραυγή"),
    "ΑΓ. ΑΝΤΩΝΙΟΣ": ("AG_ANTONIOS", "Αγ. Αντώνιος"),
    "ΑΝΑΛΗΨΗ":                  ("ANALYPSI",    "Ανάληψη"),
    "ΠΑΝ. ΒΛΑΧΕΡΝΩΝ": ("PAN_VLACH", "Παν. Βλαχερνών"),
    "ΕΥΓΕΝΕΙΑ":            ("EVGENIA",     "Ευγένεια"),
    "ΑΣΤΡΟ ΑΜΦΙΑΛΗΣ": ("ASTRO", "Αστρο Αμφιάλης"),
    "ΑΓ. ΜΗΝΑΣ":                ("AG_MINAS",    "Αγ. Μηνάς"),
}

BINS_PER_AREA = 50


def _type_for(idx: int) -> tuple:
    r = idx % 20
    if r in (0, 1, 2, 3):
        return "recycling", 2500
    if r in (4, 5, 6):
        return "organic", 240
    return "mixed", 1100


def _fill_for(area_idx: int, bin_idx: int) -> int:
    return (area_idx * 37 + bin_idx * 13 + 7) % 97


def _status_for(idx: int) -> str:
    r = idx % 25
    if r == 24:
        return "offline"
    if r in (10, 20):
        return "issue"
    return "normal"


def sample_points_on_line(multi_line, n: int) -> list:
    """Sample n evenly-spaced points along a MultiLineString or LineString."""
    total_len = multi_line.length
    if total_len == 0:
        return []
    step = total_len / (n + 1)
    points = []
    for i in range(1, n + 1):
        pt = multi_line.interpolate(step * i)
        points.append((round(pt.x, 6), round(pt.y, 6)))
    return points


def main():
    urban = json.loads(URBAN_UNITS.read_bytes())
    roads = json.loads(ROADS_FILE.read_bytes())

    # Build road union
    road_geoms = [shape(f["geometry"]) for f in roads["features"] if f.get("geometry")]
    all_roads = unary_union(road_geoms)
    print(f"Road features loaded: {len(road_geoms)}")

    # Parse area polygons
    areas = []
    for feat in urban["features"]:
        props = feat.get("properties", {})
        perigrafi_raw = props.get("perigrafi", "").strip()
        mapping = PERIGRAFI_TO_AREA.get(perigrafi_raw)
        if mapping is None:
            print(f"  SKIP unknown perigrafi (len={len(perigrafi_raw)})")
            continue
        area_code, area_name = mapping
        poly = shape(feat["geometry"])
        areas.append((area_code, area_name, poly))

    print(f"Areas matched: {len(areas)}")

    bins = []
    serial = 1
    for area_idx, (area_code, area_name, poly) in enumerate(areas):
        clipped = all_roads.intersection(poly)
        if clipped.is_empty:
            print(f"  WARNING: no roads in area {area_code} — using centroid fallback")
            # Fallback: 5x10 grid inside polygon bounds
            minx, miny, maxx, maxy = poly.bounds
            pts = []
            cols, rows = 10, 5
            for r in range(rows):
                for c in range(cols):
                    lx = minx + (maxx - minx) * (c + 1) / (cols + 1)
                    ly = miny + (maxy - miny) * (r + 1) / (rows + 1)
                    pts.append((round(lx, 6), round(ly, 6)))
        else:
            if isinstance(clipped, LineString):
                clipped = MultiLineString([clipped])
            elif not isinstance(clipped, MultiLineString):
                # Could be GeometryCollection with mixed types
                lines = [g for g in getattr(clipped, "geoms", [clipped])
                         if isinstance(g, (LineString, MultiLineString))]
                clipped = unary_union(lines) if lines else clipped

            pts = sample_points_on_line(clipped, BINS_PER_AREA)
            if len(pts) < BINS_PER_AREA:
                print(f"  WARNING: only {len(pts)} road points in {area_code}, padding with repeats")
                while len(pts) < BINS_PER_AREA:
                    pts.append(pts[len(pts) % max(len(pts), 1)])

        print(f"  {area_code}: {len(pts)} points")

        for bin_idx, (lng, lat) in enumerate(pts[:BINS_PER_AREA]):
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

    print(f"\nTotal bins generated: {len(bins)}")

    # Print as Python list for embedding in migration
    out_path = Path(__file__).parent / "road_bins_output.py"
    lines = ["# Auto-generated by generate_road_bins.py — do not edit manually\n",
             "ROAD_BINS = [\n"]
    for b in bins:
        lines.append(
            f'    {{"bin_code": "{b["bin_code"]}", "type": "{b["type"]}", "capacity": {b["capacity"]}, '
            f'"area_code": "{b["area_code"]}", "area_name": "{b["area_name"]}", '
            f'"lng": {b["lng"]}, "lat": {b["lat"]}, '
            f'"fill_level": {b["fill_level"]}, "status": "{b["status"]}"}},\n'
        )
    lines.append("]\n")
    out_path.write_text("".join(lines), encoding="utf-8")
    print(f"Written to {out_path}")


if __name__ == "__main__":
    main()
