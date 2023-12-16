from libgravatar import Gravatar
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import UserModel


async def get_user_by_email(email: str, db: Session) -> User:
    """
    Retrieve a user from the database based on their email.

    :param email: The email address of the user to be retrieved.
    :param db: The SQLAlchemy Session instance.

    :return: The User object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User:
    """
    Retrieve a user from the database based on their username.

    :param username: The username of the user to be retrieved.
    :param db: The SQLAlchemy Session instance.

    :return: The User object if found, otherwise None.
    """
    return db.query(User).filter(User.username == username).first()


async def create_user(body: UserModel, db: Session) -> User:
    """
    Create a new user and store it in the database.

    :param body: The user data as a UserModel object.
    :param db: The SQLAlchemy Session instance.

    :return: The created User object.
    """
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        print(e)

    new_user = User(**body.dict(), avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


async def update_token(user: User, token: str | None, db: Session) -> None:
    """
    Update the refresh token for a given user.

    :param user: The User object to update.
    :param token: The new refresh token, can be None.
    :param db: The SQLAlchemy Session instance.

    :return: None
    """
    user.refresh_token = token
    db.commit()


async def confirmed_email(email: str, db: Session) -> None:
    """
    Confirm the email address of a user.

    :param email: The email address to confirm.
    :param db: The SQLAlchemy Session instance.

    :return: None
    """
    user = await get_user_by_email(email, db)
    user.confirmed = True
    db.commit()


async def get_user_role(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    return user.role.name if user and user.role else None


async def update_avatar(email, url: str, db: Session) -> User:
    """
    Update the avatar URL for a user.

    :param email: The email address of the user.
    :param url: The new avatar URL.
    :param db: The SQLAlchemy Session instance.

    :return: The updated User object.
    """
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user


async def update_user(user_id: int, body: UserModel, db: Session) -> User:
    """
    Update the user with the given ID.

    :param user_id: The ID of the user to update.
    :param body: The user data as a UserModel object.
    :param db: The SQLAlchemy Session instance.

    :return: The updated User object.
    """
    user = db.query(User).filter(User.id == user_id).first()
    for key, value in body.dict().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user
