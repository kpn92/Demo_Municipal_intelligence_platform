from pathlib import Path
import json
import struct
from typing import Any

from sqlalchemy import create_engine, text

from app.core.config import settings


PROJECT_ROOT = Path(__file__).resolve().parents[2]
EXPORT_DIR = PROJECT_ROOT / "data" / "gis_exports"

LAYERS = [
    {
        "id": "buildings_2d",
        "source": PROJECT_ROOT
        / "data"
        / "gis"
        / "basemap"
        / "municipal_boundaries"
        / "Area_Buildings_Keratsini_Drapetsona.shp",
        "name": "Buildings 2D",
        "clip_extract_type": 3,
    },
    {
        "id": "buildings_25d",
        "source": PROJECT_ROOT
        / "data"
        / "gis"
        / "basemap"
        / "municipal_boundaries"
        / "Area_Buildings_Keratsini_Drapetsona.shp",
        "name": "Buildings 2.5D",
        "clip_extract_type": 3,
    },
    {
        "id": "cleaning_areas",
        "source": PROJECT_ROOT
        / "data"
        / "gis"
        / "basemap"
        / "municipal_boundaries"
        / "Area_Buildings_Keratsini_Drapetsona.shp",
        "name": "Cleaning areas",
        "group_by": "ktim_tomea",
        "clip_extract_type": 3,
    },
    {
        "id": "line_roads",
        "source": PROJECT_ROOT
        / "data"
        / "gis"
        / "basemap"
        / "roads"
        / "Line_Roads_OSM_in_areas.shp",
        "name": "Line roads",
        "clip_extract_type": 2,
    },
    {
        "id": "polygon_roads",
        "source": PROJECT_ROOT
        / "data"
        / "gis"
        / "basemap"
        / "roads"
        / "Polygon_roads.shp",
        "name": "Polygon roads",
        "clip_extract_type": 3,
    },
    {
        "id": "land_use_zones",
        "source": PROJECT_ROOT
        / "data"
        / "gis"
        / "urban_planning"
        / "land_use_zones"
        / "ydom_pol_chriseis_gis.shp",
        "name": "Land use zones",
        "clip_extract_type": 3,
    },
]


def main() -> None:
    engine = create_engine(settings.database_url)
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    with engine.connect() as connection:
        for layer in LAYERS:
            geojson = export_layer(connection, layer)
            target = EXPORT_DIR / f"{layer['id']}.geojson"
            target.write_text(
                json.dumps(geojson, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Exported {len(geojson['features'])} feature(s) to {target}")


def export_layer(connection: Any, layer: dict[str, Any]) -> dict[str, Any]:
    features = read_shapefile(layer["source"])
    if layer.get("group_by"):
        return export_grouped_layer(connection, layer, features)

    output_features = []

    for feature in features:
        if not include_feature(feature, layer):
            continue

        geometry = transform_geometry(
            connection,
            feature["wkt"],
            clip_to_boundary=layer["id"] in {"buildings_2d", "buildings_25d"},
            extract_type=layer.get("clip_extract_type", 2),
        )
        if geometry is None:
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": feature["properties"],
            }
        )

    if layer["id"] == "line_roads":
        assign_unique_line_road_segment_codes(output_features)

    return {
        "type": "FeatureCollection",
        "name": layer["id"],
        "crs": {
            "type": "name",
            "properties": {"name": "EPSG:4326"},
        },
        "features": output_features,
    }


def assign_unique_line_road_segment_codes(features: list[dict[str, Any]]) -> None:
    base_codes: list[str] = []
    counts: dict[str, int] = {}
    for index, feature in enumerate(features, start=1):
        properties = feature.get("properties") or {}
        base_code = str(
            properties.get("osm_id")
            or properties.get("code")
            or properties.get("gid")
            or f"road-{index}"
        ).strip()
        if not base_code:
            base_code = f"road-{index}"
        base_codes.append(base_code)
        counts[base_code] = counts.get(base_code, 0) + 1

    occurrences: dict[str, int] = {}
    for feature, base_code in zip(features, base_codes):
        properties = feature.setdefault("properties", {})
        occurrences[base_code] = occurrences.get(base_code, 0) + 1
        if counts[base_code] == 1 or occurrences[base_code] == 1:
            properties["segment_code"] = base_code
        else:
            properties["segment_code"] = f"{base_code}-{occurrences[base_code]}"


def export_grouped_layer(
    connection: Any,
    layer: dict[str, Any],
    features: list[dict[str, Any]],
) -> dict[str, Any]:
    group_field = layer["group_by"]
    groups: dict[str, list[dict[str, Any]]] = {}

    for feature in features:
        key = str(feature["properties"].get(group_field) or "").strip()
        if not key:
            continue
        groups.setdefault(key, []).append(feature)

    output_features = []
    for index, key in enumerate(sorted(groups, key=sort_group_key), start=1):
        geometry = transform_grouped_geometry(
            connection,
            [feature["wkt"] for feature in groups[key]],
            extract_type=layer.get("clip_extract_type", 3),
        )
        if geometry is None:
            continue

        output_features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": {
                    group_field: key,
                    "name": f"Π{index}",
                    "area_code": f"P{index}",
                    "feature_count": len(groups[key]),
                    "source_file": layer["source"].name,
                },
            }
        )

    return {
        "type": "FeatureCollection",
        "name": layer["id"],
        "crs": {
            "type": "name",
            "properties": {"name": "EPSG:4326"},
        },
        "features": output_features,
    }


def sort_group_key(value: str) -> tuple[int, str]:
    try:
        return (int(value), value)
    except ValueError:
        return (9999, value)


def include_feature(feature: dict[str, Any], layer: dict[str, Any]) -> bool:
    filters = layer.get("property_filter")
    if not filters:
        return True

    properties = feature["properties"]
    return all(str(properties.get(key)) in values for key, values in filters.items())


def transform_grouped_geometry(
    connection: Any,
    wkts: list[str],
    extract_type: int = 3,
) -> dict[str, Any] | None:
    collection_wkt = "GEOMETRYCOLLECTION(" + ", ".join(wkts) + ")"
    return connection.execute(
        text(
            """
            WITH source_geom AS (
                SELECT ST_UnaryUnion(
                    ST_Transform(ST_GeomFromText(:wkt, 2100), 4326)
                ) AS geom
            ),
            clipped AS (
                SELECT ST_CollectionExtract(
                    ST_Intersection(source_geom.geom, boundary.geom),
                    :extract_type
                ) AS geom
                FROM source_geom
                CROSS JOIN (
                    SELECT ST_UnaryUnion(ST_Collect(geom)) AS geom
                    FROM municipality_boundary
                    WHERE is_active IS TRUE
                ) boundary
                WHERE ST_Intersects(source_geom.geom, boundary.geom)
            )
            SELECT
                CASE
                    WHEN geom IS NULL OR ST_IsEmpty(geom) THEN NULL
                    ELSE ST_AsGeoJSON(ST_ForcePolygonCCW(geom), 9)::json
                END
            FROM clipped
            """
        ),
        {"wkt": collection_wkt, "extract_type": extract_type},
    ).scalar_one_or_none()


def transform_geometry(
    connection: Any,
    wkt: str,
    clip_to_boundary: bool = False,
    extract_type: int = 2,
) -> dict[str, Any] | None:
    if not clip_to_boundary:
        return connection.execute(
            text(
                """
                SELECT ST_AsGeoJSON(
                    ST_ForcePolygonCCW(
                        ST_CollectionExtract(
                            ST_MakeValid(ST_Transform(ST_GeomFromText(:wkt, 2100), 4326)),
                            :extract_type
                        )
                    ),
                    9
                )::json
                """
            ),
            {"wkt": wkt, "extract_type": extract_type},
        ).scalar_one()

    return connection.execute(
        text(
            """
            WITH source_geom AS (
                SELECT ST_MakeValid(ST_Transform(ST_GeomFromText(:wkt, 2100), 4326)) AS geom
            ),
            clipped AS (
                SELECT ST_CollectionExtract(
                    ST_Intersection(source_geom.geom, boundary.geom),
                    :extract_type
                ) AS geom
                FROM source_geom
                CROSS JOIN (
                    SELECT ST_UnaryUnion(ST_Collect(geom)) AS geom
                    FROM municipality_boundary
                    WHERE is_active IS TRUE
                ) boundary
                WHERE ST_Intersects(source_geom.geom, boundary.geom)
            )
            SELECT
                CASE
                    WHEN geom IS NULL OR ST_IsEmpty(geom) THEN NULL
                    ELSE ST_AsGeoJSON(ST_ForcePolygonCCW(geom), 9)::json
                END
            FROM clipped
            """
        ),
        {"wkt": wkt, "extract_type": extract_type},
    ).scalar_one_or_none()


def read_shapefile(path: Path) -> list[dict[str, Any]]:
    geometries = read_shp(path)
    records = read_dbf(path.with_suffix(".dbf"))

    return [
        {
            "wkt": geometry["wkt"],
            "properties": {
                **(records[index] if index < len(records) else {}),
                "source_file": path.name,
            },
        }
        for index, geometry in enumerate(geometries)
        if geometry["wkt"] is not None
    ]


def read_shp(path: Path) -> list[dict[str, str | None]]:
    data = path.read_bytes()
    offset = 100
    geometries = []

    while offset < len(data):
        _, content_length_words = struct.unpack(">2i", data[offset : offset + 8])
        content_length = content_length_words * 2
        content = data[offset + 8 : offset + 8 + content_length]
        shape_type = struct.unpack("<i", content[:4])[0]

        if shape_type == 3:
            geometries.append({"wkt": read_polyline_wkt(content)})
        elif shape_type == 5:
            geometries.append({"wkt": read_polygon_wkt(content)})
        else:
            geometries.append({"wkt": None})

        offset += 8 + content_length

    return geometries


def read_polyline_wkt(content: bytes) -> str:
    num_parts, num_points = struct.unpack("<2i", content[36:44])
    parts_offset = 44
    points_offset = parts_offset + (num_parts * 4)
    parts = list(struct.unpack(f"<{num_parts}i", content[parts_offset:points_offset]))
    points = [
        struct.unpack("<2d", content[points_offset + index * 16 : points_offset + (index + 1) * 16])
        for index in range(num_points)
    ]
    lines = []

    for index, start in enumerate(parts):
        end = parts[index + 1] if index + 1 < len(parts) else len(points)
        lines.append(points[start:end])

    if len(lines) == 1:
        return "LINESTRING(" + coordinate_text(lines[0]) + ")"

    return "MULTILINESTRING(" + ", ".join(f"({coordinate_text(line)})" for line in lines) + ")"


def read_polygon_wkt(content: bytes) -> str:
    num_parts, num_points = struct.unpack("<2i", content[36:44])
    parts_offset = 44
    points_offset = parts_offset + (num_parts * 4)
    parts = list(struct.unpack(f"<{num_parts}i", content[parts_offset:points_offset]))
    points = [
        struct.unpack("<2d", content[points_offset + index * 16 : points_offset + (index + 1) * 16])
        for index in range(num_points)
    ]
    rings = []

    for index, start in enumerate(parts):
        end = parts[index + 1] if index + 1 < len(parts) else len(points)
        ring = points[start:end]
        if ring and ring[0] != ring[-1]:
            ring = ring + [ring[0]]
        rings.append(ring)

    polygons = group_polygon_rings(rings)
    if len(polygons) == 1:
        return "POLYGON(" + polygon_rings_text(polygons[0]) + ")"

    return "MULTIPOLYGON(" + ", ".join(f"({polygon_rings_text(polygon)})" for polygon in polygons) + ")"


def group_polygon_rings(
    rings: list[list[tuple[float, float]]],
) -> list[list[list[tuple[float, float]]]]:
    if len(rings) <= 1:
        return [[ring] for ring in rings]

    ring_areas = [abs(signed_ring_area(ring)) for ring in rings]
    containers: list[list[int]] = []

    for index, ring in enumerate(rings):
        point = first_distinct_point(ring)
        containers.append(
            [
                candidate_index
                for candidate_index, candidate in enumerate(rings)
                if candidate_index != index and ring_areas[candidate_index] > ring_areas[index] and point_in_ring(point, candidate)
            ]
        )

    shells = [index for index, contained_by in enumerate(containers) if len(contained_by) % 2 == 0]
    if not shells:
        shells = [max(range(len(rings)), key=lambda index: ring_areas[index])]

    polygons: dict[int, list[list[tuple[float, float]]]] = {
        shell_index: [rings[shell_index]]
        for shell_index in shells
    }

    for index, contained_by in enumerate(containers):
        if index in polygons:
            continue

        shell_candidates = [candidate for candidate in contained_by if candidate in polygons]
        if not shell_candidates:
            polygons.setdefault(index, [rings[index]])
            continue

        parent_shell = min(shell_candidates, key=lambda candidate: ring_areas[candidate])
        polygons[parent_shell].append(rings[index])

    return list(polygons.values())


def signed_ring_area(ring: list[tuple[float, float]]) -> float:
    return sum(
        (x1 * y2) - (x2 * y1)
        for (x1, y1), (x2, y2) in zip(ring, ring[1:])
    ) / 2


def first_distinct_point(ring: list[tuple[float, float]]) -> tuple[float, float]:
    if not ring:
        return (0, 0)
    return next((point for point in ring[1:] if point != ring[0]), ring[0])


def point_in_ring(point: tuple[float, float], ring: list[tuple[float, float]]) -> bool:
    x, y = point
    inside = False

    for (x1, y1), (x2, y2) in zip(ring, ring[1:]):
        if (y1 > y) == (y2 > y):
            continue
        intersection_x = ((x2 - x1) * (y - y1) / (y2 - y1)) + x1
        if x < intersection_x:
            inside = not inside

    return inside


def polygon_rings_text(rings: list[list[tuple[float, float]]]) -> str:
    return ", ".join(f"({coordinate_text(ring)})" for ring in rings)


def coordinate_text(points: list[tuple[float, float]]) -> str:
    return ", ".join(f"{x} {y}" for x, y in points)


def read_dbf(path: Path) -> list[dict[str, Any]]:
    data = path.read_bytes()
    num_records, header_length, record_length = struct.unpack("<xxxxIHH20x", data[:32])
    fields = []
    offset = 32

    while data[offset] != 0x0D:
        descriptor = data[offset : offset + 32]
        name = descriptor[:11].split(b"\0", 1)[0].decode("ascii", errors="ignore")
        field_type = chr(descriptor[11])
        length = descriptor[16]
        decimals = descriptor[17]
        fields.append((name, field_type, length, decimals))
        offset += 32

    records = []
    record_offset = header_length

    for _ in range(num_records):
        raw_record = data[record_offset : record_offset + record_length]
        record_offset += record_length

        if raw_record[:1] == b"*":
            continue

        field_offset = 1
        record = {}

        for name, field_type, length, decimals in fields:
            raw_value = raw_record[field_offset : field_offset + length]
            field_offset += length
            text_value = raw_value.decode("utf-8", errors="ignore").replace("\x00", "").strip()
            record[name] = parse_dbf_value(text_value, field_type, decimals)

        records.append(record)

    return records


def parse_dbf_value(value: str, field_type: str, decimals: int) -> Any:
    if value == "":
        return None
    if field_type == "N":
        try:
            return float(value) if decimals else int(value)
        except ValueError:
            return value
    return value


if __name__ == "__main__":
    main()
