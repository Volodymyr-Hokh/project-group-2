import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock, patch

from sqlalchemy.orm import Session

from src.repository.users import (
    get_user_by_email,
    get_user_by_username,
    create_user,
    update_user,
    update_token,
    confirmed_email,
    update_avatar,
)
from src.database.models import User, UserRole
from src.schemas import UserModel


class TestUsers(IsolatedAsyncioTestCase):
    async def test_get_user_by_email_existing(self):
        email = "existing_user@example.com"
        user = User(email=email)
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = user
        result = await get_user_by_email(email, db)
        self.assertEqual(result, user)

    async def test_get_user_by_email_non_existing(self):
        email = "non_existing_user@example.com"
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        result = await get_user_by_email(email, db)
        self.assertIsNone(result)

    async def test_get_user_by_username_existing(self):
        username = "existing_user"
        user = User(username=username)
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = user
        result = await get_user_by_username(db, username)
        self.assertEqual(result, user)

    async def test_get_user_by_username_non_existing(self):
        username = "non_existing_user"
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        result = await get_user_by_username(db, username)
        self.assertIsNone(result)

    async def test_create_user_with_admin_role(self):
        body = UserModel(
            email="test@example.com", username="test_user", password="password"
        )
        db = MagicMock(spec=Session)
        db.query.return_value.count.return_value = 0
        db.add.return_value = None
        db.commit.return_value = None
        db.refresh.return_value = None
        result = await create_user(body, db)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.password, body.password)
        self.assertEqual(result.role, UserRole.admin.value)

    async def test_create_user_with_user_role(self):
        body = UserModel(
            email="test@example.com", username="test_user", password="password"
        )
        db = MagicMock(spec=Session)
        db.query.return_value.count.return_value = 1
        db.add.return_value = None
        db.commit.return_value = None
        db.refresh.return_value = None
        result = await create_user(body, db)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.username, body.username)
        self.assertEqual(result.password, body.password)
        self.assertEqual(result.role, UserRole.user.value)

    async def test_update_user(self):
        user_id = 1
        body = UserModel(
            email="updated@example.com", username="updated_user", password="password"
        )
        user = User(id=user_id, email="old@example.com", username="old_user")
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = user
        db.commit.return_value = None
        db.refresh.return_value = None
        result = await update_user(user_id, body, db)
        self.assertEqual(result.id, user_id)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.username, body.username)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(user)

    async def test_update_token_with_token(self):
        user = User()
        token = "new_token"
        db = MagicMock(spec=Session)
        db.commit.return_value = None
        await update_token(user, token, db)
        self.assertEqual(user.refresh_token, token)
        db.commit.assert_called_once()

    async def test_update_token_without_token(self):
        user = User(refresh_token="old_token")
        token = None
        db = MagicMock(spec=Session)
        db.commit.return_value = None
        await update_token(user, token, db)
        self.assertIsNone(user.refresh_token)
        db.commit.assert_called_once()

    async def test_confirmed_email(self):
        email = "test@example.com"
        user = User(email=email)
        db = MagicMock(spec=Session)
        with patch(
            "src.repository.users.get_user_by_email", return_value=user
        ) as get_user_mock:
            await confirmed_email(email, db)

            get_user_mock.assert_called_once_with(email, db)
        self.assertTrue(user.confirmed)
        db.commit.assert_called_once()

    async def test_update_avatar(self):
        email = "test@example.com"
        url = "https://example.com/avatar.jpg"
        user = User(email=email)
        db = MagicMock(spec=Session)
        db.commit.return_value = None
        with patch(
            "src.repository.users.get_user_by_email", return_value=user
        ) as get_user_mock:
            result = await update_avatar(email, url, db)
            get_user_mock.assert_called_once_with(email, db)
        self.assertEqual(result, user)
        self.assertEqual(result.avatar, url)
        db.commit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
