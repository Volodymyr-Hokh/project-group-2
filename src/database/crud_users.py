from sqlalchemy.orm import Session
from src.database.models import User, Roles
from src.schemas import UserUpdate, UserRole
from fastapi import APIRouter, HTTPException, Depends, status, Security, BackgroundTasks, Request

def get_users_count(db: Session):
    return db.query(User).count()

def update_user_role(user_id: int, role_update: UserUpdate, db: Session) -> User:
    """
    Update user role.

    :param user_id: The user id.
    :param role_update: The new role data.
    :param db: The SQLAlchemy Session instance.

    :return: The updated user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Отримати ролі користувача
    user_roles = [role.name for role in user.roles]
    
    # Оновити ролі користувача
    new_role = role_update.role
    if new_role not in user_roles:
        user.roles.append(Roles(name=new_role))
    
    db.commit()
    db.refresh(user)
    
    return user