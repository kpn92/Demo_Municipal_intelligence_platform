from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.cleaning_plan_assignment import CleaningPlanAssignment
from app.models.cleaning_plan_assignment_employee import CleaningPlanAssignmentEmployee
from app.models.cleaning_plan_assignment_road import CleaningPlanAssignmentRoad
from app.models.employee import Employee
from app.schemas.cleaning_plan_assignment import (
    CleaningPlanAssignmentCreate,
    CleaningPlanAssignmentStatusUpdate,
)


def get_cleaning_plan_assignment_by_id(
    db: Session,
    assignment_id: int,
) -> CleaningPlanAssignment | None:
    statement = (
        select(CleaningPlanAssignment)
        .where(CleaningPlanAssignment.id == assignment_id)
        .options(
            selectinload(CleaningPlanAssignment.shift),
            selectinload(CleaningPlanAssignment.employees).selectinload(
                CleaningPlanAssignmentEmployee.employee,
            ),
            selectinload(CleaningPlanAssignment.road_segments),
        )
    )
    return db.execute(statement).scalar_one_or_none()


def list_cleaning_plan_assignments(
    db: Session,
    assignment_date: date | None = None,
) -> list[CleaningPlanAssignment]:
    statement = (
        select(CleaningPlanAssignment)
        .options(
            selectinload(CleaningPlanAssignment.shift),
            selectinload(CleaningPlanAssignment.employees).selectinload(
                CleaningPlanAssignmentEmployee.employee,
            ),
            selectinload(CleaningPlanAssignment.road_segments),
        )
        .order_by(
            CleaningPlanAssignment.assignment_date.desc(),
            CleaningPlanAssignment.created_at.desc(),
        )
    )
    if assignment_date is not None:
        statement = statement.where(CleaningPlanAssignment.assignment_date == assignment_date)

    return list(db.execute(statement).scalars().all())


def create_cleaning_plan_assignment(
    db: Session,
    assignment_in: CleaningPlanAssignmentCreate,
) -> CleaningPlanAssignment:
    assignment = CleaningPlanAssignment(
        assignment_date=assignment_in.assignment_date,
        area_code=assignment_in.area_code,
        area_name=assignment_in.area_name,
        crew_code=assignment_in.crew_code,
        crew_label=assignment_in.crew_label,
        shift_id=assignment_in.shift_id,
        cleaning_zone_id=assignment_in.cleaning_zone_id,
        notes=assignment_in.notes,
        estimated_length_km=assignment_in.estimated_length_km,
        estimated_duration_min=assignment_in.estimated_duration_min,
        required_personnel=assignment_in.required_personnel,
        status="assigned",
    )
    db.add(assignment)
    db.flush()

    for employee_id in assignment_in.employee_ids:
        db.add(
            CleaningPlanAssignmentEmployee(
                cleaning_plan_assignment_id=assignment.id,
                employee_id=employee_id,
            ),
        )

    for road in assignment_in.road_segments:
        db.add(
            CleaningPlanAssignmentRoad(
                cleaning_plan_assignment_id=assignment.id,
                segment_code=road.segment_code,
                road_name=road.road_name,
                status=road.status,
                planned_order=road.planned_order,
                priority=road.priority,
                estimated_duration_min=road.estimated_duration_min,
                road_length_km=road.road_length_km,
                road_segment_id=road.road_segment_id,
            ),
        )

    db.commit()
    return get_cleaning_plan_assignment_by_id(db, assignment.id)


def update_cleaning_plan_assignment_status(
    db: Session,
    assignment: CleaningPlanAssignment,
    update_in: CleaningPlanAssignmentStatusUpdate,
) -> CleaningPlanAssignment:
    assignment.status = update_in.status
    if update_in.notes is not None:
        assignment.notes = update_in.notes

    for road_segment in assignment.road_segments:
        road_segment.status = update_in.road_statuses.get(
            road_segment.segment_code,
            update_in.status,
        )
        db.add(road_segment)
    db.add(assignment)
    db.commit()
    return get_cleaning_plan_assignment_by_id(db, assignment.id)


def delete_cleaning_plan_assignment(
    db: Session,
    assignment: CleaningPlanAssignment,
) -> None:
    db.delete(assignment)
    db.commit()


def get_employees_by_ids(
    db: Session,
    employee_ids: list[int],
) -> list[Employee]:
    if not employee_ids:
        return []
    statement = select(Employee).where(Employee.id.in_(employee_ids))
    return list(db.execute(statement).scalars().all())
