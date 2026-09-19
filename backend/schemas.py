from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str = Field(min_length=1, max_length=150)
    password: str = Field(min_length=1)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime


class TodoCreate(BaseModel):
    title: str
    priority: Literal["Low", "Medium", "High"] = "Medium"
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("title must not be empty")
        return v


class TodoUpdate(BaseModel):
    title: str | None = None
    completed: bool | None = None
    priority: Literal["Low", "Medium", "High"] | None = None
    due_date: date | None = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("title must not be empty")
        return v


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TodoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    priority: str
    due_date: date | None
    completed: bool
    created_at: datetime
    owner_id: int
