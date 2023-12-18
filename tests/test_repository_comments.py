import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.repository.comments import (
    add_comment,
    edit_comment,
    delete_comment,
    get_comments_by_image_id,
)
from src.database.models import Comment, User


class TestComments(IsolatedAsyncioTestCase):
    async def test_add_comment(self):
        text = "This is a test comment"
        image_id = 1
        user = User(id=1)
        db = MagicMock(spec=Session)
        comment = Comment(
            text=text,
            image_id=image_id,
            user_id=user.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add.return_value = None
        db.commit.return_value = None
        db.refresh.return_value = None
        result = await add_comment(text, image_id, user, db)
        self.assertEqual(result.text, comment.text)
        self.assertEqual(result.image_id, comment.image_id)
        self.assertEqual(result.user_id, comment.user_id)
        self.assertEqual(result.created_at.date(), comment.created_at.date())
        self.assertEqual(result.updated_at.date(), comment.updated_at.date())

    async def test_edit_comment_success(self):
        text = "Updated comment"
        comment_id = 1
        user = User(id=1)
        comment = Comment(
            id=comment_id,
            text="Original comment",
            user_id=user.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = comment
        db.commit.return_value = None
        db.refresh.return_value = None
        result = await edit_comment(text, comment_id, user, db)
        self.assertEqual(result.text, comment.text)
        self.assertEqual(result.image_id, comment.image_id)
        self.assertEqual(result.user_id, comment.user_id)
        self.assertEqual(result.created_at.date(), comment.created_at.date())
        self.assertEqual(result.updated_at.date(), comment.updated_at.date())

    async def test_edit_comment_invalid_comment_id(self):
        text = "Updated comment"
        comment_id = 1
        user = User(id=1)
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        result = await edit_comment(text, comment_id, user, db)
        self.assertIsNone(result)

    async def test_edit_comment_unauthorized_user(self):
        text = "Updated comment"
        comment_id = 1
        user = User(id=2)
        comment = Comment(
            id=comment_id,
            text="Original comment",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = comment
        result = await edit_comment(text, comment_id, user, db)
        self.assertIsNone(result)

    async def test_delete_comment_success(self):
        comment_id = 1
        user = User(id=1)
        comment = Comment(
            id=comment_id,
            text="Test comment",
            user_id=user.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = comment
        db.commit.return_value = None
        result = await delete_comment(comment_id, user, db)
        self.assertEqual(result, comment)
        db.delete.assert_called_once_with(comment)
        db.commit.assert_called_once()

    async def test_delete_comment_invalid_comment_id(self):
        comment_id = 1
        user = User(id=1)
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        result = await delete_comment(comment_id, user, db)
        self.assertIsNone(result)
        db.delete.assert_not_called()
        db.commit.assert_not_called()

    async def test_delete_comment_unauthorized_user(self):
        comment_id = 1
        user = User(id=2)
        comment = Comment(
            id=comment_id,
            text="Test comment",
            user_id=1,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = comment
        result = await delete_comment(comment_id, user, db)
        self.assertIsNone(result)
        db.delete.assert_not_called()
        db.commit.assert_not_called()

    async def test_get_comments_by_image_id_success(self):
        image_id = 1
        comments = [
            Comment(
                id=1,
                text="Comment 1",
                image_id=image_id,
                user_id=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
            Comment(
                id=2,
                text="Comment 2",
                image_id=image_id,
                user_id=2,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            ),
        ]
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
            comments
        )
        result = await get_comments_by_image_id(image_id, db)
        self.assertEqual(result, comments)
        db.query.assert_called_once_with(Comment)
        db.query.return_value.filter.return_value.order_by.return_value.all.assert_called_once()

    async def test_get_comments_by_image_id_invalid_image_id(self):
        image_id = 1
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.order_by.return_value.all.return_value = (
            []
        )
        result = await get_comments_by_image_id(image_id, db)
        self.assertEqual(result, [])
        db.query.assert_called_once_with(Comment)
        db.query.return_value.filter.return_value.order_by.return_value.all.assert_called_once()


if __name__ == "__main__":
    unittest.main()
