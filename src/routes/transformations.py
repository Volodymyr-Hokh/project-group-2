from cloudinary import CloudinaryImage
from fastapi import APIRouter, Request, Depends

from src.database.db import get_db
from src.limiter import limiter
from src.services.images import image_service
from src.services.auth import auth_service

router = APIRouter(prefix="/transformations", tags=["transformations"])


@router.post("/resize/{image_id}")
@limiter.limit(limit_value="10/minute")
async def resize(
    request: Request,
    image_id: int,
    width: int,
    height: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """
    Resize image.
    """
    return await image_service.resize_image(
        image_id=image_id, width=width, height=height, user=user, db=db
    )


@router.post("/filter/{image_id}")
@limiter.limit(limit_value="10/minute")
async def add_filter(
    request: Request,
    image_id: int,
    filter: str,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """ """
    return await image_service.add_filter(
        image_id=image_id, filter=filter, user=user, db=db
    )
