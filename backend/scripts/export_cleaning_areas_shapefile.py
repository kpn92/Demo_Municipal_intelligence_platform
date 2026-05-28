from __future__ import annotations

from datetime import date
from pathlib import Path
import json
import struct

from sqlalchemy import create_engine

from app.core.config import settings
from scripts.export_gis_context_layers import (
    read_shapefile,
    sort_group_key,
    transform_grouped_geometry,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SOURCE_PATH = (
    PROJECT_ROOT
    / "data"
    / "gis"
    / "basemap"
    / "municipal_boundaries"
    / "Area_Buildings_Keratsini_Drapetsona.shp"
)
TARGET_DIR = (
    PROJECT_ROOT
    / "data"
    / "gis"
    / "urban_planning"
    / "cleaning_areas"
)
TARGET_BASENAME = "cleaning_areas"
GROUP_FIELD = "ktim_tomea"
PRJ_WGS84 = (
    'GEOGCS["WGS 84",DATUM["WGS_1984",'
    'SPHEROID["WGS 84",6378137,298.257223563]],'
    'PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]'
)


def main() -> None:
    engine = create_engine(settings.database_url)
    features = read_shapefile(SOURCE_PATH)
    grouped = group_features(features, GROUP_FIELD)

    TARGET_DIR.mkdir(parents=True, exist_ok=True)

    with engine.connect() as connection:
        records = []
        for index, key in enumerate(sorted(grouped, key=sort_group_key), start=1):
            geometry = transform_grouped_geometry(
                connection,
                [feature["wkt"] for feature in grouped[key]],
                extract_type=3,
            )
            if geometry is None:
                continue

            records.append(
                {
                    "geometry": geometry,
                    "properties": {
                        "ktim_tomea": str(key),
                        "name": f"P{index}",
                        "label": f"Π{index}",
                        "area_code": f"P{index}",
                        "feature_cnt": len(grouped[key]),
                        "src_file": SOURCE_PATH.name,
                        "created_on": date.today().isoformat(),
                    },
                }
            )

    write_polygon_shapefile(TARGET_DIR / TARGET_BASENAME, records)
    print(f"Exported {len(records)} cleaning area polygon(s) to {TARGET_DIR}")


def group_features(features: list[dict], group_field: str) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = {}
    for feature in features:
        key = str(feature["properties"].get(group_field) or "").strip()
        if not key:
            continue
        groups.setdefault(key, []).append(feature)
    return groups


def write_polygon_shapefile(base_path: Path, records: list[dict]) -> None:
    shape_records = [geometry_to_shape_record(record["geometry"]) for record in records]

    shp_bytes, shx_bytes = build_shp_and_shx(shape_records)
    dbf_bytes = build_dbf(records)

    base_path.with_suffix(".shp").write_bytes(shp_bytes)
    base_path.with_suffix(".shx").write_bytes(shx_bytes)
    base_path.with_suffix(".dbf").write_bytes(dbf_bytes)
    base_path.with_suffix(".prj").write_text(PRJ_WGS84, encoding="ascii")
    base_path.with_suffix(".cpg").write_text("UTF-8", encoding="ascii")
    base_path.with_suffix(".geojson").write_text(
        json.dumps(
            {
                "type": "FeatureCollection",
                "name": TARGET_BASENAME,
                "features": [
                    {
                        "type": "Feature",
                        "geometry": record["geometry"],
                        "properties": record["properties"],
                    }
                    for record in records
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def geometry_to_shape_record(geometry: dict) -> dict:
    shape_type = geometry.get("type")
    if shape_type not in {"Polygon", "MultiPolygon"}:
        raise ValueError(f"Unsupported geometry type for shapefile export: {shape_type}")

    parts: list[int] = []
    points: list[tuple[float, float]] = []

    polygons = geometry["coordinates"] if shape_type == "MultiPolygon" else [geometry["coordinates"]]

    for polygon in polygons:
        for ring in polygon:
            if not ring:
                continue
            cleaned_ring = [(float(x), float(y)) for x, y in ring]
            if cleaned_ring[0] != cleaned_ring[-1]:
                cleaned_ring.append(cleaned_ring[0])
            parts.append(len(points))
            points.extend(cleaned_ring)

    xs = [point[0] for point in points]
    ys = [point[1] for point in points]

    return {
        "shape_type": 5,
        "bbox": (min(xs), min(ys), max(xs), max(ys)),
        "parts": parts,
        "points": points,
    }


def build_shp_and_shx(shape_records: list[dict]) -> tuple[bytes, bytes]:
    shp_records = []
    shx_records = []
    shp_offset_words = 50

    for index, record in enumerate(shape_records, start=1):
        content = build_polygon_record_content(record)
        content_length_words = len(content) // 2
        shp_records.append(
            struct.pack(">2i", index, content_length_words) + content
        )
        shx_records.append(struct.pack(">2i", shp_offset_words, content_length_words))
        shp_offset_words += 4 + content_length_words

    bbox = combine_bbox(shape_records)
    shp_header = build_main_header(5, bbox, 50 + sum(len(r) for r in shp_records) // 2)
    shx_header = build_main_header(5, bbox, 50 + len(shx_records) * 4)
    return shp_header + b"".join(shp_records), shx_header + b"".join(shx_records)


def build_polygon_record_content(record: dict) -> bytes:
    xmin, ymin, xmax, ymax = record["bbox"]
    parts = record["parts"]
    points = record["points"]

    content = bytearray()
    content.extend(struct.pack("<i", record["shape_type"]))
    content.extend(struct.pack("<4d", xmin, ymin, xmax, ymax))
    content.extend(struct.pack("<2i", len(parts), len(points)))
    content.extend(struct.pack(f"<{len(parts)}i", *parts))

    for x, y in points:
        content.extend(struct.pack("<2d", x, y))

    return bytes(content)


def combine_bbox(shape_records: list[dict]) -> tuple[float, float, float, float]:
    xmins = [record["bbox"][0] for record in shape_records]
    ymins = [record["bbox"][1] for record in shape_records]
    xmaxs = [record["bbox"][2] for record in shape_records]
    ymaxs = [record["bbox"][3] for record in shape_records]
    return min(xmins), min(ymins), max(xmaxs), max(ymaxs)


def build_main_header(shape_type: int, bbox: tuple[float, float, float, float], file_length_words: int) -> bytes:
    xmin, ymin, xmax, ymax = bbox
    header = bytearray(100)
    struct.pack_into(">i", header, 0, 9994)
    struct.pack_into(">i", header, 24, file_length_words)
    struct.pack_into("<i", header, 28, 1000)
    struct.pack_into("<i", header, 32, shape_type)
    struct.pack_into("<4d", header, 36, xmin, ymin, xmax, ymax)
    struct.pack_into("<4d", header, 68, 0.0, 0.0, 0.0, 0.0)
    return bytes(header)


def build_dbf(records: list[dict]) -> bytes:
    fields = [
        ("KTIM_TOMEA", "C", 10, 0),
        ("NAME", "C", 10, 0),
        ("LABEL", "C", 10, 0),
        ("AREA_CODE", "C", 10, 0),
        ("FEATURE_CNT", "N", 8, 0),
        ("SRC_FILE", "C", 40, 0),
        ("CREATED_ON", "C", 10, 0),
    ]

    num_records = len(records)
    header_length = 32 + len(fields) * 32 + 1
    record_length = 1 + sum(field[2] for field in fields)
    today = date.today()

    data = bytearray()
    data.extend(struct.pack("<BBBBIHH20x", 0x03, today.year - 1900, today.month, today.day, num_records, header_length, record_length))

    for name, field_type, length, decimals in fields:
        descriptor = bytearray(32)
        descriptor[:11] = name.encode("ascii")[:11].ljust(11, b"\x00")
        descriptor[11] = ord(field_type)
        descriptor[16] = length
        descriptor[17] = decimals
        data.extend(descriptor)

    data.append(0x0D)

    for record in records:
        row = bytearray()
        row.extend(b" ")
        props = record["properties"]
        for name, field_type, length, _ in fields:
            value = props[field_name_to_property_key(name)]
            row.extend(format_dbf_value(value, field_type, length))
        data.extend(row)

    data.append(0x1A)
    return bytes(data)


def field_name_to_property_key(field_name: str) -> str:
    return {
        "KTIM_TOMEA": "ktim_tomea",
        "NAME": "name",
        "LABEL": "label",
        "AREA_CODE": "area_code",
        "FEATURE_CNT": "feature_cnt",
        "SRC_FILE": "src_file",
        "CREATED_ON": "created_on",
    }[field_name]


def format_dbf_value(value: object, field_type: str, length: int) -> bytes:
    if field_type == "N":
        text = str(int(value)).rjust(length)
        return text.encode("ascii")

    text = str(value)
    encoded = text.encode("utf-8")[:length]
    return encoded.ljust(length, b" ")


if __name__ == "__main__":
    main()
