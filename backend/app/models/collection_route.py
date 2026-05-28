from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Date, DateTime, ForeignKey, Integer, JSON, Numeric, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.db.geometry import Geometry


class CollectionRoute(Base):
    __tablename__ = "collection_route"

    id: Mapped[int] = mapped_column(primary_key=True)
    route_code: Mapped[str] = mapped_column(String(60), unique=True, nullable=False)
    route_date: Mapped[date] = mapped_column(Date, nullable=False)
    area_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    area_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="planned")
    estimated_duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    route_geometry: Mapped[Any | None] = mapped_column(Geometry("LINESTRING", 4326), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Fleet wizard assignment fields
    area_codes: Mapped[list | None] = mapped_column(JSON, nullable=True)
    area_names: Mapped[list | None] = mapped_column(JSON, nullable=True)
    bin_type: Mapped[str | None] = mapped_column(String(40), nullable=True)
    excluded_bin_ids: Mapped[list | None] = mapped_column(JSON, nullable=True)
    estimated_km: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    total_bins: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_trips: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    red_count: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    yellow_count: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    green_count: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    road_coordinates: Mapped[list | None] = mapped_column(JSON, nullable=True)
    vehicle_plate: Mapped[str | None] = mapped_column(String(20), nullable=True)
    vehicle_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    vehicle_frontend_id: Mapped[str | None] = mapped_column(String(40), nullable=True)

    shift_id: Mapped[int | None] = mapped_column(ForeignKey("shift.id"), nullable=True)
    sector_id: Mapped[int | None] = mapped_column(ForeignKey("sector.id"), nullable=True)
    vehicle_id: Mapped[int | None] = mapped_column(ForeignKey("vehicle.id"), nullable=True)

    shift = relationship("Shift")
    sector = relationship("Sector")
    vehicle = relationship("Vehicle")
    bins = relationship("CollectionRouteBin", back_populates="route", cascade="all, delete-orphan")
    crew_assignments = relationship(
        "CollectionRouteCrewAssignment",
        back_populates="route",
        cascade="all, delete-orphan",
    )
    events = relationship("CollectionExecutionEvent", back_populates="route", cascade="all, delete-orphan")
