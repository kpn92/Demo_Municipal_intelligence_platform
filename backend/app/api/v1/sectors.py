from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.sector import (
    SectorCreate,
    SectorDetailRead,
    SectorRead,
    SectorUpdate,
)
from app.services.sector_service import (
    create_sector,
    deactivate_sector,
    delete_sector,
    get_sector_by_code,
    get_sector_detail_by_id,
    get_sector_by_id,
    get_sectors,
    update_sector,
)

router = APIRouter(prefix="/sectors", tags=["Sectors"])


@router.post(
    "",
    response_model=SectorRead,
    status_code=status.HTTP_201_CREATED,
)
def create_sector_endpoint(
    sector_in: SectorCreate,
    db: Session = Depends(get_db),
):
    existing_sector = get_sector_by_code(db, sector_in.code)
    if existing_sector:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sector with code '{sector_in.code}' already exists.",
        )

    return create_sector(db, sector_in)


@router.get(
    "",
    response_model=list[SectorRead],
    status_code=status.HTTP_200_OK,
)
def list_sectors_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_sectors(db, skip=skip, limit=limit)


@router.get(
    "/{sector_id}/detail",
    response_model=SectorDetailRead,
    status_code=status.HTTP_200_OK,
)
def get_sector_detail_endpoint(
    sector_id: int,
    db: Session = Depends(get_db),
):
    sector = get_sector_detail_by_id(db, sector_id)
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector with id {sector_id} was not found.",
        )

    return sector


@router.get(
    "/{sector_id}",
    response_model=SectorRead,
    status_code=status.HTTP_200_OK,
)
def get_sector_endpoint(
    sector_id: int,
    db: Session = Depends(get_db),
):
    sector = get_sector_by_id(db, sector_id)
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector with id {sector_id} was not found.",
        )

    return sector


@router.put(
    "/{sector_id}",
    response_model=SectorRead,
    status_code=status.HTTP_200_OK,
)
def update_sector_endpoint(
    sector_id: int,
    sector_in: SectorUpdate,
    db: Session = Depends(get_db),
):
    sector = get_sector_by_id(db, sector_id)
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector with id {sector_id} was not found.",
        )

    if sector_in.code and sector_in.code != sector.code:
        existing_sector = get_sector_by_code(db, sector_in.code)
        if existing_sector:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sector with code '{sector_in.code}' already exists.",
            )

    return update_sector(db, sector, sector_in)


@router.patch(
    "/{sector_id}/deactivate",
    response_model=SectorRead,
    status_code=status.HTTP_200_OK,
)
def deactivate_sector_endpoint(
    sector_id: int,
    db: Session = Depends(get_db),
):
    sector = get_sector_by_id(db, sector_id)
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector with id {sector_id} was not found.",
        )

    return deactivate_sector(db, sector)


@router.delete(
    "/{sector_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_sector_endpoint(
    sector_id: int,
    db: Session = Depends(get_db),
):
    sector = get_sector_by_id(db, sector_id)
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector with id {sector_id} was not found.",
        )

    delete_sector(db, sector)
    return None
