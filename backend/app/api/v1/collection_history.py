from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.collection_history import CollectionEventRead, HistoryStatsRead, BinNotCollected
from app.services import collection_history_service

router = APIRouter(prefix="/fleet/history", tags=["collection-history"])


@router.get("/events", response_model=list[CollectionEventRead])
def list_events(
    date_from: date = Query(...),
    date_to: date = Query(...),
    bin_type: Optional[str] = Query(default=None),
    area_name: Optional[str] = Query(default=None),
    vehicle_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
):
    return collection_history_service.get_collection_events(
        db, date_from, date_to, bin_type, area_name, vehicle_id
    )


@router.get("/stats", response_model=HistoryStatsRead)
def get_stats(
    date_from: date = Query(...),
    date_to: date = Query(...),
    bin_type: Optional[str] = Query(default=None),
    area_name: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    return collection_history_service.get_history_stats(
        db, date_from, date_to, bin_type, area_name
    )


@router.get("/bins-not-collected", response_model=list[BinNotCollected])
def bins_not_collected(
    date_from: date = Query(...),
    date_to: date = Query(...),
    bin_type: Optional[str] = Query(default=None),
    area_name: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    return collection_history_service.get_bins_not_collected(
        db, date_from, date_to, bin_type, area_name
    )


@router.get("/bin-stats")
def bin_stats(
    date_from: date = Query(...),
    date_to: date = Query(...),
    bin_type: Optional[str] = Query(default=None),
    area_name: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    return collection_history_service.get_bin_stats_geojson(
        db, date_from, date_to, bin_type, area_name
    )


@router.get("/export")
def export_history(
    date_from: date = Query(...),
    date_to: date = Query(...),
    format: str = Query(default="excel"),
    bin_type: Optional[str] = Query(default=None),
    area_name: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    filename_base = f"history_{date_from}_{date_to}"
    if format == "pdf":
        data = collection_history_service.export_history_pdf(
            db, date_from, date_to, bin_type, area_name
        )
        return Response(
            content=data,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.pdf"'},
        )
    data = collection_history_service.export_history_excel(
        db, date_from, date_to, bin_type, area_name
    )
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename_base}.xlsx"'},
    )
