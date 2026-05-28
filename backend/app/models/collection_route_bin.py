from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CollectionRouteBin(Base):
    __tablename__ = "collection_route_bin"
    __table_args__ = (
        UniqueConstraint("collection_route_id", "waste_bin_id", name="uq_collection_route_bin"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    collection_route_id: Mapped[int] = mapped_column(ForeignKey("collection_route.id"), nullable=False)
    waste_bin_id: Mapped[int] = mapped_column(ForeignKey("waste_bin.id"), nullable=False)
    sequence_order: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")
    collection_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    route = relationship("CollectionRoute", back_populates="bins")
    waste_bin = relationship("WasteBin")
