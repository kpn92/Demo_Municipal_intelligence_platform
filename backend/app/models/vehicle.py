from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.geometry import Geometry


class Vehicle(Base):
    __tablename__ = "vehicle"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    plate_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    capacity: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    capacity_unit: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="available")
    current_location: Mapped[Any | None] = mapped_column(Geometry("POINT", 4326), nullable=True)
    area_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    area_name: Mapped[str | None] = mapped_column(String(160), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    sector_id: Mapped[int | None] = mapped_column(ForeignKey("sector.id"), nullable=True)
    sector = relationship("Sector")
