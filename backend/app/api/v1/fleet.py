from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.models.collection_route import CollectionRoute
from app.schemas.fleet import CollectionRouteRead, FleetAssignmentCreate, FleetAssignmentRead, VehicleRead, WasteBinRead
from app.services import fleet_service

router = APIRouter(prefix="/fleet", tags=["Fleet"])


@router.get("/vehicles", response_model=list[VehicleRead], status_code=status.HTTP_200_OK)
def list_vehicles(db: Session = Depends(get_db)):
    rows = db.execute(
        text(
            """
            SELECT
                id,
                vehicle_code,
                type,
                plate_number,
                capacity,
                capacity_unit,
                status,
                area_code,
                area_name,
                sector_id,
                is_active,
                CASE
                    WHEN current_location IS NULL THEN NULL
                    ELSE json_build_object(
                        'lng', ST_X(current_location::geometry),
                        'lat', ST_Y(current_location::geometry)
                    )
                END AS current_location
            FROM vehicle
            WHERE is_active IS TRUE
            ORDER BY vehicle_code
            """
        )
    ).mappings()
    return [dict(row) for row in rows]


@router.get("/bins", response_model=list[WasteBinRead], status_code=status.HTTP_200_OK)
def list_bins(
    area_code: str | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    filters = ["is_active IS TRUE"]
    params = {}
    if area_code:
        filters.append("area_code = :area_code")
        params["area_code"] = area_code
    if status_filter:
        filters.append("status = :status")
        params["status"] = status_filter

    rows = db.execute(
        text(
            f"""
            SELECT
                id,
                bin_code,
                type,
                capacity,
                json_build_object(
                    'lng', ST_X(location::geometry),
                    'lat', ST_Y(location::geometry)
                ) AS location,
                area_code,
                area_name,
                road_segment_code,
                CASE
                    WHEN last_collection_time IS NULL THEN fill_level
                    ELSE LEAST(100, fill_level + GREATEST(0,
                        (CURRENT_DATE - last_collection_time::date) * 15
                    ))
                END AS fill_level,
                status,
                last_collection_time,
                sector_id,
                road_segment_id,
                is_active
            FROM waste_bin
            WHERE {" AND ".join(filters)}
            ORDER BY area_code, road_segment_code, bin_code
            """
        ),
        params,
    ).mappings()
    return [dict(row) for row in rows]


@router.get("/routes", response_model=list[CollectionRouteRead], status_code=status.HTTP_200_OK)
def list_routes(
    route_date: date | None = Query(default=None),
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    query = db.query(CollectionRoute)
    if route_date:
        query = query.filter(CollectionRoute.route_date == route_date)
    if status_filter:
        query = query.filter(CollectionRoute.status == status_filter)

    routes = query.order_by(CollectionRoute.route_date.desc(), CollectionRoute.route_code).all()
    return [
        CollectionRouteRead(
            id=route.id,
            route_code=route.route_code,
            route_date=route.route_date,
            area_code=route.area_code,
            area_name=route.area_name,
            status=route.status,
            estimated_duration_min=route.estimated_duration_min,
            shift_id=route.shift_id,
            sector_id=route.sector_id,
            vehicle_id=route.vehicle_id,
            bin_count=len(route.bins),
            collected_bin_count=sum(1 for entry in route.bins if entry.status == "collected"),
        )
        for route in routes
    ]


@router.get("/overview", status_code=status.HTTP_200_OK)
def get_fleet_overview(db: Session = Depends(get_db)):
    vehicle_counts = db.execute(
        text("SELECT status, COUNT(*) AS count FROM vehicle WHERE is_active IS TRUE GROUP BY status")
    ).mappings()
    bin_counts = db.execute(
        text("SELECT status, COUNT(*) AS count FROM waste_bin WHERE is_active IS TRUE GROUP BY status")
    ).mappings()
    return {
        "vehicles": {row["status"]: row["count"] for row in vehicle_counts},
        "bins": {row["status"]: row["count"] for row in bin_counts},
    }


@router.post("/assignments", response_model=FleetAssignmentRead, status_code=status.HTTP_201_CREATED)
def create_fleet_assignment(data: FleetAssignmentCreate, db: Session = Depends(get_db)):
    return fleet_service.save_fleet_assignment(db, data)


@router.get("/assignments", response_model=list[FleetAssignmentRead], status_code=status.HTTP_200_OK)
def list_fleet_assignments(
    route_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return fleet_service.list_fleet_assignments(db, route_date)


@router.patch("/assignments/{assignment_id}/status", response_model=FleetAssignmentRead, status_code=status.HTTP_200_OK)
def update_fleet_assignment_status(
    assignment_id: int,
    new_status: str = Query(...),
    db: Session = Depends(get_db),
):
    result = fleet_service.update_assignment_status(db, assignment_id, new_status)
    if result is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return result


@router.delete("/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fleet_assignment(assignment_id: int, db: Session = Depends(get_db)):
    if not fleet_service.delete_fleet_assignment(db, assignment_id):
        raise HTTPException(status_code=404, detail="Assignment not found")


@router.patch("/vehicles/{vehicle_id}/status", status_code=status.HTTP_200_OK)
def update_vehicle_status(
    vehicle_id: int,
    new_status: str = Query(..., pattern="^(available|maintenance|offline)$"),
    db: Session = Depends(get_db),
):
    result = db.execute(
        text("UPDATE vehicle SET status = :s WHERE id = :id AND is_active IS TRUE RETURNING id, plate_number"),
        {"s": new_status, "id": vehicle_id},
    ).fetchone()
    db.commit()
    if not result:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return {"id": vehicle_id, "plate": result.plate_number, "status": new_status}


@router.patch("/bins/{bin_id}/status", status_code=status.HTTP_200_OK)
def update_bin_status(
    bin_id: int,
    new_status: str = Query(..., pattern="^(normal|needs_collection|full|issue|offline)$"),
    db: Session = Depends(get_db),
):
    result = db.execute(
        text("UPDATE waste_bin SET status = :s WHERE id = :id AND is_active IS TRUE RETURNING id"),
        {"s": new_status, "id": bin_id},
    ).fetchone()
    db.commit()
    if not result:
        raise HTTPException(status_code=404, detail="Bin not found")
    return {"id": bin_id, "status": new_status}


class BinCollectRequest(BaseModel):
    area_codes: list[str]


@router.post("/bins/collect", status_code=status.HTTP_200_OK)
def collect_bins(data: BinCollectRequest, db: Session = Depends(get_db)):
    updated = fleet_service.collect_area_bins(db, data.area_codes)
    return {"updated": updated}
