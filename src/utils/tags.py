import re

from sqlalchemy.orm import Session

from src.database.models import Tag
from src.repository.tags import get_or_create_tag


async def get_tags_from_description(description: str, db: Session):
    tag_names = re.findall(r"#(\w+)", description)
    tags = []
    for tag_name in tag_names:
        tag = await get_or_create_tag(db, tag_name)
        tags.append(tag)
    return tags
