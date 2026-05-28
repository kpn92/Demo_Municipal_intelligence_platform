from datetime import date
from math import atan2
from typing import Any

from sqlalchemy.orm import Session

from app.mapping.gis_layers import get_gis_layers, get_layer_catalog
from app.services.daily_assignment_service import get_daily_assignment_plan_by_date


def build_cleaning_map_overview(db: Session, assignment_date: date) -> dict[str, Any]:
    assignments = get_daily_assignment_plan_by_date(db, assignment_date)
    task_features = []
    route_features = []
    zone_features = []
    road_features = []

    for assignment in assignments:
        task_points = []

        for assignment_item in assignment.assignment_items:
            item = assignment_item.sector_item
            if item.latitude is None or item.longitude is None:
                continue

            coordinate = [item.longitude, item.latitude]
            task_points.append(
                {
                    "coordinate": coordinate,
                    "priority": item.priority,
                    "item_type": item.item_type,
                    "name": item.name,
                },
            )
            task_features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": coordinate,
                    },
                    "properties": {
                        "id": item.id,
                        "assignment_id": assignment.id,
                        "sector_id": assignment.sector_id,
                        "sector_name": assignment.sector.name,
                        "employee_name": f"{assignment.employee.first_name} {assignment.employee.last_name}",
                        "name": item.name,
                        "address": item.address,
                        "item_type": item.item_type,
                        "priority": item.priority,
                        "estimated_minutes": item.estimated_minutes or 30,
                        "status": _status_for_priority(item.priority),
                    },
                },
            )

        if len(task_points) >= 2:
            route_features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [point["coordinate"] for point in task_points],
                    },
                    "properties": {
                        "assignment_id": assignment.id,
                        "sector_id": assignment.sector_id,
                        "sector_name": assignment.sector.name,
                        "employee_name": f"{assignment.employee.first_name} {assignment.employee.last_name}",
                        "status": assignment.status,
                    },
                },
            )
            road_features.extend(_build_demo_road_segments(assignment, task_points))

        zone_polygon = _build_zone_polygon([point["coordinate"] for point in task_points])
        if zone_polygon:
            zone_features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [zone_polygon],
                    },
                    "properties": {
                        "sector_id": assignment.sector_id,
                        "sector_name": assignment.sector.name,
                        "assignment_id": assignment.id,
                        "employee_name": f"{assignment.employee.first_name} {assignment.employee.last_name}",
                        "workload_minutes": sum(
                            (assignment_item.sector_item.estimated_minutes or 30)
                            for assignment_item in assignment.assignment_items
                        ),
                    },
                },
            )

    return {
        "assignment_date": assignment_date.isoformat(),
        "layer_catalog": get_layer_catalog(),
        **get_gis_layers(db, assignment_date),
        "zones": _feature_collection(zone_features),
        "road_segments": _feature_collection(road_features),
        "tasks": _feature_collection(task_features),
        "routes": _feature_collection(route_features),
        "vehicles": _feature_collection([]),
    }


def _feature_collection(features: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "features": features,
    }


def _status_for_priority(priority: int) -> str:
    if priority == 1:
        return "urgent"
    if priority == 2:
        return "pending"
    return "assigned"


def _build_zone_polygon(points: list[list[float]]) -> list[list[float]] | None:
    if len(points) < 3:
        return None

    lng_avg = sum(point[0] for point in points) / len(points)
    lat_avg = sum(point[1] for point in points) / len(points)
    sorted_points = sorted(
        points,
        key=lambda point: atan2(point[1] - lat_avg, point[0] - lng_avg),
    )
    return sorted_points + [sorted_points[0]]


def _build_demo_road_segments(assignment: Any, task_points: list[dict[str, Any]]) -> list[dict[str, Any]]:
    segments = []

    for index, current_point in enumerate(task_points[:-1]):
        next_point = task_points[index + 1]
        priority = min(current_point["priority"], next_point["priority"])
        segments.append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        current_point["coordinate"],
                        next_point["coordinate"],
                    ],
                },
                "properties": {
                    "id": f"{assignment.id}-{index + 1}",
                    "assignment_id": assignment.id,
                    "sector_id": assignment.sector_id,
                    "sector_name": assignment.sector.name,
                    "status": _status_for_priority(priority),
                    "priority": priority,
                    "source": "demo_from_assignment_points",
                },
            },
        )

    return segments
