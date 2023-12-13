import re

from sqlalchemy.orm import Session

from src.repository.tags import get_or_create_tag


async def get_tags_from_description(description: str, db: Session):
    """
    Gets the tags from description.

    :param description: Image description.
    :param db: The SQLAlchemy Session instance.

    :return: Tag list.
    """
    tag_names = re.findall(r"#(\w+)", description)
    tags = []
    for tag_name in tag_names:
        tag = await get_or_create_tag(db, tag_name)
        tags.append(tag)
    return tags
