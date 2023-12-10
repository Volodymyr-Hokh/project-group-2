from sqlalchemy.orm import Session

from .models import Roles

def create_roles(db: Session):
    role_names = ["user", "moderator", "admin"]
    for role_name in role_names:
        role = Roles(name=role_name)
        db.add(role)
    db.commit()