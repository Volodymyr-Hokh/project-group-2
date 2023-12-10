from fastapi import Depends, Request

from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import User


class Auth:
    async def get_current_user(
        self,
        request: Request,
        db: Session = Depends(get_db),
    ):
        return db.query(User).filter(User.id == 1).first()


auth_service = Auth()
