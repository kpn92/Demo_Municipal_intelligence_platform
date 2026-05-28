from datetime import date

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.models.daily_assignment import DailyAssignment
from app.models.daily_assignment_item import DailyAssignmentItem
from app.models.employee import Employee
from app.models.sector import Sector
from app.models.sector_item import SectorItem
from app.schemas.daily_assignment import DailyAssignmentCreate, DailyAssignmentUpdate


def get_daily_assignment_by_id(db: Session, assignment_id: int) -> DailyAssignment | None:
    statement = select(DailyAssignment).where(DailyAssignment.id == assignment_id)
    return db.execute(statement).scalar_one_or_none()


def get_daily_assignments(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[DailyAssignment]:
    statement = (
        select(DailyAssignment)
        .offset(skip)
        .limit(limit)
        .order_by(DailyAssignment.assignment_date, DailyAssignment.id)
    )
    return list(db.execute(statement).scalars().all())


def get_daily_assignments_by_date(
    db: Session,
    assignment_date: date,
) -> list[DailyAssignment]:
    statement = (
        select(DailyAssignment)
        .where(DailyAssignment.assignment_date == assignment_date)
        .order_by(DailyAssignment.shift_id, DailyAssignment.employee_id)
    )
    return list(db.execute(statement).scalars().all())


def get_daily_assignment_plan_by_date(
    db: Session,
    assignment_date: date,
) -> list[DailyAssignment]:
    statement = (
        select(DailyAssignment)
        .where(DailyAssignment.assignment_date == assignment_date)
        .options(
            selectinload(DailyAssignment.employee),
            selectinload(DailyAssignment.shift),
            selectinload(DailyAssignment.sector).selectinload(Sector.items),
            selectinload(DailyAssignment.assignment_items).selectinload(
                DailyAssignmentItem.sector_item,
            ),
        )
        .order_by(DailyAssignment.shift_id, DailyAssignment.employee_id)
    )
    return list(db.execute(statement).scalars().all())


def get_existing_employee_assignment(
    db: Session,
    assignment_date: date,
    employee_id: int,
    shift_id: int,
) -> DailyAssignment | None:
    statement = select(DailyAssignment).where(
        DailyAssignment.assignment_date == assignment_date,
        DailyAssignment.employee_id == employee_id,
        DailyAssignment.shift_id == shift_id,
    )
    return db.execute(statement).scalar_one_or_none()


def create_daily_assignment(
    db: Session,
    assignment_in: DailyAssignmentCreate,
) -> DailyAssignment:
    assignment = DailyAssignment(
        assignment_date=assignment_in.assignment_date,
        employee_id=assignment_in.employee_id,
        sector_id=assignment_in.sector_id,
        shift_id=assignment_in.shift_id,
        notes=assignment_in.notes,
        status="scheduled",
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def generate_daily_assignments(
    db: Session,
    assignment_date: date,
    shift_id: int,
    notes: str | None = None,
) -> tuple[int, int]:
    available_employees = db.execute(
        select(Employee)
        .where(Employee.is_active.is_(True))
        .where(
            (Employee.contract_start_date.is_(None))
            | (Employee.contract_start_date <= assignment_date)
        )
        .where(
            (Employee.contract_end_date.is_(None))
            | (Employee.contract_end_date >= assignment_date)
        )
        .order_by(Employee.sector_id, Employee.id)
    ).scalars().all()

    created_count = 0
    skipped_count = 0
    sector_employee_map: dict[int, list[Employee]] = {}

    for employee in available_employees:
        sector_employee_map.setdefault(employee.sector_id, []).append(employee)

    for employee in available_employees:
        existing_assignment = get_existing_employee_assignment(
            db=db,
            assignment_date=assignment_date,
            employee_id=employee.id,
            shift_id=shift_id,
        )
        if existing_assignment:
            skipped_count += 1
            continue

        assignment = DailyAssignment(
            assignment_date=assignment_date,
            employee_id=employee.id,
            sector_id=employee.sector_id,
            shift_id=shift_id,
            notes=notes,
            status="scheduled",
        )
        db.add(assignment)
        created_count += 1

    db.flush()

    for sector_id, employees in sector_employee_map.items():
        assignments = db.execute(
            select(DailyAssignment)
            .where(DailyAssignment.assignment_date == assignment_date)
            .where(DailyAssignment.shift_id == shift_id)
            .where(DailyAssignment.sector_id == sector_id)
            .where(DailyAssignment.employee_id.in_([employee.id for employee in employees]))
            .order_by(DailyAssignment.employee_id)
        ).scalars().all()

        if not assignments:
            continue

        db.execute(
            delete(DailyAssignmentItem).where(
                DailyAssignmentItem.daily_assignment_id.in_(
                    [assignment.id for assignment in assignments],
                ),
            ),
        )

        sector_items = db.execute(
            select(SectorItem)
            .where(SectorItem.sector_id == sector_id)
            .where(SectorItem.is_active.is_(True))
            .order_by(
                SectorItem.priority,
                SectorItem.estimated_minutes.desc().nullslast(),
                SectorItem.id,
            )
        ).scalars().all()

        assignment_loads = {assignment.id: 0 for assignment in assignments}

        for sector_item in sector_items:
            target_assignment = min(
                assignments,
                key=lambda assignment: (
                    assignment_loads[assignment.id],
                    assignment.employee_id,
                ),
            )
            db.add(
                DailyAssignmentItem(
                    daily_assignment_id=target_assignment.id,
                    sector_item_id=sector_item.id,
                ),
            )
            assignment_loads[target_assignment.id] += sector_item.estimated_minutes or 30

    db.commit()
    return created_count, skipped_count


def update_daily_assignment(
    db: Session,
    assignment: DailyAssignment,
    assignment_in: DailyAssignmentUpdate,
) -> DailyAssignment:
    update_data = assignment_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(assignment, field, value)

    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    return assignment


def delete_daily_assignment(
    db: Session,
    assignment: DailyAssignment,
) -> None:
    db.delete(assignment)
    db.commit()
