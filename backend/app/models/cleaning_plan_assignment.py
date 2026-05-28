from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base


class CleaningPlanAssignment(Base):
    __tablename__ = "cleaning_plan_assignment"

    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_date: Mapped[date] = mapped_column(Date, nullable=False)
    area_code: Mapped[str] = mapped_column(String(80), nullable=False)
    area_name: Mapped[str] = mapped_column(String(160), nullable=False)
    crew_code: Mapped[str] = mapped_column(String(40), nullable=False)
    crew_label: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="draft")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    estimated_length_km: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    estimated_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    required_personnel: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    shift_id: Mapped[int | None] = mapped_column(ForeignKey("shift.id"), nullable=True)
    cleaning_zone_id: Mapped[int | None] = mapped_column(ForeignKey("cleaning_zone.id"), nullable=True)

    shift = relationship("Shift")
    cleaning_zone = relationship("CleaningZone")
    employees = relationship(
        "CleaningPlanAssignmentEmployee",
        back_populates="assignment",
        cascade="all, delete-orphan",
    )
    road_segments = relationship(
        "CleaningPlanAssignmentRoad",
        back_populates="assignment",
        cascade="all, delete-orphan",
    )
