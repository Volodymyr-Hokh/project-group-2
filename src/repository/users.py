from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel

from src.database.models import User, UserRole
from src.schemas import UserModel, TokenData
from typing import List


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieves a user from the database based on the provided email.

    Args:
        email (str): The email of the user to retrieve.\n
        db (Session): The database session.\n

    Returns:
        User: The user object if found, None otherwise.
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User:
    """
    Retrieves a user from the database based on the provided username.

    Args:
        db (Session): The database session.\n
        username (str): The username of the user to retrieve.\n

    Returns:
        User: The user object if found, None otherwise.
    """
    return db.query(User).filter(User.username == username).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Creates a new user in the database.

    Args:
        body (UserModel): The user model containing the user's information.\n
        db (Session): The database session.\n

    Returns:
        User: The newly created user.

    Raises:
        Exception: If there is an error while retrieving the user's avatar from Gravatar.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)

    new_user = User(**body.dict(), avatar=avatar)

    if not db.query(User).count():
        roles = [UserRole.admin]
    else:
        roles = [UserRole.user]

    new_user = User(**body.dict(), avatar=avatar, role=roles[0].value)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


async def update_user(user_id: int, body: UserModel, db: Session) -> User:
    """
    Updates a user in the database.

    Args:
        user_id (int): The ID of the user to be updated.\n
        body (UserModel): The updated user data.\n
        db (Session): The database session.\n

    Returns:
        User: The updated user object.
    """
    user = db.query(User).filter(User.id == user_id).first()
    for key, value in body.model_dump().items():
        if value is not None:
            setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Updates the refresh token for a user in the database.

    Args:
        user (User): The user object to update the token for.\n
        token (str | None): The new refresh token. Pass None to remove the token.\n
        db (Session): The database session.\n

    Returns:
        None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirms the email address of a user.

    Args:
        email (str): The email address of the user.\n
        db (Session): The database session.\n

    Returns:
        None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def get_user_role(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    return user.role.name if user and user.role else None


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Updates the avatar URL for a user.

    Args:
        email (str): The email of the user.\n
        url (str): The new avatar URL.\n
        db (Session): The database session.\n

    Returns:
        User: The updated user object.

    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
