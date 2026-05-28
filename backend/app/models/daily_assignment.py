from datetime import date

from sqlalchemy import Date, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DailyAssignment(Base):
    __tablename__ = "daily_assignment"

    __table_args__ = (
        UniqueConstraint(
            "assignment_date",
            "employee_id",
            "shift_id",
            name="uq_daily_assignment_employee_date_shift",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_date: Mapped[date] = mapped_column(Date, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="scheduled")
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)

    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"), nullable=False)
    sector_id: Mapped[int] = mapped_column(ForeignKey("sector.id"), nullable=False)
    shift_id: Mapped[int] = mapped_column(ForeignKey("shift.id"), nullable=False)

    employee = relationship("Employee")
    sector = relationship("Sector")
    shift = relationship("Shift")
    assignment_items = relationship(
        "DailyAssignmentItem",
        back_populates="daily_assignment",
        cascade="all, delete-orphan",
    )
