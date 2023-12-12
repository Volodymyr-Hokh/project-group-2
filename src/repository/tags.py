from sqlalchemy.orm import Session

from src.database.models import Tag


async def get_or_create_tag(db: Session, name: str):
    tag = db.query(Tag).filter(Tag.name == name).first()
    if not tag:
        tag = Tag(name=name)
    return tag
