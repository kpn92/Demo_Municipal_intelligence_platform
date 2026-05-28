from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.db.geometry import Geometry


class CollectionExecutionEvent(Base):
    __tablename__ = "collection_execution_event"

    id: Mapped[int] = mapped_column(primary_key=True)
    collection_route_id: Mapped[int] = mapped_column(ForeignKey("collection_route.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(30), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    location: Mapped[Any | None] = mapped_column(Geometry("POINT", 4326), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    fill_level_before: Mapped[int | None] = mapped_column(Integer, nullable=True)
    waste_bin_id: Mapped[int | None] = mapped_column(ForeignKey("waste_bin.id"), nullable=True)
    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("vehicle.id"), nullable=True)
    employee_id: Mapped[int | None] = mapped_column(ForeignKey("employee.id"), nullable=True)

    route = relationship("CollectionRoute", back_populates="events")
    waste_bin = relationship("WasteBin")
    vehicle = relationship("Vehicle")
    employee = relationship("Employee")
