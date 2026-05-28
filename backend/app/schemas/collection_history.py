from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CollectionEventRead(BaseModel):
    id: int
    bin_id: int
    bin_code: str
    bin_type: str
    vehicle_id: Optional[int]
    vehicle_plate: Optional[str]
    vehicle_name: Optional[str]
    collected_at: datetime
    fill_level_before: Optional[int]
    area_name: Optional[str]
    area_code: Optional[str]
    lat: float
    lng: float


class DayCount(BaseModel):
    date: str
    count: int


class TypeCount(BaseModel):
    bin_type: str
    count: int


class HistoryStatsRead(BaseModel):
    total_collections: int
    avg_fill_level: float
    most_active_vehicle: Optional[str]
    bins_not_collected: int
    collections_by_day: list[DayCount]
    collections_by_type: list[TypeCount]


class BinNotCollected(BaseModel):
    bin_id: int
    bin_code: str
    bin_type: str
    area_name: Optional[str]
    last_collected_at: Optional[datetime]
    days_since_last: Optional[int]
    lat: float
    lng: float
