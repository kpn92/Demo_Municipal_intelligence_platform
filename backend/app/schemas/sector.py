from pydantic import BaseModel, ConfigDict, Field

from app.schemas.sector_item import SectorItemRead


class SectorBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)


class SectorCreate(SectorBase):
    pass


class SectorUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=20)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=255)
    is_active: bool | None = None


class SectorDeactivate(BaseModel):
    is_active: bool = False


class SectorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None
    is_active: bool


class SectorDetailRead(SectorRead):
    items: list[SectorItemRead] = Field(default_factory=list)
