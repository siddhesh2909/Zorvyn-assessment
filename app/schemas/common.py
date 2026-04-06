from pydantic import BaseModel
from typing import Any


class SuccessResponse(BaseModel):
    success: bool = True
    message: str | None = None
    data: Any = None
