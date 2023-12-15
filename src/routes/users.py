from fastapi import APIRouter, Depends, status, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
import cloudinary
import cloudinary.uploader


from src.database.db import get_db
from src.database.models import User, Image
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.conf.config import settings
from src.schemas import UserDb, UserUpdate, UserResponseProfile


router = APIRouter(prefix="/users", tags=["users"])


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


@router.put("/{username}/edit", response_model=UserDb)
async def user_profile_edit(
    user_update: UserUpdate,
    current_user: User = Depends(auth_service.get_current_user),
    db: Session = Depends(get_db),
):
    """
    Edit the profile of the currently authenticated user.

    :param user_update: The updated user details.
    :param current_user: The current authenticated user.
    :param db: The database session.

    :return: The updated user details as a UserDb object.
    """
    if current_user.username != user_update.username:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if user_update.password != current_user.password:
        raise HTTPException(status_code=403, detail="Incorrect password")
    user_update.password = auth_service.get_password_hash(user_update.new_password)
    user = repository_users.update_user(db, user_update)
    return user


@router.patch("/admin/ban/{user_id}", response_model=UserDb)
async def ban_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    """
    Ban a user by setting their is_active field to False.

    :param user_id: The ID of the user to ban.
    :param db: The database session.
    :param current_user: The current authenticated user.

    :return: The updated user details as a UserDb object.
    """
    # if "admin" not in current_user.role:
    #     raise HTTPException(status_code=403, detail="Not enough permissions")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    db.commit()

    return user
