from datetime import datetime

from sqlalchemy.orm import Session

from src.database.models import Comment, User


async def add_comment(text: str, image_id: int, user: User, db: Session):
    """ """
    comment = Comment(
        text=text,
        image_id=image_id,
        user_id=user.id,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


async def edit_comment(text: str, comment_id: int, user: User, db: Session):
    """ """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    if comment.user_id != user.id:
        return None
    comment.text = text
    comment.updated_at = datetime.now()
    db.commit()
    db.refresh(comment)
    return comment


async def delete_comment(comment_id: int, user: User, db: Session):
    """ """
    # TODO Додати логіку, що тільки адмін або модератор може видаляти коментарі
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    if comment.user_id != user.id:
        return None
    db.delete(comment)
    db.commit()
    return comment


async def get_comments_by_image_id(image_id: int, db: Session):
    """ """
    comments = (
        db.query(Comment)
        .filter(Comment.image_id == image_id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    return comments