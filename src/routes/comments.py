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
    """
    Adding comment to db.
    :param request: FastAPI Request instance.
    :param text: Comment text.
    :param image_id: Image id number.
    :param db: The SQLAlchemy Session instance.
    :param user: Get the current authenticated user.
    :return:
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
    Editing comment in db.
    :param request: FastAPI Request instance.
    :param text: Comment text.
    :param comment_id: Comment id number.
    :param db: The SQLAlchemy Session instance.
    :param user: Get the current authenticated user.
    :return:
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
    Deleting comment in db.
    :param request: FastAPI Request instance.
    :param comment_id: Comment id number.
    :param db: The SQLAlchemy Session instance.
    :param user: Get the current authenticated user.
    :return:
    """
    if user.role not in (UserRole.admin.value, UserRole.moderator.value):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
        detail="Only administrators and moderators can delete comments")
    
    return await comments_repository.delete_comment(
        comment_id=comment_id, user=user, db=db
    )


@router.get("/{image_id}", response_model=list[CommentResponse])
@limiter.limit(limit_value="10/minute")
async def get_comments_by_image_id(
    request: Request,
    image_id: int,
    db=Depends(get_db),
    user=Depends(auth_service.get_current_user),
):
    """
    Getting comments by image id.
    :param request: FastAPI Request instance.
    :param image_id: Image id number.
    :param db: The SQLAlchemy Session instance.
    :param user: Get the current authenticated user.
    :return:
    """
    return await comments_repository.get_comments_by_image_id(image_id=image_id, db=db)