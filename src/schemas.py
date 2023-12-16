from pydantic import BaseModel
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class Tag(BaseModel):
    name: str


class ImageResponse(BaseModel):
    id: int
    description: str
    url: str
    tags: list[Tag]
    created_at: datetime
    updated_at: datetime


class UserModel(BaseModel):
    username: str = Field(min_length=5, max_length=16)
    email: str
    password: str = Field(min_length=6, max_length=10)


class UserDb(BaseModel):
    id: int
    confirmed: bool
    username: str
    email: str
    created_at: datetime
    avatar: str
    role: str

    class Config:
        orm_mode = True


class UserResponse(BaseModel):
    user: UserDb
    detail: str = "User successfully created"


class UserResponseProfile(BaseModel):
    user: UserDb
    image_count: int = 0
    last_image_id: Optional[int] = None


class RequestEmail(BaseModel):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str]
    email: Optional[str]
    role: Optional[str]


class UserUpdate(BaseModel):
    username: Optional[str] = Field(min_length=5, max_length=16)
    email: Optional[EmailStr]
    password: Optional[str] = Field(min_length=6, max_length=10)
    new_password: Optional[str] = Field(min_length=6, max_length=10)


class CommentResponse(BaseModel):
    id: int
    text: str
    created_at: datetime
    updated_at: datetime
    user_id: int
    image_id: int
