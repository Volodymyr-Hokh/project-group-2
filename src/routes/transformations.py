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
    Resizes an image to the specified width and height.

    Args:
        request (Request): The HTTP request object.\n
        image_id (int): The ID of the image to be resized.\n
        width (int): The desired width of the resized image.\n
        height (int): The desired height of the resized image.\n
        db: The database dependency.\n
        user: The current user dependency.\n

    Returns:
        The resized image.
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
    """Adds a filter to the specified image.

    Args:
        request (Request): The HTTP request object.\n
        image_id (int): The ID of the image to add the filter to.\n
        filter (str): The filter to be applied to the image.\n
        db (Database): The database connection dependency.\n
        user (User): The current authenticated user.\n

    Returns:
        The result of adding the filter to the image.
    """
    return await image_service.add_filter(
        image_id=image_id, filter=filter, user=user, db=db
    )
