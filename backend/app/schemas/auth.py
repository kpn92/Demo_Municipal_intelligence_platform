from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=1, max_length=255)


class AuthRoleRead(BaseModel):
    code: str
    name: str


class AuthUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    full_name: str
    role: str
    roles: list[AuthRoleRead]
    modules: list[str]
    sector_scope: str | None = None
    is_superuser: bool = False


class LoginResponse(BaseModel):
    user: AuthUserRead
