from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.employee import EmployeeRead
from app.schemas.sector import SectorDetailRead
from app.schemas.sector_item import SectorItemRead
from app.schemas.shift import ShiftRead


class DailyAssignmentBase(BaseModel):
    assignment_date: date
    employee_id: int
    sector_id: int
    shift_id: int
    notes: str | None = Field(default=None, max_length=255)


class DailyAssignmentCreate(DailyAssignmentBase):
    pass


class DailyAssignmentGenerateRequest(BaseModel):
    assignment_date: date
    shift_id: int
    notes: str | None = Field(default=None, max_length=255)


class DailyAssignmentUpdate(BaseModel):
    assignment_date: date | None = None
    employee_id: int | None = None
    sector_id: int | None = None
    shift_id: int | None = None
    status: str | None = Field(default=None, max_length=20)
    notes: str | None = Field(default=None, max_length=255)


class DailyAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assignment_date: date
    status: str
    notes: str | None
    employee_id: int
    sector_id: int
    shift_id: int


class DailyAssignmentItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    daily_assignment_id: int
    sector_item_id: int
    sector_item: SectorItemRead


class DailyAssignmentPlanRead(DailyAssignmentRead):
    employee: EmployeeRead
    sector: SectorDetailRead
    shift: ShiftRead
    assignment_items: list[DailyAssignmentItemRead] = Field(default_factory=list)


class DailyAssignmentGenerateResult(BaseModel):
    created_count: int
    skipped_count: int
    assignments: list[DailyAssignmentPlanRead]
