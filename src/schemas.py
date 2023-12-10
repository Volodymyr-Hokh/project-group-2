from datetime import datetime

from pydantic import BaseModel

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
