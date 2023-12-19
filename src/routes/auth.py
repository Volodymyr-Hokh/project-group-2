from typing import List

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Security,
    BackgroundTasks,
    Request,
)
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User, UserRole
from src.schemas import UserModel, UserResponse, Token, RequestEmail, UserDb
from src.repository import users as repository_users
from src.services.auth import Auth
from src.services.emails import send_email


router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
auth_service = Auth()


@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(
    body: UserModel,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Creates a new user account.

    Args:
        body (UserModel): The user data for creating a new account.\n
        background_tasks (BackgroundTasks): The background tasks manager.\n
        request (Request): The HTTP request object.\n
        db (Session, optional): The database session. Defaults to Depends(get_db).\n

    Returns:
        dict: A dictionary containing the newly created user and a success message.

    Raises:
        HTTPException: If an account with the same email already exists.

    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )

    roles = [UserRole.admin] if not db.query(User).count() else [UserRole.user]
    role = roles[0].value

    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, body.email, body.username, request.base_url)
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=Token)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Logs in a user and returns access and refresh tokens.

    Args:
        body (OAuth2PasswordRequestForm): The request body containing the username and password.\n
        db (Session): The database session.\n

    Returns:
        dict: A dictionary containing the access token, refresh token, and token type.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or account is blocked",
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    access_token = await auth_service.create_access_token(
        data={"sub": user.email, "role": user.role}
    )
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """
    Refreshes the access token and generates a new refresh token for the authenticated user.

    Args:
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials containing the refresh token.\n
        db (Session): The database session.\n

    Returns:
        dict: A dictionary containing the new access token, refresh token, and token type.

    Raises:
        HTTPException: If the provided refresh token is invalid.
    """
    token = credentials.credentials
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
        )

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Confirms the email associated with the given token.

    Args:
        token (str): The token used for email verification.\n
        db (Session, optional): The database session. Defaults to Depends(get_db).\n

    Returns:
        dict: A dictionary containing a message indicating the status of the email confirmation.

    Raises:
        HTTPException: If the user is not found or if the email is already confirmed.
    """
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Sends a confirmation email to the user's email address.

    Args:
        body (RequestEmail): The request body containing the user's email.\n
        background_tasks (BackgroundTasks): The background tasks manager.\n
        request (Request): The HTTP request object.\n
        db (Session, optional): The database session. Defaults to Depends(get_db).\n

    Returns:
        dict: A dictionary containing the message indicating the status of the email confirmation request.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation."}
