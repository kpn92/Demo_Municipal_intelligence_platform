from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CollectionRouteCrewAssignment(Base):
    __tablename__ = "collection_route_crew_assignment"
    __table_args__ = (
        UniqueConstraint("collection_route_id", "employee_id", name="uq_collection_route_crew_employee"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    collection_route_id: Mapped[int] = mapped_column(ForeignKey("collection_route.id"), nullable=False)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(30), nullable=False, default="worker")

    route = relationship("CollectionRoute", back_populates="crew_assignments")
    employee = relationship("Employee")
