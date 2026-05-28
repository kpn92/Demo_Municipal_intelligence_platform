from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate


def get_employee_by_id(db: Session, employee_id: int) -> Employee | None:
    statement = select(Employee).where(Employee.id == employee_id)
    return db.execute(statement).scalar_one_or_none()


def get_employee_by_code(db: Session, employee_code: str) -> Employee | None:
    statement = select(Employee).where(Employee.employee_code == employee_code)
    return db.execute(statement).scalar_one_or_none()


def get_employees(db: Session, skip: int = 0, limit: int = 100) -> list[Employee]:
    statement = select(Employee).offset(skip).limit(limit).order_by(Employee.id)
    return list(db.execute(statement).scalars().all())


def create_employee(db: Session, employee_in: EmployeeCreate) -> Employee:
    employee = Employee(
        first_name=employee_in.first_name,
        last_name=employee_in.last_name,
        employee_code=employee_in.employee_code,
        role=employee_in.role,
        phone=employee_in.phone,
        employment_type=employee_in.employment_type,
        contract_start_date=employee_in.contract_start_date,
        contract_end_date=employee_in.contract_end_date,
        sector_id=employee_in.sector_id,
        is_active=True,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def update_employee(db: Session, employee: Employee, employee_in: EmployeeUpdate) -> Employee:
    update_data = employee_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(employee, field, value)

    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def deactivate_employee(db: Session, employee: Employee) -> Employee:
    employee.is_active = False
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


def delete_employee(db: Session, employee: Employee) -> None:
    db.delete(employee)
    db.commit()
