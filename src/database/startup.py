from src.database.crud_roles import create_roles
from src.database.db import get_db

def initialize_roles_on_startup():
    create_roles()

initialize_roles_on_startup()
