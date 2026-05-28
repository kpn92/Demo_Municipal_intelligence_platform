from pathlib import Path
import json
import struct

from sqlalchemy import create_engine, text

from app.core.config import settings


SHAPEFILE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "gis"
    / "municipalities"
    / "municipality_keratsini_drapetsona"
    / "adm_pol_kallikratikos_dimos_ker_drap.shp"
)
GEOJSON_EXPORT_PATH = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "gis_exports"
    / "municipality_boundary.geojson"
)


def main() -> None:
    polygons = read_polygon_shapefile(SHAPEFILE_PATH)
    if not polygons:
        raise RuntimeError(f"No polygons found in {SHAPEFILE_PATH}")

    multipolygon_wkt = to_multipolygon_wkt(polygons)
    engine = create_engine(settings.database_url)

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
        connection.execute(text("DELETE FROM municipality_boundary"))
        connection.execute(
            text(
                """
                INSERT INTO municipality_boundary
                    (code, name, description, geom, is_active)
                VALUES
                    (
                        :code,
                        :name,
                        :description,
                        ST_Multi(ST_Transform(ST_GeomFromText(:wkt, 2100), 4326)),
                        true
                    )
                """
            ),
            {
                "code": "keratsini_drapetsona",
                "name": "Δήμος Κερατσινίου - Δραπετσώνας",
                "description": "Πραγματικό όριο δήμου από shapefile ΕΓΣΑ87 / EPSG:2100.",
                "wkt": multipolygon_wkt,
            },
        )
        geojson = connection.execute(
            text(
                """
                SELECT json_build_object(
                    'type', 'FeatureCollection',
                    'name', 'municipality_boundary',
                    'crs', json_build_object(
                        'type', 'name',
                        'properties', json_build_object('name', 'EPSG:4326')
                    ),
                    'features', COALESCE(json_agg(
                        json_build_object(
                            'type', 'Feature',
                            'geometry', ST_AsGeoJSON(geom)::json,
                            'properties', json_build_object(
                                'id', id,
                                'code', code,
                                'name', name,
                                'description', description
                            )
                        )
                    ), '[]'::json)
                ) AS geojson
                FROM municipality_boundary
                WHERE is_active IS TRUE
                """
            )
        ).scalar_one()

    write_geojson_export(geojson)
    print(f"Imported {len(polygons)} polygon(s) from {SHAPEFILE_PATH}")
    print(f"Exported GeoJSON to {GEOJSON_EXPORT_PATH}")


def read_polygon_shapefile(path: Path) -> list[list[list[tuple[float, float]]]]:
    data = path.read_bytes()
    offset = 100
    polygons = []

    while offset < len(data):
        _, content_length_words = struct.unpack(">2i", data[offset : offset + 8])
        content_length = content_length_words * 2
        content = data[offset + 8 : offset + 8 + content_length]
        shape_type = struct.unpack("<i", content[:4])[0]

        if shape_type == 5:
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

            polygons.append(rings)

        offset += 8 + content_length

    return polygons


def to_multipolygon_wkt(polygons: list[list[list[tuple[float, float]]]]) -> str:
    polygon_texts = []

    for rings in polygons:
        ring_texts = []
        for ring in rings:
            ring_texts.append(
                "(" + ", ".join(f"{x} {y}" for x, y in ring) + ")"
            )
        polygon_texts.append("(" + ", ".join(ring_texts) + ")")

    return "MULTIPOLYGON(" + ", ".join(polygon_texts) + ")"


def write_geojson_export(geojson: dict) -> None:
    GEOJSON_EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    GEOJSON_EXPORT_PATH.write_text(
        json.dumps(geojson, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
