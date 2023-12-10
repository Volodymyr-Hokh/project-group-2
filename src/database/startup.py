from sqlalchemy.orm import Session
from app.repo.roles import create_roles
from app.database.db import get_db

def initialize_roles_on_startup():
    db: Session = get_db()

    create_roles(db)


initialize_roles_on_startup()