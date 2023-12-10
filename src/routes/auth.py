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
from src.schemas import UserModel, UserResponse, TokenData, RequestEmail
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.services.emails import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


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
    Create a new user account and send a confirmation email.

    :param body: The user data as a UserModel object.
    :param background_tasks: BackgroundTasks instance for handling asynchronous tasks.
    :param request: FastAPI Request instance.
    :param db: The SQLAlchemy Session instance.

    :return: UserResponse containing the created user and a confirmation message.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(
        send_email, new_user.email, new_user.username, request.base_url
    )
    return {
        "user": new_user,
        "detail": "User successfully created. Check your email for confirmation.",
    }


@router.post("/login", response_model=TokenData)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Log in a user and generate access and refresh tokens.

    :param body: OAuth2PasswordRequestForm containing username (email) and password.
    :param db: The SQLAlchemy Session instance.

    :return: TokenData containing access and refresh tokens.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/refresh_token", response_model=TokenData)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """
    Refresh access token using a valid refresh token.

    :param credentials: HTTPAuthorizationCredentials containing the refresh token.
    :param db: The SQLAlchemy Session instance.

    :return: TokenModel containing new access and refresh tokens.
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
    Confirm user's email using the confirmation token.

    :param token: The confirmation token sent via email.
    :param db: The SQLAlchemy Session instance.

    :return: A message confirming or rejecting the email confirmation.
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
    Send a confirmation email for email verification or re-send the confirmation email.

    :param body: RequestEmail containing the email address.
    :param background_tasks: BackgroundTasks instance for handling asynchronous tasks.
    :param request: FastAPI Request instance.
    :param db: The SQLAlchemy Session instance.

    :return: A message instructing the user to check their email for confirmation.
    """
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(
            send_email, user.email, user.username, request.base_url
        )
    return {"message": "Check your email for confirmation."}
