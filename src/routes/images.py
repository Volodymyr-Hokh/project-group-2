from fastapi import APIRouter, Request, Depends, HTTPException

from src.database.db import get_db
from src.limiter import limiter
from src.repository import images as images_repository
from src.schemas import ImageRequest, ImageResponse
from src.services.auth import auth_service

router = APIRouter(prefix="/images", tags=["images"])


@router.post("/", response_model=ImageResponse)
@limiter.limit(limit_value="10/minute")
async def add_image(
    request: Request,
    body: ImageRequest,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    return await images_repository.add_image(image=body, user=user, db=db)


@router.delete("/{image_id}", response_model=ImageResponse)
@limiter.limit(limit_value="10/minute")
async def delete_image(
    request: Request,
    image_id: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
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
    return await images_repository.get_images(user=user, db=db)


@router.get("/{image_id}", response_model=ImageResponse)
@limiter.limit(limit_value="10/minute")
async def get_image(
    request: Request,
    image_id: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    image = await images_repository.get_image(image_id=image_id, user=user, db=db)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image
