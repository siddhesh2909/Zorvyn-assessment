from pydantic import BaseModel, Field
from typing import Literal


class UpdateRoleRequest(BaseModel):
    role: Literal["viewer", "analyst", "admin"]


class UpdateStatusRequest(BaseModel):
    status: Literal["active", "inactive"]


class GetUsersQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    role: Literal["viewer", "analyst", "admin"] | None = None
    status: Literal["active", "inactive"] | None = None
    search: str | None = Field(default=None, max_length=100)
