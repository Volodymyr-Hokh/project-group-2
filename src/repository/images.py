from datetime import datetime
from typing import List

import cloudinary.uploader
from sqlalchemy import text, and_
from sqlalchemy.orm import Session

from src.database.models import Image, User
from src.utils.tags import get_tags_from_description


async def add_image(
    image_url: str, public_id: str, description: str, user: User, db: Session
):
    """Adds an image to the repository.

    Args:
        image_url (str): The URL of the image.\n
        public_id (str): The public ID of the image.\n
        description (str): The description of the image.\n
        user (User): The user who uploaded the image.\n
        db (Session): The database session.\n

    Returns:
        Image: The added image object.
    """
    image = Image(
        url=image_url,
        public_id=public_id,
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
    """Deletes an image from the database and Cloudinary.

    Args:
        image_id (int): The ID of the image to be deleted.\n
        user (User): The user who owns the image.\n
        db (Session): The database session.\n

    Returns:
        Image: The deleted image object, or None if the image does not exist.

    """
    image = (
        db.query(Image)
        .filter(and_(Image.id == image_id, Image.user_id == user.id))
        .first()
    )
    if image:
        cloudinary.uploader.destroy(image.public_id)
        db.delete(image)
        db.commit()
    return image


async def edit_description(image_id: int, description: str, user: User, db: Session):
    """Updates the description of an image.

    Args:
        image_id (int): The ID of the image to be edited.\n
        description (str): The new description for the image.\n
        user (User): The user who is editing the image.\n
        db (Session): The database session.\n

    Returns:
        Image: The updated image object.

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
    """Retrieves all images associated with a user.

    Args:
        user (User): The user object.\n
        db (Session): The database session.\n

    Returns:
        List[Image]: A list of Image objects associated with the user.
    """
    return db.query(Image).filter(Image.user_id == user.id).all()


async def get_image(image_id: int, user: User, db: Session):
    """Retrieves an image from the database.

    Args:
        image_id (int): The ID of the image to retrieve.\n
        user (User): The user object representing the owner of the image.\n
        db (Session): The database session.\n

    Returns:
        Image: The image object if found, None otherwise.
    """
    return (
        db.query(Image)
        .filter(and_(Image.id == image_id, Image.user_id == user.id))
        .first()
    )
