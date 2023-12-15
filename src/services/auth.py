import pickle
from typing import Optional
from datetime import datetime, timedelta

import redis
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from src.database.models import User
from src.schemas import  TokenData
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
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)

    def verify_password(self, plain_password, hashed_password):
        """
        Verify a plain password against its hashed counterpart.

        :param plain_password: The plain text password to verify.
        :param hashed_password: The hashed password to compare against.

        :return: True if the passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Hash a password.

        :param password: The plain text password to hash.

        :return: The hashed password.
        """
        return self.pwd_context.hash(password)

    async def create_access_token(
        self, data: dict, expires_delta: Optional[float] = None
    ) -> str:
        """
        Generate a new access token.

        :param data: The data to be encoded into the token.
        :param expires_delta: Optional expiration time in seconds.

        :return: The encoded access token.
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
        Generate a new refresh token.

        :param data: The data to be encoded into the token.
        :param expires_delta: Optional expiration time in seconds.

        :return: The encoded refresh token.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update(
            {"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token", "roles": data.get("role")}
        )
        encoded_refresh_token = jwt.encode(
            to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM
        )
        return encoded_refresh_token

    async def decode_refresh_token(self, refresh_token: str):
        """
        Decode and verify a refresh token.

        :param refresh_token: The refresh token to decode.

        :return: The decoded email from the token.
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
        Get the current authenticated user.

        :param token: The access token for authentication.
        :param db: The SQLAlchemy Session instance.

        :return: The current authenticated user.
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
                role = payload.get("role")
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

        user.role = role
        return user

    # async def get_roles_of_current_user(
    #     token: str = Depends(oauth2_scheme),
    #     db: Session = Depends(get_db),
    #     current_user: User = Depends(get_current_user)
    # ):
    #     """
    #     Get the roles of the current authenticated user.

    #     :param token: The access token for authentication.
    #     :param db: The SQLAlchemy Session instance.
    #     :param current_user: The current authenticated user.

    #     :return: The roles of the current authenticated user.
    #     """
    #     return current_user.role

    async def update_user_role(
        self, new_role: str, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
    ):
        """
        Update the role of the current authenticated user.

        :param new_role: The new role to assign to the user.
        :param token: The access token for authentication.
        :param db: The SQLAlchemy Session instance.

        :return: The updated TokenData object.
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

    def create_email_token(self, data: dict):
        """
        Generate a token for email verification.

        :param data: The data to be encoded into the token.

        :return: The generated email verification token.
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return token

    async def get_email_from_token(self, token: str):
        """
        Decode and retrieve the email from an email verification token.

        :param token: The email verification token.

        :return: The email extracted from the token.
        """
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid token for email verification",
            )


auth_service = Auth()
