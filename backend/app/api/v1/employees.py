from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.employee import EmployeeCreate, EmployeeRead, EmployeeUpdate
from app.services.employee_service import (
    create_employee,
    deactivate_employee,
    delete_employee,
    get_employee_by_code,
    get_employee_by_id,
    get_employees,
    update_employee,
)
from app.services.sector_service import get_sector_by_id

router = APIRouter(prefix="/employees", tags=["Employees"])


@router.post("", response_model=EmployeeRead, status_code=status.HTTP_201_CREATED)
def create_employee_endpoint(
    employee_in: EmployeeCreate,
    db: Session = Depends(get_db),
):
    existing_employee = get_employee_by_code(db, employee_in.employee_code)
    if existing_employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with code '{employee_in.employee_code}' already exists.",
        )

    sector = get_sector_by_id(db, employee_in.sector_id)
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sector with id {employee_in.sector_id} does not exist.",
        )

    return create_employee(db, employee_in)


@router.get("", response_model=list[EmployeeRead], status_code=status.HTTP_200_OK)
def list_employees_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_employees(db, skip=skip, limit=limit)


@router.get("/{employee_id}", response_model=EmployeeRead, status_code=status.HTTP_200_OK)
def get_employee_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} was not found.",
        )

    return employee


@router.put("/{employee_id}", response_model=EmployeeRead, status_code=status.HTTP_200_OK)
def update_employee_endpoint(
    employee_id: int,
    employee_in: EmployeeUpdate,
    db: Session = Depends(get_db),
):
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} was not found.",
        )

    if employee_in.employee_code and employee_in.employee_code != employee.employee_code:
        existing_employee = get_employee_by_code(db, employee_in.employee_code)
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Employee with code '{employee_in.employee_code}' already exists.",
            )

    if employee_in.sector_id is not None:
        sector = get_sector_by_id(db, employee_in.sector_id)
        if not sector:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Sector with id {employee_in.sector_id} does not exist.",
            )

    return update_employee(db, employee, employee_in)


@router.patch("/{employee_id}/deactivate", response_model=EmployeeRead, status_code=status.HTTP_200_OK)
def deactivate_employee_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} was not found.",
        )

    return deactivate_employee(db, employee)


@router.delete("/{employee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employee_endpoint(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Employee with id {employee_id} was not found.",
        )

    delete_employee(db, employee)
    return None