from fastapi import APIRouter, Request, Depends, HTTPException, UploadFile, File
from fastapi.responses import Response
from fastapi.templating import Jinja2Templates

from src.database.db import get_db
from src.limiter import limiter
from src.repository import images as images_repository
from src.schemas import ImageResponse
from src.services.auth import auth_service
from src.services.images import image_service

router = APIRouter(prefix="/images", tags=["images"])
# templates = Jinja2Templates(directory="src/services/templates/qr_codes")


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
    Adding image to db.

    :param request: FastAPI Request instance.
    :param file: A file uploaded in a request.
    :param description: Image description.
    :param db: The SQLAlchemy Session instance.
    :param user: Get the current authenticated user.

    :return:
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
    Deleting users image.

    :param request: FastAPI Request instance.
    :param image_id: Image id number.
    :param db: The SQLAlchemy Session instance.
    :param user: Get the current authenticated user.


    :return:  A message confirming or rejecting delete.
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
    Edit picture description.

    :param request: FastAPI Request instance.
    :param image_id: Image id number.
    :param description: Image description.
    :param db: The SQLAlchemy Session instance.
    :param user: Get the current authenticated user.

    :return: The updated description details as a UserDb object.
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
    Gets images by users_id.

    :param request: FastAPI Request instance.
    :param db: The SQLAlchemy Session instance.
    :param user: Get the current authenticated user.

    :return: Images by users_id as a UserDb object.
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
    Get image by user_id and image_id.

    :param request: FastAPI Request instance.
    :param image_id: Image id number.
    :param db: The SQLAlchemy Session instance.
    :param user: Get the current authenticated user.

    :return: Gets image by user_id and image_id as a ImageDb object.
    """
    image = await images_repository.get_image(image_id=image_id, user=user, db=db)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image


@router.post("/generate_qr_code")
@limiter.limit(limit_value="10/minute")
async def generate_qr_code(
    image_url: str, request: Request, user=Depends(auth_service.get_current_user)
):
    """ """
    if user:
        qr_code = await image_service.generate_qr_code(image_url=image_url)
        return Response(
            content=qr_code,
            media_type="image/png",
            headers={"content-disposition": "inline"},
            status_code=200,
        )
