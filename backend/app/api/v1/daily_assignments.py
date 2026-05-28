from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.daily_assignment import (
    DailyAssignmentCreate,
    DailyAssignmentGenerateRequest,
    DailyAssignmentGenerateResult,
    DailyAssignmentPlanRead,
    DailyAssignmentRead,
    DailyAssignmentUpdate,
)
from app.services.daily_assignment_service import (
    create_daily_assignment,
    delete_daily_assignment,
    generate_daily_assignments,
    get_daily_assignment_by_id,
    get_daily_assignment_plan_by_date,
    get_daily_assignments,
    get_daily_assignments_by_date,
    get_existing_employee_assignment,
    update_daily_assignment,
)
from app.services.employee_service import get_employee_by_id
from app.services.sector_service import get_sector_by_id
from app.services.shift_service import get_shift_by_id

router = APIRouter(prefix="/daily-assignments", tags=["Daily Assignments"])


@router.post("", response_model=DailyAssignmentRead, status_code=status.HTTP_201_CREATED)
def create_daily_assignment_endpoint(
    assignment_in: DailyAssignmentCreate,
    db: Session = Depends(get_db),
):
    employee = get_employee_by_id(db, assignment_in.employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with id {assignment_in.employee_id} does not exist.",
        )

    sector = get_sector_by_id(db, assignment_in.sector_id)
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sector with id {assignment_in.sector_id} does not exist.",
        )

    shift = get_shift_by_id(db, assignment_in.shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Shift with id {assignment_in.shift_id} does not exist.",
        )

    existing_assignment = get_existing_employee_assignment(
        db=db,
        assignment_date=assignment_in.assignment_date,
        employee_id=assignment_in.employee_id,
        shift_id=assignment_in.shift_id,
    )
    if existing_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This employee already has an assignment for the same date and shift.",
        )

    return create_daily_assignment(db, assignment_in)


@router.get("", response_model=list[DailyAssignmentRead], status_code=status.HTTP_200_OK)
def list_daily_assignments_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    assignment_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if assignment_date is not None:
        return get_daily_assignments_by_date(db, assignment_date)

    return get_daily_assignments(db, skip=skip, limit=limit)


@router.post(
    "/generate",
    response_model=DailyAssignmentGenerateResult,
    status_code=status.HTTP_201_CREATED,
)
def generate_daily_assignment_plan_endpoint(
    generate_in: DailyAssignmentGenerateRequest,
    db: Session = Depends(get_db),
):
    shift = get_shift_by_id(db, generate_in.shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Shift with id {generate_in.shift_id} does not exist.",
        )

    created_count, skipped_count = generate_daily_assignments(
        db=db,
        assignment_date=generate_in.assignment_date,
        shift_id=generate_in.shift_id,
        notes=generate_in.notes,
    )
    assignments = get_daily_assignment_plan_by_date(db, generate_in.assignment_date)

    return DailyAssignmentGenerateResult(
        created_count=created_count,
        skipped_count=skipped_count,
        assignments=assignments,
    )


@router.get("/plan", response_model=list[DailyAssignmentPlanRead], status_code=status.HTTP_200_OK)
def get_daily_assignment_plan_endpoint(
    assignment_date: date = Query(...),
    db: Session = Depends(get_db),
):
    return get_daily_assignment_plan_by_date(db, assignment_date)


@router.get("/{assignment_id}", response_model=DailyAssignmentRead, status_code=status.HTTP_200_OK)
def get_daily_assignment_endpoint(
    assignment_id: int,
    db: Session = Depends(get_db),
):
    assignment = get_daily_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Daily assignment with id {assignment_id} was not found.",
        )

    return assignment


@router.put("/{assignment_id}", response_model=DailyAssignmentRead, status_code=status.HTTP_200_OK)
def update_daily_assignment_endpoint(
    assignment_id: int,
    assignment_in: DailyAssignmentUpdate,
    db: Session = Depends(get_db),
):
    assignment = get_daily_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Daily assignment with id {assignment_id} was not found.",
        )

    new_employee_id = assignment_in.employee_id if assignment_in.employee_id is not None else assignment.employee_id
    new_sector_id = assignment_in.sector_id if assignment_in.sector_id is not None else assignment.sector_id
    new_shift_id = assignment_in.shift_id if assignment_in.shift_id is not None else assignment.shift_id
    new_assignment_date = (
        assignment_in.assignment_date if assignment_in.assignment_date is not None else assignment.assignment_date
    )

    employee = get_employee_by_id(db, new_employee_id)
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Employee with id {new_employee_id} does not exist.",
        )

    sector = get_sector_by_id(db, new_sector_id)
    if not sector:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Sector with id {new_sector_id} does not exist.",
        )

    shift = get_shift_by_id(db, new_shift_id)
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Shift with id {new_shift_id} does not exist.",
        )

    existing_assignment = get_existing_employee_assignment(
        db=db,
        assignment_date=new_assignment_date,
        employee_id=new_employee_id,
        shift_id=new_shift_id,
    )
    if existing_assignment and existing_assignment.id != assignment.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This employee already has an assignment for the same date and shift.",
        )

    return update_daily_assignment(db, assignment, assignment_in)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_daily_assignment_endpoint(
    assignment_id: int,
    db: Session = Depends(get_db),
):
    assignment = get_daily_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Daily assignment with id {assignment_id} was not found.",
        )

    delete_daily_assignment(db, assignment)
    return None
