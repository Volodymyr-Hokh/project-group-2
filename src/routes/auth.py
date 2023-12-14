from typing import List

from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request
from fastapi.security import (
    OAuth2PasswordRequestForm,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.schemas import UserModel, UserResponse, Token, RequestEmail
from src.repository import users as repository_users
from src.services.auth import Auth
from src.services.emails import send_email

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()
auth_service = Auth()

@router.post(
    "/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def signup(body: UserModel, db: Session = Depends(get_db)):
    """
    User registration.

    :param body: UserModel containing username, email and password.
    :param db: The SQLAlchemy Session instance.

    :return: A message confirming or rejecting user's registration.
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await repository_users.create_user(body, db)
    return {"user": new_user, "detail": "User successfully created"}


@router.post("/login", response_model=Token)
async def login(
    body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    User's authorization via JWT token.
    
    :param body: OAuth2PasswordRequestForm containing username and password fields as form data.
    :param db: The SQLAlchemy Session instance.


    :return: Generated access token, refresh token and token type.
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
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

@router.get("/current_user_roles")
async def get_roles_of_current_user(
    roles: list[str] = Depends(auth_service.get_current_user_role)
):
    """
    Get the roles of the current authenticated user.

    :param roles: The roles of the current authenticated user.

    :return: The roles of the current authenticated user.
    """
    return {"roles": roles}

@router.get("/refresh_token", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(get_db),
):
    """
    Refreshing token.

    :param credentials: Security endpoind to access the token.
    :param db: The SQLAlchemy Session instance.

   
    :return: Updated access token, refresh token and token type.
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