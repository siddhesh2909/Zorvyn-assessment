from pydantic import BaseModel, Field, field_validator
from typing import Literal
import re


class CreateRecordRequest(BaseModel):
    amount: float = Field(..., gt=0)
    type: Literal["income", "expense"]
    category: str = Field(..., min_length=1, max_length=50)
    date: str = Field(...)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("date")
    @classmethod
    def date_format(cls, v: str) -> str:
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    @field_validator("amount")
    @classmethod
    def amount_precision(cls, v: float) -> float:
        return round(v, 2)


class UpdateRecordRequest(BaseModel):
    amount: float | None = Field(default=None, gt=0)
    type: Literal["income", "expense"] | None = None
    category: str | None = Field(default=None, min_length=1, max_length=50)
    date: str | None = None
    description: str | None = Field(default=None, max_length=500)

    @field_validator("date")
    @classmethod
    def date_format(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v

    @field_validator("amount")
    @classmethod
    def amount_precision(cls, v: float | None) -> float | None:
        if v is not None:
            return round(v, 2)
        return v


class GetRecordsQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    type: Literal["income", "expense"] | None = None
    category: str | None = Field(default=None, max_length=50)
    startDate: str | None = None
    endDate: str | None = None
    minAmount: float | None = Field(default=None, gt=0)
    maxAmount: float | None = Field(default=None, gt=0)
    search: str | None = Field(default=None, max_length=100)
    sortBy: Literal["date", "amount", "type", "category", "created_at"] = "date"
    order: Literal["ASC", "DESC", "asc", "desc"] = "DESC"

    @field_validator("startDate", "endDate")
    @classmethod
    def date_format(cls, v: str | None) -> str | None:
        if v is not None and not re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            raise ValueError("Date must be in YYYY-MM-DD format")
        return v
