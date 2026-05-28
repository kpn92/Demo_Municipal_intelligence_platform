from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DailyAssignmentItem(Base):
    __tablename__ = "daily_assignment_item"

    __table_args__ = (
        UniqueConstraint(
            "daily_assignment_id",
            "sector_item_id",
            name="uq_daily_assignment_item_assignment_sector_item",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    daily_assignment_id: Mapped[int] = mapped_column(
        ForeignKey("daily_assignment.id"),
        nullable=False,
    )
    sector_item_id: Mapped[int] = mapped_column(
        ForeignKey("sector_item.id"),
        nullable=False,
    )

    daily_assignment = relationship(
        "DailyAssignment",
        back_populates="assignment_items",
    )
    sector_item = relationship("SectorItem")
