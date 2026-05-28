from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class EmployeeBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    employee_code: str = Field(..., min_length=1, max_length=20)
    role: str = Field(..., min_length=1, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    employment_type: str = Field(default="permanent", min_length=1, max_length=20)
    contract_start_date: date | None = None
    contract_end_date: date | None = None
    sector_id: int


class EmployeeCreate(EmployeeBase):
    pass


class EmployeeUpdate(BaseModel):
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    employee_code: str | None = Field(default=None, min_length=1, max_length=20)
    role: str | None = Field(default=None, min_length=1, max_length=50)
    phone: str | None = Field(default=None, max_length=20)
    employment_type: str | None = Field(default=None, min_length=1, max_length=20)
    contract_start_date: date | None = None
    contract_end_date: date | None = None
    sector_id: int | None = None
    is_active: bool | None = None


class EmployeeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    employee_code: str
    role: str
    phone: str | None
    employment_type: str
    contract_start_date: date | None
    contract_end_date: date | None
    is_active: bool
    sector_id: int
