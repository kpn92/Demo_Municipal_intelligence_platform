from decimal import Decimal

from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CleaningPlanAssignmentRoad(Base):
    __tablename__ = "cleaning_plan_assignment_road"
    __table_args__ = (
        UniqueConstraint(
            "cleaning_plan_assignment_id",
            "segment_code",
            name="uq_cleaning_plan_assignment_road_segment_code",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    cleaning_plan_assignment_id: Mapped[int] = mapped_column(
        ForeignKey("cleaning_plan_assignment.id"),
        nullable=False,
    )
    segment_code: Mapped[str] = mapped_column(String(120), nullable=False)
    road_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="assigned")
    planned_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    road_length_km: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)

    road_segment_id: Mapped[int | None] = mapped_column(ForeignKey("road_segment.id"), nullable=True)

    assignment = relationship("CleaningPlanAssignment", back_populates="road_segments")
    road_segment = relationship("RoadSegment")
