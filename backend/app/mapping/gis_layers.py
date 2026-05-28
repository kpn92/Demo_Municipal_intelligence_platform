from datetime import date
from typing import Any

from sqlalchemy import text
from sqlalchemy.orm import Session


def get_gis_layers(db: Session, assignment_date: date) -> dict[str, Any]:
    return {
        "municipality_boundary": get_municipality_boundary_layer(db),
        "cleaning_zones_gis": _feature_collection(
            db,
            """
            SELECT
                id,
                code,
                name,
                description,
                priority,
                ST_AsGeoJSON(geom)::json AS geometry
            FROM cleaning_zone
            WHERE is_active IS TRUE
            ORDER BY priority, id
            """,
        ),
        "road_segments_gis": _feature_collection(
            db,
            """
            SELECT
                rs.id,
                rs.code,
                rs.name,
                rs.road_type,
                rs.default_priority,
                rs.cleaning_zone_id,
                cz.name AS cleaning_zone_name,
                COALESCE(latest.status, 'pending') AS status,
                COALESCE(latest.priority, rs.default_priority) AS priority,
                ST_AsGeoJSON(rs.geom)::json AS geometry
            FROM road_segment rs
            LEFT JOIN cleaning_zone cz ON cz.id = rs.cleaning_zone_id
            LEFT JOIN LATERAL (
                SELECT status, priority
                FROM cleaning_status_event cse
                WHERE cse.target_type = 'road_segment'
                  AND cse.target_id = rs.id
                  AND cse.event_date <= :assignment_date
                ORDER BY cse.event_date DESC, cse.created_at DESC, cse.id DESC
                LIMIT 1
            ) latest ON TRUE
            WHERE rs.is_active IS TRUE
            ORDER BY COALESCE(latest.priority, rs.default_priority), rs.id
            """,
            {"assignment_date": assignment_date},
        ),
        "map_assets": _feature_collection(
            db,
            """
            SELECT
                ma.id,
                ma.code,
                ma.name,
                ma.asset_type,
                ma.address,
                ma.priority,
                ma.notes,
                ma.cleaning_zone_id,
                cz.name AS cleaning_zone_name,
                COALESCE(latest.status, 'pending') AS status,
                COALESCE(latest.priority, ma.priority) AS status_priority,
                ST_AsGeoJSON(ma.geom)::json AS geometry
            FROM map_asset ma
            LEFT JOIN cleaning_zone cz ON cz.id = ma.cleaning_zone_id
            LEFT JOIN LATERAL (
                SELECT status, priority
                FROM cleaning_status_event cse
                WHERE cse.target_type = 'map_asset'
                  AND cse.target_id = ma.id
                  AND cse.event_date <= :assignment_date
                ORDER BY cse.event_date DESC, cse.created_at DESC, cse.id DESC
                LIMIT 1
            ) latest ON TRUE
            WHERE ma.is_active IS TRUE
            ORDER BY COALESCE(latest.priority, ma.priority), ma.id
            """,
            {"assignment_date": assignment_date},
        ),
    }


def get_municipality_boundary_layer(db: Session) -> dict[str, Any]:
    return _feature_collection(
        db,
        """
        SELECT
            id,
            code,
            name,
            description,
            ST_AsGeoJSON(geom)::json AS geometry
        FROM municipality_boundary
        WHERE is_active IS TRUE
        ORDER BY id
        """,
    )


def get_layer_catalog() -> list[dict[str, Any]]:
    return [
        {
            "id": "municipality_boundary",
            "label": "Όρια δήμου",
            "enabled_by_default": True,
            "geometry_type": "MultiPolygon",
        },
        {
            "id": "cleaning_zones_gis",
            "label": "Περιοχές καθαριότητας",
            "enabled_by_default": True,
            "geometry_type": "MultiPolygon",
        },
        {
            "id": "road_segments_gis",
            "label": "Δρόμοι",
            "enabled_by_default": True,
            "geometry_type": "LineString",
        },
        {
            "id": "map_assets",
            "label": "Δημόσια περιουσία / σημεία",
            "enabled_by_default": True,
            "geometry_type": "Geometry",
        },
        {
            "id": "assignment_tasks",
            "label": "Αναθέσεις καθαριστών",
            "enabled_by_default": True,
            "geometry_type": "Point",
        },
    ]


def _feature_collection(
    db: Session,
    sql: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rows = db.execute(text(sql), params or {}).mappings().all()
    features = []

    for row in rows:
        row_data = dict(row)
        geometry = row_data.pop("geometry")
        features.append(
            {
                "type": "Feature",
                "geometry": geometry,
                "properties": row_data,
            },
        )

    return {
        "type": "FeatureCollection",
        "features": features,
    }
