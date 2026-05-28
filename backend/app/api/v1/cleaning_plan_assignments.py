from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.cleaning_plan_assignment import (
    CleaningPlanAssignmentCreate,
    CleaningPlanAssignmentRead,
    CleaningPlanAssignmentStatusUpdate,
)
from app.services.cleaning_plan_assignment_service import (
    create_cleaning_plan_assignment,
    delete_cleaning_plan_assignment,
    get_cleaning_plan_assignment_by_id,
    get_employees_by_ids,
    list_cleaning_plan_assignments,
    update_cleaning_plan_assignment_status,
)
from app.services.cleaning_plan_assignment_pdf_service import build_cleaning_plan_assignment_pdf
from app.services.shift_service import get_shift_by_id

router = APIRouter(prefix="/cleaning-plan-assignments", tags=["Cleaning Plan Assignments"])


@router.post("", response_model=CleaningPlanAssignmentRead, status_code=status.HTTP_201_CREATED)
def create_cleaning_plan_assignment_endpoint(
    assignment_in: CleaningPlanAssignmentCreate,
    db: Session = Depends(get_db),
):
    employees = get_employees_by_ids(db, assignment_in.employee_ids)
    if len(employees) != len(set(assignment_in.employee_ids)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more employees do not exist.",
        )

    if assignment_in.shift_id is not None:
        shift = get_shift_by_id(db, assignment_in.shift_id)
        if not shift:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Shift with id {assignment_in.shift_id} does not exist.",
            )

    same_day_assignments = list_cleaning_plan_assignments(db, assignment_date=assignment_in.assignment_date)
    existing_crew = next(
        (
            assignment
            for assignment in same_day_assignments
            if assignment.crew_code == assignment_in.crew_code
            or assignment.crew_label == assignment_in.crew_label
        ),
        None,
    )
    if existing_crew:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This crew is already assigned for the selected date.",
        )

    requested_employee_ids = set(assignment_in.employee_ids)
    already_assigned_employee_ids = {
        assignment_employee.employee_id
        for assignment in same_day_assignments
        for assignment_employee in assignment.employees
    }
    duplicate_employee_ids = requested_employee_ids.intersection(already_assigned_employee_ids)
    if duplicate_employee_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more employees are already assigned for the selected date.",
        )

    return create_cleaning_plan_assignment(db, assignment_in)


@router.get("", response_model=list[CleaningPlanAssignmentRead], status_code=status.HTTP_200_OK)
def list_cleaning_plan_assignments_endpoint(
    assignment_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return list_cleaning_plan_assignments(db, assignment_date=assignment_date)


@router.get("/{assignment_id}", response_model=CleaningPlanAssignmentRead, status_code=status.HTTP_200_OK)
def get_cleaning_plan_assignment_endpoint(
    assignment_id: int,
    db: Session = Depends(get_db),
):
    assignment = get_cleaning_plan_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cleaning plan assignment with id {assignment_id} was not found.",
        )
    return assignment


@router.get("/{assignment_id}/pdf", status_code=status.HTTP_200_OK)
def get_cleaning_plan_assignment_pdf_endpoint(
    assignment_id: int,
    db: Session = Depends(get_db),
):
    assignment = get_cleaning_plan_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cleaning plan assignment with id {assignment_id} was not found.",
        )
    pdf_content = build_cleaning_plan_assignment_pdf(assignment)
    filename = f"cleaning-plan-assignment-{assignment_id}.pdf"
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.patch("/{assignment_id}/status", response_model=CleaningPlanAssignmentRead, status_code=status.HTTP_200_OK)
def update_cleaning_plan_assignment_status_endpoint(
    assignment_id: int,
    update_in: CleaningPlanAssignmentStatusUpdate,
    db: Session = Depends(get_db),
):
    assignment = get_cleaning_plan_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cleaning plan assignment with id {assignment_id} was not found.",
        )
    return update_cleaning_plan_assignment_status(db, assignment, update_in)


@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cleaning_plan_assignment_endpoint(
    assignment_id: int,
    db: Session = Depends(get_db),
):
    assignment = get_cleaning_plan_assignment_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Cleaning plan assignment with id {assignment_id} was not found.",
        )
    delete_cleaning_plan_assignment(db, assignment)
