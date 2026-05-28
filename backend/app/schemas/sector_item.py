from pydantic import BaseModel, ConfigDict, Field


class SectorItemBase(BaseModel):
    sector_id: int
    item_type: str = Field(..., min_length=1, max_length=30)
    name: str = Field(..., min_length=1, max_length=120)
    address: str | None = Field(default=None, max_length=255)
    priority: int = Field(default=3, ge=1, le=5)
    estimated_minutes: int | None = Field(default=None, ge=1, le=1440)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    notes: str | None = None


class SectorItemCreate(SectorItemBase):
    pass


class SectorItemUpdate(BaseModel):
    sector_id: int | None = None
    item_type: str | None = Field(default=None, min_length=1, max_length=30)
    name: str | None = Field(default=None, min_length=1, max_length=120)
    address: str | None = Field(default=None, max_length=255)
    priority: int | None = Field(default=None, ge=1, le=5)
    estimated_minutes: int | None = Field(default=None, ge=1, le=1440)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    notes: str | None = None
    is_active: bool | None = None


class SectorItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sector_id: int
    item_type: str
    name: str
    address: str | None
    priority: int
    estimated_minutes: int | None
    latitude: float | None
    longitude: float | None
    notes: str | None
    is_active: bool
