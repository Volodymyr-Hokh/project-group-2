from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response

from src.database.db import get_db
from src.limiter import limiter
from src.repository import images as images_repository
from src.repository import comments as comments_repository
from src.schemas import ImageResponse, CommentResponse
from src.services.auth import auth_service
from src.services.images import image_service

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/", response_model=ImageResponse)
@limiter.limit(limit_value="10/minute")
async def add_image(
    request: Request,
    file: UploadFile = File(...),
    description: str = "",
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """
    Uploads an image and adds it to the database.

    Args:
        request (Request): The incoming request object.\n
        file (UploadFile): The image file to be uploaded.\n
        description (str, optional): The description of the image. Defaults to "".\n
        db: The database connection dependency.\n
        user: The current user dependency.\n

    Returns:
        dict: The added image information.

    Raises:
        HTTPException: If there is an error uploading the image or adding it to the database.
    """
    image_info = await image_service.upload_image(file=file)
    return await images_repository.add_image(
        image_url=image_info["url"],
        public_id=image_info["public_id"],
        description=description,
        user=user,
        db=db,
    )


@router.delete("/{image_id}", response_model=ImageResponse)
@limiter.limit(limit_value="10/minute")
async def delete_image(
    request: Request,
    image_id: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """
    Deletes an image from the database.

    Args:
        request (Request): The incoming request object.\n
        image_id (int): The ID of the image to be deleted.\n
        db: The database dependency.\n
        user: The current user dependency.\n

    Returns:
        The deleted image.

    Raises:
        HTTPException: If the image is not found.
    """
    image = await images_repository.delete_image(image_id=image_id, user=user, db=db)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.put("/{image_id}", response_model=ImageResponse)
@limiter.limit(limit_value="10/minute")
async def edit_description(
    request: Request,
    image_id: int,
    description: str,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """
    Edits the description of an image.

    Args:
        request (Request): The HTTP request object.\n
        image_id (int): The ID of the image to edit.\n
        description (str): The new description for the image.\n
        db: The database dependency.\n
        user: The current user dependency.\n

    Returns:
        The edited image.

    Raises:
        HTTPException: If the image is not found.
    """
    image = await images_repository.edit_description(
        image_id=image_id, description=description, user=user, db=db
    )
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.get("/", response_model=list[ImageResponse])
@limiter.limit(limit_value="10/minute")
async def get_images(
    request: Request,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """
    Retrieves images for the current user.

    Args:
        request (Request): The incoming request object.\n
        db: The database dependency.\n
        user: The current user dependency.\n

    Returns:
        List[Image]: A list of images belonging to the current user.
    """
    return await images_repository.get_images(user=user, db=db)


@router.get("/{image_id}", response_model=ImageResponse)
@limiter.limit(limit_value="10/minute")
async def get_image(
    request: Request,
    image_id: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """
    Retrieves an image with the specified image_id.

    Args:
        request (Request): The incoming request object.\n
        image_id (int): The ID of the image to retrieve.\n
        db: The database dependency.\n
        user: The user dependency.\n

    Returns:
        The retrieved image.

    Raises:
        HTTPException: If the image is not found.
    """
    image = await images_repository.get_image(image_id=image_id, user=user, db=db)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.get("/{image_id}/comments", response_model=list[CommentResponse])
@limiter.limit(limit_value="10/minute")
async def get_comments_by_image_id(
    request: Request,
    image_id: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """
    Retrieves comments for a specific image by its ID.

    Args:
        request (Request): The incoming request object.\n
        image_id (int): The ID of the image.\n
        db: The database dependency.\n
        user: The current user dependency.\n

    Returns:
        List[Comment]: A list of comments associated with the image.
    """
    return await comments_repository.get_comments_by_image_id(image_id=image_id, db=db)


@router.post("/generate_qr_code")
@limiter.limit(limit_value="10/minute")
async def generate_qr_code(
    image_url: str, request: Request, user=Depends(auth_service.get_current_user)
):
    """Generates a QR code for the given image URL.

    Args:
        image_url (str): The URL of the image to generate the QR code for.\n
        request (Request): The incoming request object.\n
        user: The current user (optional).\n

    Returns:
        Response: The response containing the generated QR code as content.
    """
    if user:
        qr_code = await image_service.generate_qr_code(image_url=image_url)
        return Response(
            content=qr_code,
            media_type="image/png",
            headers={"content-disposition": "inline"},
            status_code=200,
        )
