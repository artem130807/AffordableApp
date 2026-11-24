from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: EmailStr
    name: str = Field(min_length=2, max_length=120)
    password: SecretStr = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr


class RefreshRequest(BaseModel):
    refresh_token: SecretStr


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class PermissionResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: str | None

    model_config = {"from_attributes": True}


class PermissionCreateRequest(BaseModel):
    code: str = Field(pattern=r"^[a-z][a-z0-9_.:-]*$", min_length=3, max_length=100)
    name: str = Field(min_length=2, max_length=150)
    description: str | None = Field(default=None, max_length=500)


class RoleResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    permissions: tuple[PermissionResponse, ...]

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    is_active: bool
    roles: list[RoleResponse]

    model_config = {"from_attributes": True}


class RoleCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=64)
    description: str | None = Field(default=None, max_length=255)
    permissions: frozenset[str]


class AssignRoleRequest(BaseModel):
    role_id: UUID


class AssignPermissionRequest(BaseModel):
    permission_id: UUID
