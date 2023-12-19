from datetime import datetime

from sqlalchemy.orm import Session

from src.database.models import Comment, User


async def add_comment(text: str, image_id: int, user: User, db: Session):
    """Adds a comment to an image.

    Args:
        text (str): The text of the comment.\n
        image_id (int): The ID of the image.\n
        user (User): The user who made the comment.\n
        db (Session): The database session.\n

    Returns:
        Comment: The newly created comment.
    """
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
    """Updates the text of a comment with the given comment_id.

    Args:
        text (str): The new text for the comment.\n
        comment_id (int): The ID of the comment to be edited.\n
        user (User): The user making the edit.\n
        db (Session): The database session.\n

    Returns:
        Comment: The updated comment object if successful, None otherwise.
    """
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
    """Deletes a comment from the database.

    Args:
        comment_id (int): The ID of the comment to be deleted.\n
        user (User): The user who is attempting to delete the comment.\n
        db (Session): The database session.\n

    Returns:
        Comment: The deleted comment if successful, None otherwise.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        return None
    if comment.user_id != user.id:
        return None
    db.delete(comment)
    db.commit()
    return comment


async def get_comments_by_image_id(image_id: int, db: Session):
    """Retrieves comments for a given image ID from the database.

    Args:
        image_id (int): The ID of the image.\n
        db (Session): The database session.\n

    Returns:
        List[Comment]: A list of Comment objects representing the comments for the image.
    """
    comments = (
        db.query(Comment)
        .filter(Comment.image_id == image_id)
        .order_by(Comment.created_at.desc())
        .all()
    )

    return comments
