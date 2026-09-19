from datetime import date, datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


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


class TodoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    priority: str
    due_date: date | None
    completed: bool
    created_at: datetime
    owner_id: int
