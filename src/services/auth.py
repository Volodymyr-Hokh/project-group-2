import pickle
from typing import Optional
from datetime import datetime, timedelta

import redis
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import TokenData
from src.database.db import get_db
from src.repository import users as repository_users
from src.conf.config import settings


class Auth:
    """
    Class handling authentication-related operations such as password hashing, token generation, and user verification.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies if the plain password matches the hashed password.

        Args:
            plain_password (str): The plain password to be verified.\n
            hashed_password (str): The hashed password to compare against.\n

        Returns:
            bool: True if the plain password matches the hashed password, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Returns the hashed version of the provided password.

        Args:
            password (str): The password to be hashed.

        Returns:
            str: The hashed password.
        """
        return self.pwd_context.hash(password)

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        """
        Creates an access token for the given data.

        Args:
            data (dict): The data to be encoded in the access token.\n
            expires_delta (float, optional): The expiration time in seconds for the access token. Defaults to None.\n

        Returns:
            str: The encoded access token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=150)
        to_encode.update(
            {
                "iat": datetime.utcnow(),
                "exp": expire,
                "scope": "access_token",
                "role": data.get("role"),
            }
        )
        encoded_access_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_access_token

    async def create_refresh_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        """
        Creates a refresh token for the given data.

        Args:
            data (dict): The data to be encoded in the refresh token.\n
            expires_delta (Optional[float], optional): The expiration time in seconds. Defaults to None.\n

        Returns:
            str: The encoded refresh token.

        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {
                "iat": datetime.utcnow(),
                "exp": expire,
                "scope": "refresh_token",
                "roles": data.get("role"),
            }
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decodes the given refresh token and returns the email associated with it.

        Args:
            refresh_token (str): The refresh token to decode.

        Returns:
            str: The email associated with the refresh token.

        Raises:
            HTTPException: If the refresh token has an invalid scope or if the credentials cannot be validated.
        """
        try:
            payload = jwt.decode(
                refresh_token, self.SECRET_KEY, algorithms=[self.ALGORITHM]
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    async def get_current_user(
        self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ) -> User:
        """
        Retrieves the current authenticated user based on the provided token.

        Args:
            token (str): The authentication token.\n
            db (Session): The database session.\n

        Returns:
            User: The current authenticated user.

        Raises:
            HTTPException: If the credentials cannot be validated.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        email = None
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                role = payload.get("role")
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        except Exception as e:
            print(e)

        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                return None
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)

        user.role = role
        return user

    async def update_user_role(
        self,
        new_role: str,
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ):
        """
        Updates the role of a user.

        Args:
            new_role (str): The new role to assign to the user.\n
            token (str, optional): The authentication token. Defaults to Depends(oauth2_scheme).\n
            db (Session, optional): The database session. Defaults to Depends(get_db).\n

        Returns:
            TokenData: The updated token data containing the user's email and new role.
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)

        user.role = new_role
        db.commit()

        updated_token_data = TokenData(email=user.email, role=new_role)

        return updated_token_data

    async def get_email_from_token(self, token: str):
        """
        Retrieves the email associated with the given token.

        Args:
            token (str): The token to decode.

        Returns:
            str: The email associated with the token.

        Raises:
            HTTPException: If the token has an invalid scope or if the credentials cannot be validated.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            if payload["scope"] in ("access_token", "email_verification"):
                email = payload["sub"]
                return email
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid scope for token",
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

    def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token


auth_service = Auth()
