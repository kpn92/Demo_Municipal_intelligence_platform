from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.shift import ShiftCreate, ShiftRead, ShiftUpdate
from app.services.shift_service import (
    create_shift,
    deactivate_shift,
    delete_shift,
    get_shift_by_code,
    get_shift_by_id,
    get_shifts,
    update_shift,
)

router = APIRouter(prefix="/shifts", tags=["Shifts"])


@router.post("", response_model=ShiftRead, status_code=status.HTTP_201_CREATED)
def create_shift_endpoint(
    shift_in: ShiftCreate,
    db: Session = Depends(get_db),
):
    existing_shift = get_shift_by_code(db, shift_in.code)
    if existing_shift:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Shift with code '{shift_in.code}' already exists.",
        )

    return create_shift(db, shift_in)


@router.get("", response_model=list[ShiftRead], status_code=status.HTTP_200_OK)
def list_shifts_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_shifts(db, skip=skip, limit=limit)


@router.get("/{shift_id}", response_model=ShiftRead, status_code=status.HTTP_200_OK)
def get_shift_endpoint(
    shift_id: int,
    db: Session = Depends(get_db),
):
    shift = get_shift_by_id(db, shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shift with id {shift_id} was not found.",
        )

    return shift


@router.put("/{shift_id}", response_model=ShiftRead, status_code=status.HTTP_200_OK)
def update_shift_endpoint(
    shift_id: int,
    shift_in: ShiftUpdate,
    db: Session = Depends(get_db),
):
    shift = get_shift_by_id(db, shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shift with id {shift_id} was not found.",
        )

    if shift_in.code and shift_in.code != shift.code:
        existing_shift = get_shift_by_code(db, shift_in.code)
        if existing_shift:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Shift with code '{shift_in.code}' already exists.",
            )

    return update_shift(db, shift, shift_in)


@router.patch("/{shift_id}/deactivate", response_model=ShiftRead, status_code=status.HTTP_200_OK)
def deactivate_shift_endpoint(
    shift_id: int,
    db: Session = Depends(get_db),
):
    shift = get_shift_by_id(db, shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shift with id {shift_id} was not found.",
        )

    return deactivate_shift(db, shift)


@router.delete("/{shift_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shift_endpoint(
    shift_id: int,
    db: Session = Depends(get_db),
):
    shift = get_shift_by_id(db, shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Shift with id {shift_id} was not found.",
        )

    delete_shift(db, shift)
    return None