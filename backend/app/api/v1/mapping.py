from datetime import date
import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.mapping.cleaning_overview import build_cleaning_map_overview
from app.mapping.gis_layers import get_municipality_boundary_layer

router = APIRouter(prefix="/mapping", tags=["Mapping"])

PROJECT_ROOT = Path(__file__).resolve().parents[4]
GIS_EXPORTS_DIR = PROJECT_ROOT / "data" / "gis_exports"
CONTEXT_LAYERS = [
    {
        "id": "municipality_boundary",
        "label": "Όρια δήμου",
        "filename": "municipality_boundary.geojson",
        "geometry_type": "MultiPolygon",
        "enabled": True,
    },
    {
        "id": "buildings_2d",
        "label": "Κτίρια 2D",
        "filename": "buildings_2d.geojson",
        "geometry_type": "Polygon",
        "enabled": True,
    },
    {
        "id": "cleaning_areas",
        "label": "Περιοχές καθαρισμού",
        "filename": "cleaning_areas.geojson",
        "geometry_type": "Polygon",
        "enabled": True,
    },
    {
        "id": "buildings_25d",
        "label": "Κτίρια 2.5D",
        "filename": "buildings_25d.geojson",
        "geometry_type": "Polygon",
        "enabled": True,
    },
    {
        "id": "land_use_zones",
        "label": "Χρήσεις Γης",
        "filename": "land_use_zones.geojson",
        "geometry_type": "Polygon",
        "enabled": True,
    },
]


@router.get("/cleaning/overview", status_code=status.HTTP_200_OK)
def get_cleaning_map_overview_endpoint(
    assignment_date: date = Query(...),
    db: Session = Depends(get_db),
):
    return build_cleaning_map_overview(db, assignment_date)


@router.get("/municipality-boundary", status_code=status.HTTP_200_OK)
def get_municipality_boundary_endpoint(
    db: Session = Depends(get_db),
):
    return get_municipality_boundary_layer(db)


@router.get("/context/{layer_id}", status_code=status.HTTP_200_OK)
def get_context_layer_endpoint(layer_id: str):
    layer = next((candidate for candidate in CONTEXT_LAYERS if candidate["id"] == layer_id), None)
    if not layer or not layer["enabled"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown mapping layer.")

    path = GIS_EXPORTS_DIR / layer["filename"]
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Layer export was not found.")

    return json.loads(path.read_text(encoding="utf-8"))
