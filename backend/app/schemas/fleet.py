from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class PointRead(BaseModel):
    lng: float
    lat: float


class VehicleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_code: str
    type: str
    plate_number: str
    capacity: Decimal | None = None
    capacity_unit: str | None = None
    status: str
    current_location: PointRead | None = None
    area_code: str | None = None
    area_name: str | None = None
    sector_id: int | None = None
    is_active: bool


class WasteBinRead(BaseModel):
    id: int
    bin_code: str
    type: str
    capacity: int | None = None
    location: PointRead
    area_code: str | None = None
    area_name: str | None = None
    road_segment_code: str | None = None
    fill_level: int
    status: str
    last_collection_time: datetime | None = None
    sector_id: int | None = None
    road_segment_id: int | None = None
    is_active: bool


class CollectionRouteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    route_code: str
    route_date: date
    area_code: str | None = None
    area_name: str | None = None
    status: str
    estimated_duration_min: int | None = None
    shift_id: int | None = None
    sector_id: int | None = None
    vehicle_id: int | None = None
    bin_count: int = 0
    collected_bin_count: int = 0


class FleetAssignmentCreate(BaseModel):
    assignment_date: date
    vehicle_frontend_id: str
    vehicle_plate: str
    vehicle_name: str
    bin_type: str | None = None
    area_codes: list[str]
    area_names: list[str]
    excluded_bin_ids: list[int] = Field(default_factory=list)
    total_bins: int
    estimated_minutes: int
    estimated_km: float
    total_trips: int
    red_count: int
    yellow_count: int
    green_count: int
    road_coordinates: list[list[float]] | None = None


class FleetAssignmentRead(BaseModel):
    id: int
    assignment_date: date
    status: str
    vehicle_frontend_id: str | None = None
    vehicle_plate: str | None = None
    vehicle_name: str | None = None
    vehicle_id: int | None = None
    bin_type: str | None = None
    area_codes: list[str] = Field(default_factory=list)
    area_names: list[str] = Field(default_factory=list)
    excluded_bin_ids: list[int] = Field(default_factory=list)
    total_bins: int = 0
    estimated_minutes: int = 0
    estimated_km: float = 0.0
    total_trips: int = 1
    red_count: int = 0
    yellow_count: int = 0
    green_count: int = 0
    road_coordinates: list[list[float]] | None = None
