from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.sector_item import (
    SectorItemCreate,
    SectorItemRead,
    SectorItemUpdate,
)
from app.services.sector_item_service import (
    create_sector_item,
    deactivate_sector_item,
    delete_sector_item,
    get_sector_item_by_id,
    get_sector_items,
    update_sector_item,
)
from app.services.sector_service import get_sector_by_id

router = APIRouter(prefix="/sector-items", tags=["Sector Items"])


@router.post("", response_model=SectorItemRead, status_code=status.HTTP_201_CREATED)
def create_sector_item_endpoint(
    item_in: SectorItemCreate,
    db: Session = Depends(get_db),
):
    sector = get_sector_by_id(db, item_in.sector_id)
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sector with id {item_in.sector_id} does not exist.",
        )

    return create_sector_item(db, item_in)


@router.get("", response_model=list[SectorItemRead], status_code=status.HTTP_200_OK)
def list_sector_items_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    sector_id: int | None = Query(default=None),
    item_type: str | None = Query(default=None),
    active_only: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    return get_sector_items(
        db=db,
        skip=skip,
        limit=limit,
        sector_id=sector_id,
        item_type=item_type,
        active_only=active_only,
    )


@router.get("/{item_id}", response_model=SectorItemRead, status_code=status.HTTP_200_OK)
def get_sector_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
):
    item = get_sector_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector item with id {item_id} was not found.",
        )

    return item


@router.put("/{item_id}", response_model=SectorItemRead, status_code=status.HTTP_200_OK)
def update_sector_item_endpoint(
    item_id: int,
    item_in: SectorItemUpdate,
    db: Session = Depends(get_db),
):
    item = get_sector_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector item with id {item_id} was not found.",
        )

    if item_in.sector_id is not None:
        sector = get_sector_by_id(db, item_in.sector_id)
        if not sector:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sector with id {item_in.sector_id} does not exist.",
            )

    return update_sector_item(db, item, item_in)


@router.patch("/{item_id}/deactivate", response_model=SectorItemRead, status_code=status.HTTP_200_OK)
def deactivate_sector_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
):
    item = get_sector_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector item with id {item_id} was not found.",
        )

    return deactivate_sector_item(db, item)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sector_item_endpoint(
    item_id: int,
    db: Session = Depends(get_db),
):
    item = get_sector_item_by_id(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sector item with id {item_id} was not found.",
        )

    delete_sector_item(db, item)
    return None
