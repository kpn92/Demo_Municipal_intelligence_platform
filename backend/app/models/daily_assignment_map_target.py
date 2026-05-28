from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DailyAssignmentMapTarget(Base):
    __tablename__ = "daily_assignment_map_target"
    __table_args__ = (
        UniqueConstraint(
            "daily_assignment_id",
            "target_type",
            "target_id",
            name="uq_daily_assignment_map_target",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    daily_assignment_id: Mapped[int] = mapped_column(
        ForeignKey("daily_assignment.id"),
        nullable=False,
    )
    target_type: Mapped[str] = mapped_column(String(40), nullable=False)
    target_id: Mapped[int] = mapped_column(Integer, nullable=False)
    planned_order: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="assigned")

    daily_assignment = relationship("DailyAssignment")

