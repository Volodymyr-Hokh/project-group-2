from pydantic import BaseModel


class ImageRequest(BaseModel):
    description: str
    url: str
