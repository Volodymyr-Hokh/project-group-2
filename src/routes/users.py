from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
import cloudinary
import cloudinary.uploader


from src.database.db import get_db
from src.database.models import User, Image, UserRole
from src.schemas import UserUpdate, UserResponse, UserResponseProfile, UserDb
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.patch("/users/{user_id}")
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the profile of the currently authenticated user.

    :param user_id: The ID of the user to update.
    :param user_update: The updated user details.
    :param current_user: The current authenticated user.
    :param db: The database session.

    :return: The updated user details as a UserDb object.
    """
    if "admin" not in current_user.role:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = await repository_users.update_user(user_id, user_update, db)
    return user


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Get information about the currently authenticated user.

    :param current_user: The current authenticated user.

    :return: The user details as a UserDb object.
    """
    return current_user


@router.patch("/avatar", response_model=UserDb)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the avatar of the currently authenticated user.

    :param file: The uploaded file containing the new avatar image.
    :param current_user: The current authenticated user.
    :param db: The SQLAlchemy Session instance.

    :return: The updated user details as a UserDb object.
    """
    cloudinary.config(
        cloud_name=settings.cloudinary_name,
        api_key=settings.cloudinary_api_key,
        api_secret=settings.cloudinary_api_secret,
        secure=True,
    )

    cloudinary.uploader.upload(
        file.file, public_id=f"NotesApp/{current_user.username}", overwrite=True
    )
    src_url = cloudinary.CloudinaryImage(f"NotesApp/{current_user.username}").build_url(
        width=250, height=250, crop="fill"
    )
    user = await repository_users.update_avatar(current_user.email, src_url, db)
    return user


@router.get("/{username}", response_model=UserResponseProfile)
async def user_profile(username: str, db: Session = Depends(get_db)):
    """
    Get information about a user by their username.

    :param username: The username of the user.
    :param db: The database session.

    :return: The user details as a UserDb object.
    """
    user = repository_users.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    image_count = db.query(Image).filter(Image.user_id == user.id).count()

    last_image_id = (
        db.query(Image)
        .filter(Image.user_id == user.id)
        .order_by(desc(Image.created_at))
        .first()
        .id
        if image_count > 0
        else None
    )

    return {"user": user, "image_count": image_count, "last_image_id": last_image_id}
