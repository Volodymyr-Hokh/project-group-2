import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from datetime import datetime
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

import cloudinary
from sqlalchemy.orm import Session

from src.conf.config import settings
from src.repository.images import (
    add_image,
    delete_image,
    edit_description,
    get_images,
    get_image,
)
from src.database.models import Image, User


class TestImages(IsolatedAsyncioTestCase):
    def setUp(self):
        self.maxDiff = None
        cloudinary.config(
            cloud_name=settings.cloudinary_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret,
            secure=True,
        )

    async def test_add_image(self):
        image_url = "https://example.com/image.jpg"
        public_id = "abc123"
        description = "Test image"
        user = User(id=1)
        db = MagicMock(spec=Session)
        image = Image(
            url=image_url,
            public_id=public_id,
            description=description,
            user_id=user.id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        db.add.return_value = None
        db.commit.return_value = None
        db.refresh.return_value = None
        result = await add_image(image_url, public_id, description, user, db)
        self.assertEqual(result.url, image.url)
        self.assertEqual(result.public_id, image.public_id)
        self.assertEqual(result.description, image.description)
        self.assertEqual(result.user_id, image.user_id)
        self.assertEqual(result.created_at.date(), image.created_at.date())
        self.assertEqual(result.updated_at.date(), image.updated_at.date())

    async def test_delete_image_existing(self):
        image_id = 1
        user = User(id=1)
        image = Image(id=image_id, user_id=user.id, public_id="abc123")
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = image
        result = await delete_image(image_id, user, db)
        self.assertEqual(result.url, image.url)
        self.assertEqual(result.public_id, image.public_id)
        self.assertEqual(result.description, image.description)
        self.assertEqual(result.user_id, image.user_id)
        db.delete.assert_called_once_with(image)
        db.commit.assert_called_once()

    async def test_delete_image_non_existing(self):
        image_id = 1
        user = User(id=1)
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        result = await delete_image(image_id, user, db)
        self.assertIsNone(result)

    async def test_edit_description_existing_image(self):
        image_id = 1
        description = "Updated description"
        user = User(id=1)
        image = Image(id=image_id, user_id=user.id, description="Old description")
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = image
        db.commit.return_value = None
        result = await edit_description(image_id, description, user, db)
        self.assertEqual(result.description, description)
        self.assertEqual(result.updated_at.date(), datetime.now().date())
        db.commit.assert_called_once()

    async def test_edit_description_non_existing_image(self):
        image_id = 1
        description = "Updated description"
        user = User(id=1)
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        result = await edit_description(image_id, description, user, db)
        self.assertIsNone(result)

    async def test_get_images(self):
        user = User(id=1)
        images = [
            Image(id=1, user_id=user.id),
            Image(id=2, user_id=user.id),
            Image(id=3, user_id=user.id),
        ]
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.all.return_value = images
        result = await get_images(user, db)
        self.assertEqual(result, images)
        db.query.return_value.filter.return_value.all.assert_called_once()

    async def test_get_image_existing(self):
        image_id = 1
        user = User(id=1)
        image = Image(id=image_id, user_id=user.id)
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = image
        result = await get_image(image_id, user, db)
        self.assertEqual(result, image)
        db.query.return_value.filter.return_value.first.assert_called_once()

    async def test_get_image_non_existing(self):
        image_id = 1
        user = User(id=1)
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        result = await get_image(image_id, user, db)
        self.assertIsNone(result)
        db.query.return_value.filter.return_value.first.assert_called_once()


if __name__ == "__main__":
    unittest.main()
