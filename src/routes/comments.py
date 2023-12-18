from fastapi import APIRouter, Request, Depends, HTTPException, status

from src.database.db import get_db
from src.limiter import limiter
from src.repository import comments as comments_repository
from src.database.models import UserRole
from src.schemas import CommentResponse
from src.services.auth import auth_service


router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/", response_model=CommentResponse)
@limiter.limit(limit_value="10/minute")
async def add_comment(
    request: Request,
    text: str,
    image_id: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """Adds a comment to an image.

    Args:
        request (Request): The request object.\n
        text (str): The text of the comment.\n
        image_id (int): The ID of the image.\n
        db: The database dependency.\n
        user: The current user dependency.\n

    Returns:
        The added comment.

    """
    return await comments_repository.add_comment(
        text=text, image_id=image_id, user=user, db=db
    )


@router.put("/{comment_id}", response_model=CommentResponse)
@limiter.limit(limit_value="10/minute")
async def edit_comment(
    request: Request,
    text: str,
    comment_id: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """
    Edits a comment in the database.

    Args:
        request (Request): The HTTP request object.\n
        text (str): The updated text of the comment.\n
        comment_id (int): The ID of the comment to be edited.\n
        db: The database dependency.\n
        user: The current user dependency.\n

    Raises:
        HTTPException: If the comment text is empty or contains only whitespace.

    Returns:
        The edited comment.
    """
    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment text cannot be empty or contain only whitespace",
        )

    return await comments_repository.edit_comment(
        text=text, comment_id=comment_id, user=user, db=db
    )


@router.delete("/{comment_id}", response_model=CommentResponse)
@limiter.limit(limit_value="10/minute")
async def delete_comment(
    request: Request,
    comment_id: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """
    Deletes a comment.

    Args:
        request (Request): The request object.\n
        comment_id (int): The ID of the comment to be deleted.\n
        db: The database dependency.\n
        user: The current user dependency.\n

    Raises:
        HTTPException: If the user is not an administrator or moderator.

    Returns:
        The result of the delete operation.
    """
    if user.role not in (UserRole.admin.value, UserRole.moderator.value):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators and moderators can delete comments",
        )

    return await comments_repository.delete_comment(
        comment_id=comment_id, user=user, db=db
    )
