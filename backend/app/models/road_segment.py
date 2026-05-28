from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.geometry import Geometry


class RoadSegment(Base):
    __tablename__ = "road_segment"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    road_type: Mapped[str] = mapped_column(String(40), nullable=False, default="street")
    default_priority: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    geom: Mapped[Any] = mapped_column(Geometry("LINESTRING", 4326), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    cleaning_zone_id: Mapped[int | None] = mapped_column(
        ForeignKey("cleaning_zone.id"),
        nullable=True,
    )
    cleaning_zone = relationship("CleaningZone")

