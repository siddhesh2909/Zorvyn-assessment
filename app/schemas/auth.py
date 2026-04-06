from pydantic import BaseModel, Field, field_validator
from typing import Literal
import re


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str = Field(...)
    password: str = Field(..., min_length=6, max_length=128)
    role: Literal["viewer", "analyst", "admin"] = "viewer"

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError("Username must only contain alphanumeric characters")
        return v

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Please provide a valid email address")
        return v.lower()


class LoginRequest(BaseModel):
    email: str = Field(...)
    password: str = Field(...)

    @field_validator("email")
    @classmethod
    def email_valid(cls, v: str) -> str:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, v):
            raise ValueError("Please provide a valid email address")
        return v.lower()
