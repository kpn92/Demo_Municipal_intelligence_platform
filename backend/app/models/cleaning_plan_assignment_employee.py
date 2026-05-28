from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CleaningPlanAssignmentEmployee(Base):
    __tablename__ = "cleaning_plan_assignment_employee"
    __table_args__ = (
        UniqueConstraint(
            "cleaning_plan_assignment_id",
            "employee_id",
            name="uq_cleaning_plan_assignment_employee",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cleaning_plan_assignment_id: Mapped[int] = mapped_column(
        ForeignKey("cleaning_plan_assignment.id"),
        nullable=False,
    )
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"), nullable=False)

    assignment = relationship("CleaningPlanAssignment", back_populates="employees")
    employee = relationship("Employee")
