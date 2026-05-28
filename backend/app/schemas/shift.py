from datetime import time

from pydantic import BaseModel, ConfigDict, Field


class ShiftBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    name: str = Field(..., min_length=1, max_length=50)
    start_time: time
    end_time: time


class ShiftCreate(ShiftBase):
    pass


class ShiftUpdate(BaseModel):
    code: str | None = Field(default=None, min_length=1, max_length=20)
    name: str | None = Field(default=None, min_length=1, max_length=50)
    start_time: time | None = None
    end_time: time | None = None
    is_active: bool | None = None


class ShiftRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    start_time: time
    end_time: time
    is_active: bool