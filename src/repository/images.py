from datetime import datetime
from typing import List
from uuid import uuid4

import cloudinary
import cloudinary.uploader
from sqlalchemy import text, and_
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.database.models import Image, User
from src.utils.tags import get_tags_from_description


async def upload_image(file):
    """
    
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )
    unique_filename = str(uuid4())
    r = cloudinary.uploader.upload(
        file.file, public_id=f"KillerInstagram/{unique_filename}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(
        f"KillerInstagram/{unique_filename}"
    ).build_url(version=r.get("version"))
    return src_url


async def add_image(image_url: str, description: str, user: User, db: Session):
    """

    """
    image = Image(
        url=image_url,
        description=description,
        user_id=user.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    image.tags = await get_tags_from_description(image.description, db)
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


async def delete_image(image_id: int, user: User, db: Session):
    """
    
    """
    image = (
        db.query(Image)
        .filter(and_(Image.id == image_id, Image.user_id == user.id))
        .first()
    )
    if image:
        db.delete(image)
        db.commit()
    return image


async def edit_description(image_id: int, description: str, user: User, db: Session):
    """
    
    """
    image = (
        db.query(Image)
        .filter(and_(Image.id == image_id, Image.user_id == user.id))
        .first()
    )
    if image:
        image.description = description
        image.tags = await get_tags_from_description(description, db)
        image.updated_at = datetime.now()
        db.commit()
    return image


async def get_images(user: User, db: Session):
    """

    """
    return db.query(Image).filter(Image.user_id == user.id).all()


async def get_image(image_id: int, user: User, db: Session):
    """
    
    """
    return (
        db.query(Image)
        .filter(and_(Image.id == image_id, Image.user_id == user.id))
        .first()
    )
