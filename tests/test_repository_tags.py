import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from src.repository.tags import get_or_create_tag
from src.database.models import Tag


class TestTags(IsolatedAsyncioTestCase):
    async def test_get_or_create_tag_existing(self):
        tag_name = "existing_tag"
        tag = Tag(name=tag_name)
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = tag
        result = await get_or_create_tag(db, tag_name)
        self.assertEqual(result, tag)
        db.query.return_value.filter.return_value.first.assert_called_once()

    async def test_get_or_create_tag_non_existing(self):
        tag_name = "non_existing_tag"
        db = MagicMock(spec=Session)
        db.query.return_value.filter.return_value.first.return_value = None
        result = await get_or_create_tag(db, tag_name)
        self.assertIsInstance(result, Tag)
        self.assertEqual(result.name, tag_name)
        db.query.return_value.filter.return_value.first.assert_called_once()


if __name__ == "__main__":
    unittest.main()
