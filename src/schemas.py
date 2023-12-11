from typing import List, Optional

from pydantic import BaseModel

from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, date

from src.database.models import Tag


class Tag(BaseModel):
    name: str


class ImageRequest(BaseModel):
    description: str
    url: str


class ImageResponse(BaseModel):
    id: int
    description: str
    url: str
    tags: list
    created_at: datetime
    updated_at: datetime


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime
    avatar: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class RoleModel(BaseModel):
    name: str


class RequestEmail(BaseModel):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    email: str | None = None
    roles: List[str] = []
