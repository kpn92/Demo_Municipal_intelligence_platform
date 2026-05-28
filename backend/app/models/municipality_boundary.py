from typing import Any

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.geometry import Geometry


class MunicipalityBoundary(Base):
    __tablename__ = "municipality_boundary"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    geom: Mapped[Any] = mapped_column(Geometry("MULTIPOLYGON", 4326), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

