from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.geometry import Geometry


class WasteBin(Base):
    __tablename__ = "waste_bin"

    id: Mapped[int] = mapped_column(primary_key=True)
    bin_code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(40), nullable=False, default="mixed")
    capacity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    location: Mapped[Any] = mapped_column(Geometry("POINT", 4326), nullable=False)
    area_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    area_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    road_segment_code: Mapped[str | None] = mapped_column(String(120), nullable=True)
    fill_level: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="normal")
    last_collection_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    sector_id: Mapped[int | None] = mapped_column(ForeignKey("sector.id"), nullable=True)
    road_segment_id: Mapped[int | None] = mapped_column(ForeignKey("road_segment.id"), nullable=True)

    sector = relationship("Sector")
    road_segment = relationship("RoadSegment")
