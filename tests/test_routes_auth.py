import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch

from fastapi import BackgroundTasks, Request, status
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session


from src.routes import auth
from src.schemas import UserModel
from src.database.models import User
from src.services.auth import auth_service


class TestAuth(IsolatedAsyncioTestCase):
    async def test_signup_new_user(self):
        body = UserModel(
            email="test@example.com", username="test_user", password="password"
        )
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        db.query.return_value.count.return_value = 0
        db.add.return_value = None
        db.commit.return_value = None
        db.refresh.return_value = None
        background_tasks = MagicMock(spec=BackgroundTasks)
        request = MagicMock(spec=Request)
        result = await auth.signup(body, background_tasks, request, db)
        self.assertEqual(result["user"].email, body.email)
        self.assertEqual(result["user"].username, body.username)
        self.assertEqual(result["detail"], "User successfully created")

    async def test_signup_existing_user(self):
        body = UserModel(
            email="test@example.com", username="test_user", password="password"
        )
        db = MagicMock(spec=Session)
        db.query.return_value.count.return_value = 1
        exist_user = User(email=body.email, username=body.username)
        db.query.return_value.filter.return_value.first.return_value = exist_user
        background_tasks = MagicMock(spec=BackgroundTasks)
        request = MagicMock(spec=Request)
        with self.assertRaises(HTTPException) as cm:
            await auth.signup(body, background_tasks, request, db)
        self.assertEqual(cm.exception.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(cm.exception.detail, "Account already exists")

    async def test_signup_with_multiple_existing_users(self):
        body = UserModel(
            email="test@example.com", username="test_user", password="password"
        )
        db = MagicMock(spec=Session)
        db.query.return_value.count.return_value = 2
        exist_user = User(email=body.email, username=body.username)
        db.query.return_value.filter.return_value.first.return_value = exist_user
        background_tasks = MagicMock(spec=BackgroundTasks)
        request = MagicMock(spec=Request)
        with self.assertRaises(HTTPException) as cm:
            await auth.signup(body, background_tasks, request, db)
        self.assertEqual(cm.exception.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(cm.exception.detail, "Account already exists")

    async def test_login_with_valid_credentials(self):
        username = "test@example.com"
        password = "password"
        access_token = "access_token"
        refresh_token = "refresh_token"
        user = MagicMock()
        user.email = username
        user.is_active = True
        user.password = auth_service.get_password_hash(password)
        user.role = "user"
        db = MagicMock(spec=Session)
        body = OAuth2PasswordRequestForm(username=username, password=password)
        with patch(
            "src.repository.users.get_user_by_email", return_value=user
        ) as get_user_mock, patch(
            "src.services.auth.auth_service.verify_password", return_value=True
        ) as verify_password_mock, patch(
            "src.services.auth.auth_service.create_access_token",
            return_value="access_token",
        ) as create_access_token_mock, patch(
            "src.services.auth.auth_service.create_refresh_token",
            return_value="refresh_token",
        ) as create_refresh_token_mock, patch(
            "src.repository.users.update_token"
        ) as update_token_mock:
            result = await auth.login(body, db)
        access_token = await auth_service.create_access_token(
            {"sub": username, "role": user.role}
        )
        refresh_token = await auth_service.create_refresh_token({"sub": username})
        self.assertEqual(result["access_token"], access_token)
        self.assertEqual(result["refresh_token"], refresh_token)
        self.assertEqual(result["token_type"], "bearer")

    async def test_login_with_invalid_email(self):
        username = "test@example.com"
        password = "password"
        user = None
        db = MagicMock(spec=Session)
        body = OAuth2PasswordRequestForm(username=username, password=password)
        with patch(
            "src.repository.users.get_user_by_email", return_value=user
        ) as get_user_mock:
            with self.assertRaises(HTTPException) as context:
                await auth.login(body, db)
            get_user_mock.assert_called_once_with(username, db)
            self.assertEqual(
                context.exception.status_code, status.HTTP_401_UNAUTHORIZED
            )
            self.assertEqual(
                context.exception.detail, "Invalid email or account is blocked"
            )

    async def test_login_with_inactive_account(self):
        username = "test@example.com"
        password = "password"
        user = MagicMock()
        user.email = username
        user.is_active = False
        db = MagicMock(spec=Session)
        body = OAuth2PasswordRequestForm(username=username, password=password)
        with patch(
            "src.repository.users.get_user_by_email", return_value=user
        ) as get_user_mock:
            with self.assertRaises(HTTPException) as context:
                await auth.login(body, db)
            get_user_mock.assert_called_once_with(username, db)
            self.assertEqual(
                context.exception.status_code, status.HTTP_401_UNAUTHORIZED
            )
            self.assertEqual(
                context.exception.detail, "Invalid email or account is blocked"
            )

    async def test_login_with_invalid_password(self):
        username = "test@example.com"
        password = "password"
        user = MagicMock()
        user.email = username
        user.is_active = True
        user.password = auth_service.get_password_hash("wrong_password")
        db = MagicMock(spec=Session)
        body = OAuth2PasswordRequestForm(username=username, password=password)
        with patch(
            "src.repository.users.get_user_by_email", return_value=user
        ) as get_user_mock, patch(
            "src.services.auth.auth_service.verify_password", return_value=False
        ) as verify_password_mock:
            with self.assertRaises(HTTPException) as context:
                await auth.login(body, db)
            self.assertEqual(
                context.exception.status_code, status.HTTP_401_UNAUTHORIZED
            )
            self.assertEqual(context.exception.detail, "Invalid password")

    async def test_refresh_token_valid(self):
        token = "valid_token"
        email = "test@example.com"
        user = MagicMock()
        user.refresh_token = token
        db = MagicMock(spec=Session)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with patch(
            "src.routes.auth.auth_service.decode_refresh_token", return_value=email
        ):
            with patch(
                "src.routes.auth.repository_users.get_user_by_email", return_value=user
            ):
                with patch(
                    "src.routes.auth.auth_service.create_access_token",
                    return_value="access_token",
                ):
                    with patch(
                        "src.routes.auth.auth_service.create_refresh_token",
                        return_value="new_refresh_token",
                    ):
                        result = await auth.refresh_token(credentials, db)
        self.assertEqual(
            result,
            {
                "access_token": "access_token",
                "refresh_token": "new_refresh_token",
                "token_type": "bearer",
            },
        )

    async def test_refresh_token_invalid(self):
        token = "invalid_token"
        email = "test@example.com"
        user = MagicMock()
        user.refresh_token = "valid_token"
        db = MagicMock(spec=Session)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        with patch(
            "src.routes.auth.auth_service.decode_refresh_token", return_value=email
        ):
            with patch(
                "src.routes.auth.repository_users.get_user_by_email", return_value=user
            ):
                with self.assertRaises(HTTPException) as cm:
                    await auth.refresh_token(credentials, db)
        self.assertEqual(cm.exception.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(cm.exception.detail, "Invalid refresh token")


if __name__ == "__main__":
    unittest.main()
