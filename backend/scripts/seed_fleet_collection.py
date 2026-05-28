from __future__ import annotations

import json
import math
from pathlib import Path

from sqlalchemy import create_engine, text

from app.core.config import settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ROADS_GEOJSON = PROJECT_ROOT / "frontend" / "mapping" / "data" / "context" / "line_roads.geojson"

VEHICLES = [
    {
        "vehicle_code": "VEH-001",
        "type": "garbage_truck",
        "plate_number": "KHP-4132",
        "capacity": 12.0,
        "capacity_unit": "m3",
        "status": "available",
        "lng": 23.6206,
        "lat": 37.9588,
        "area_code": "2",
        "area_name": "Δ2",
    },
    {
        "vehicle_code": "VEH-002",
        "type": "garbage_truck",
        "plate_number": "KHP-5521",
        "capacity": 12.0,
        "capacity_unit": "m3",
        "status": "route",
        "lng": 23.6129,
        "lat": 37.9676,
        "area_code": "10",
        "area_name": "ΤΑΜΠΟΥΡΙΑ",
    },
    {
        "vehicle_code": "VEH-003",
        "type": "street_sweeper",
        "plate_number": "KHP-6018",
        "capacity": 5.0,
        "capacity_unit": "m3",
        "status": "route",
        "lng": 23.6264,
        "lat": 37.9607,
        "area_code": "12",
        "area_name": "ΑΓ. ΓΙΩΡΓΗΣ",
    },
    {
        "vehicle_code": "VEH-004",
        "type": "pickup",
        "plate_number": "KHP-7744",
        "capacity": 1.0,
        "capacity_unit": "tn",
        "status": "maintenance",
        "lng": 23.6181,
        "lat": 37.9529,
        "area_code": None,
        "area_name": "Αμαξοστάσιο",
    },
    {
        "vehicle_code": "VEH-005",
        "type": "water_truck",
        "plate_number": "KHP-8890",
        "capacity": 8.0,
        "capacity_unit": "m3",
        "status": "offline",
        "lng": 23.6172,
        "lat": 37.9537,
        "area_code": None,
        "area_name": "Αμαξοστάσιο",
    },
]


def main() -> None:
    engine = create_engine(settings.database_url)
    roads = json.loads(ROADS_GEOJSON.read_text(encoding="utf-8"))["features"]
    bins = build_bins(roads)

    with engine.begin() as connection:
        seed_vehicles(connection)
        seed_bins(connection, bins)

    print(f"Seeded {len(VEHICLES)} vehicle(s) and {len(bins)} bin(s).")


def seed_vehicles(connection) -> None:
    for vehicle in VEHICLES:
        connection.execute(
            text(
                """
                INSERT INTO vehicle (
                    vehicle_code,
                    type,
                    plate_number,
                    capacity,
                    capacity_unit,
                    status,
                    current_location,
                    area_code,
                    area_name,
                    is_active
                )
                VALUES (
                    :vehicle_code,
                    :type,
                    :plate_number,
                    :capacity,
                    :capacity_unit,
                    :status,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
                    :area_code,
                    :area_name,
                    TRUE
                )
                ON CONFLICT (vehicle_code) DO UPDATE SET
                    type = EXCLUDED.type,
                    plate_number = EXCLUDED.plate_number,
                    capacity = EXCLUDED.capacity,
                    capacity_unit = EXCLUDED.capacity_unit,
                    status = EXCLUDED.status,
                    current_location = EXCLUDED.current_location,
                    area_code = EXCLUDED.area_code,
                    area_name = EXCLUDED.area_name,
                    is_active = TRUE
                """
            ),
            vehicle,
        )


def seed_bins(connection, bins: list[dict]) -> None:
    for waste_bin in bins:
        connection.execute(
            text(
                """
                INSERT INTO waste_bin (
                    bin_code,
                    type,
                    capacity,
                    location,
                    area_code,
                    area_name,
                    road_segment_code,
                    fill_level,
                    status,
                    is_active
                )
                VALUES (
                    :bin_code,
                    :type,
                    :capacity,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
                    :area_code,
                    :area_name,
                    :road_segment_code,
                    :fill_level,
                    :status,
                    TRUE
                )
                ON CONFLICT (bin_code) DO UPDATE SET
                    type = EXCLUDED.type,
                    capacity = EXCLUDED.capacity,
                    location = EXCLUDED.location,
                    area_code = EXCLUDED.area_code,
                    area_name = EXCLUDED.area_name,
                    road_segment_code = EXCLUDED.road_segment_code,
                    fill_level = EXCLUDED.fill_level,
                    status = EXCLUDED.status,
                    is_active = TRUE
                """
            ),
            waste_bin,
        )


def build_bins(roads: list[dict]) -> list[dict]:
    bins: list[dict] = []
    for road in roads:
        properties = road.get("properties") or {}
        coordinates = collect_line_coordinates(road.get("geometry") or {})
        if len(coordinates) < 2:
            continue

        spacing = spacing_for_road(properties)
        points = interpolate_points(coordinates, spacing)
        segment_code = str(properties.get("segment_code") or properties.get("osm_id") or properties.get("code") or "")
        area_code = clean_area_code(properties.get("gid") or properties.get("area_code") or properties.get("onoma"))
        area_name = str(properties.get("perigrafi") or properties.get("area_name") or "").strip() or None
        for index, point in enumerate(points, start=1):
            sequence_seed = len(bins) + index
            fill_level = deterministic_fill_level(segment_code, index)
            bins.append(
                {
                    "bin_code": f"BIN-{segment_code}-{index:03d}",
                    "type": "recycling" if sequence_seed % 4 == 0 else "mixed",
                    "capacity": 660 if spacing <= 60 else 1100,
                    "lng": point[0],
                    "lat": point[1],
                    "area_code": area_code,
                    "area_name": area_name,
                    "road_segment_code": segment_code,
                    "fill_level": fill_level,
                    "status": status_from_fill_level(fill_level),
                }
            )
    return bins


def spacing_for_road(properties: dict) -> int:
    area_name = str(properties.get("perigrafi") or "").upper()
    road_class = str(properties.get("fclass") or "").lower()
    if road_class in {"primary", "secondary", "tertiary"}:
        return 90
    if area_name in {"ΤΑΜΠΟΥΡΙΑ", "ΕΥΓΕΝΕΙΑ", "ΑΓ. ΓΙΩΡΓΗΣ"}:
        return 55
    if area_name in {"ΑΣΤΡΟ ΑΜΦΙΑΛΗΣ", "ΧΑΡΑΥΓΗ"}:
        return 130
    if area_name.startswith("Δ"):
        return 100
    return 75


def deterministic_fill_level(segment_code: str, index: int) -> int:
    seed = sum(ord(character) for character in segment_code) + index * 17
    return 20 + (seed % 80)


def status_from_fill_level(fill_level: int) -> str:
    if fill_level >= 90:
        return "full"
    if fill_level >= 72:
        return "needs_collection"
    return "normal"


def clean_area_code(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def collect_line_coordinates(geometry: dict) -> list[list[float]]:
    coordinates = geometry.get("coordinates") or []
    if geometry.get("type") == "LineString":
        return coordinates
    if geometry.get("type") == "MultiLineString":
        return [point for line in coordinates for point in line]
    return []


def interpolate_points(coordinates: list[list[float]], spacing_meters: int) -> list[tuple[float, float]]:
    length = polyline_length_meters(coordinates)
    if length < 25:
        return []

    count = max(1, int(length // spacing_meters))
    distances = [(index + 0.5) * (length / count) for index in range(count)]
    return [point_at_distance(coordinates, distance) for distance in distances]


def polyline_length_meters(coordinates: list[list[float]]) -> float:
    return sum(distance_meters(coordinates[index - 1], coordinates[index]) for index in range(1, len(coordinates)))


def point_at_distance(coordinates: list[list[float]], target_distance: float) -> tuple[float, float]:
    walked = 0.0
    for index in range(1, len(coordinates)):
        start = coordinates[index - 1]
        end = coordinates[index]
        segment_length = distance_meters(start, end)
        if walked + segment_length >= target_distance:
            ratio = 0 if segment_length == 0 else (target_distance - walked) / segment_length
            return (
                start[0] + (end[0] - start[0]) * ratio,
                start[1] + (end[1] - start[1]) * ratio,
            )
        walked += segment_length
    return coordinates[-1][0], coordinates[-1][1]


def distance_meters(first: list[float], second: list[float]) -> float:
    lng1, lat1 = first
    lng2, lat2 = second
    lat_avg = math.radians((lat1 + lat2) / 2)
    meters_per_degree_lat = 111_320
    meters_per_degree_lng = 111_320 * math.cos(lat_avg)
    dx = (lng2 - lng1) * meters_per_degree_lng
    dy = (lat2 - lat1) * meters_per_degree_lat
    return math.hypot(dx, dy)


if __name__ == "__main__":
    main()
