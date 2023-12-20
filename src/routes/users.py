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
    Updates the user with the specified user_id.

    Args:
        user_id (int): The ID of the user to update.\n
        user_update (UserUpdate): The updated user data.\n
        current_user (User, optional): The current authenticated user. Defaults to Depends(auth_service.get_current_user).\n
        db (Session, optional): The database session. Defaults to Depends(get_db).\n

    Raises:
        HTTPException: If the current user does not have sufficient permissions.

    Returns:
        User: The updated user.
    """
    if "admin" not in current_user.role:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    user = await repository_users.update_user(user_id, user_update, db)
    return user


@router.get("/me/", response_model=UserDb)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieves the details of the currently authenticated user.

    Args:
        current_user (User): The currently authenticated user.

    Returns:
        User: The details of the currently authenticated user.

    """
    return current_user


@router.patch("/avatar", response_model=UserDb)
async def update_avatar_user(
    file: UploadFile = File(),
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Updates the avatar of the current user.

    Args:
        file (UploadFile, optional): The file containing the new avatar image. Defaults to None.\n
        current_user (User, optional): The current authenticated user. Defaults to None.\n
        db (Session, optional): The database session. Defaults to None.\n

    Returns:
        User: The updated user object.

    Raises:
        None

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
    Retrieves the profile information of a user.

    Args:
        username (str): The username of the user.\n
        db (Session, optional): The database session. Defaults to Depends(get_db).\n

    Returns:
        dict: A dictionary containing the user's profile information, including the user object, the number of images associated with the user, and the ID of the last image uploaded by the user.

    Raises:
        HTTPException: If the user is not found in the database.
    """
    user = await repository_users.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    images = db.query(Image).filter(Image.user_id == user.id).all()
    image_count = len(images)

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
