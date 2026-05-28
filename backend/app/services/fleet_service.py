from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.collection_route import CollectionRoute
from app.schemas.fleet import FleetAssignmentCreate, FleetAssignmentRead


def _route_to_read(route: CollectionRoute) -> FleetAssignmentRead:
    return FleetAssignmentRead(
        id=route.id,
        assignment_date=route.route_date,
        status=route.status,
        vehicle_frontend_id=route.vehicle_frontend_id,
        vehicle_plate=route.vehicle_plate,
        vehicle_name=route.vehicle_name,
        vehicle_id=route.vehicle_id,
        bin_type=route.bin_type,
        area_codes=route.area_codes or [],
        area_names=route.area_names or [],
        excluded_bin_ids=route.excluded_bin_ids or [],
        total_bins=route.total_bins or 0,
        estimated_minutes=route.estimated_duration_min or 0,
        estimated_km=float(route.estimated_km or 0),
        total_trips=route.total_trips or 1,
        red_count=route.red_count or 0,
        yellow_count=route.yellow_count or 0,
        green_count=route.green_count or 0,
        road_coordinates=route.road_coordinates,
    )


def save_fleet_assignment(db: Session, data: FleetAssignmentCreate) -> FleetAssignmentRead:
    vehicle_id: int | None = None
    if data.vehicle_plate:
        row = db.execute(
            text("SELECT id FROM vehicle WHERE plate_number = :plate LIMIT 1"),
            {"plate": data.vehicle_plate},
        ).fetchone()
        if row:
            vehicle_id = row[0]

    # Delete any existing assignment for the same vehicle+date (upsert)
    existing = (
        db.query(CollectionRoute)
        .filter(
            CollectionRoute.vehicle_frontend_id == data.vehicle_frontend_id,
            CollectionRoute.route_date == data.assignment_date,
        )
        .first()
    )
    if existing:
        db.delete(existing)
        db.flush()

    safe_plate = data.vehicle_plate.replace(" ", "").replace("/", "")
    route_code = f"FLEET-{safe_plate}-{data.assignment_date.isoformat()}"

    route = CollectionRoute(
        route_code=route_code,
        route_date=data.assignment_date,
        status="planned",
        vehicle_id=vehicle_id,
        vehicle_frontend_id=data.vehicle_frontend_id,
        vehicle_plate=data.vehicle_plate,
        vehicle_name=data.vehicle_name,
        bin_type=data.bin_type,
        area_codes=data.area_codes,
        area_names=data.area_names,
        excluded_bin_ids=data.excluded_bin_ids or [],
        estimated_duration_min=data.estimated_minutes,
        estimated_km=Decimal(str(data.estimated_km)),
        total_bins=data.total_bins,
        total_trips=data.total_trips,
        red_count=data.red_count,
        yellow_count=data.yellow_count,
        green_count=data.green_count,
        road_coordinates=data.road_coordinates,
    )
    db.add(route)
    db.commit()
    db.refresh(route)
    return _route_to_read(route)


def list_fleet_assignments(db: Session, route_date: date | None = None) -> list[FleetAssignmentRead]:
    q = db.query(CollectionRoute).filter(CollectionRoute.vehicle_frontend_id.isnot(None))
    if route_date:
        q = q.filter(CollectionRoute.route_date == route_date)
    routes = q.order_by(CollectionRoute.route_date.desc(), CollectionRoute.id).all()
    return [_route_to_read(r) for r in routes]


def update_assignment_status(db: Session, assignment_id: int, new_status: str) -> FleetAssignmentRead | None:
    route = db.get(CollectionRoute, assignment_id)
    if not route or route.vehicle_frontend_id is None:
        return None
    route.status = new_status
    db.commit()
    db.refresh(route)
    return _route_to_read(route)


def delete_fleet_assignment(db: Session, assignment_id: int) -> bool:
    route = db.get(CollectionRoute, assignment_id)
    if not route or route.vehicle_frontend_id is None:
        return False
    db.delete(route)
    db.commit()
    return True


def collect_area_bins(db: Session, area_codes: list[str]) -> int:
    """Reset fill_level to 0 and stamp last_collection_time for all active bins in the given areas."""
    if not area_codes:
        return 0
    now = datetime.now(timezone.utc)
    result = db.execute(
        text("""
            UPDATE waste_bin
            SET fill_level = 0,
                last_collection_time = :now
            WHERE area_code = ANY(:area_codes)
              AND is_active IS TRUE
              AND status != 'offline'
        """),
        {"now": now, "area_codes": area_codes},
    )
    db.commit()
    return result.rowcount
