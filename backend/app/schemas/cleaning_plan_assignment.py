from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.employee import EmployeeRead
from app.schemas.shift import ShiftRead


class CleaningPlanAssignmentRoadBase(BaseModel):
    segment_code: str = Field(min_length=1, max_length=120)
    road_name: str | None = Field(default=None, max_length=160)
    status: str = Field(default="assigned", max_length=30)
    planned_order: int | None = None
    priority: int | None = None
    estimated_duration_min: int | None = None
    road_length_km: Decimal | None = None
    road_segment_id: int | None = None


class CleaningPlanAssignmentRoadCreate(CleaningPlanAssignmentRoadBase):
    pass


class CleaningPlanAssignmentRoadRead(CleaningPlanAssignmentRoadBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cleaning_plan_assignment_id: int


class CleaningPlanAssignmentEmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    employee_id: int
    employee: EmployeeRead


class CleaningPlanAssignmentBase(BaseModel):
    assignment_date: date
    area_code: str = Field(min_length=1, max_length=80)
    area_name: str = Field(min_length=1, max_length=160)
    crew_code: str = Field(min_length=1, max_length=40)
    crew_label: str = Field(min_length=1, max_length=80)
    shift_id: int | None = None
    cleaning_zone_id: int | None = None
    notes: str | None = None
    estimated_length_km: Decimal | None = None
    estimated_duration_min: int | None = None
    required_personnel: int | None = None


class CleaningPlanAssignmentCreate(CleaningPlanAssignmentBase):
    employee_ids: list[int] = Field(default_factory=list, min_length=1)
    road_segments: list[CleaningPlanAssignmentRoadCreate] = Field(default_factory=list, min_length=1)


class CleaningPlanAssignmentStatusUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=30)
    notes: str | None = None
    road_statuses: dict[str, str] = Field(default_factory=dict)


class CleaningPlanAssignmentRead(CleaningPlanAssignmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    shift: ShiftRead | None = None
    employees: list[CleaningPlanAssignmentEmployeeRead] = Field(default_factory=list)
    road_segments: list[CleaningPlanAssignmentRoadRead] = Field(default_factory=list)
