from sqlalchemy.orm import Session
from src.database.db import get_db  # Use get_db instead of SessionLocal
from .models import Roles

def create_roles():
    # Use a context manager to get the session from the generator
    with get_db() as db:  
        role_names = ["user", "moderator", "admin"]
        for role_name in role_names:
            role = Roles(name=role_name)
            db.add(role)
        db.commit()