from fastapi import Depends, HTTPException, status
from src.services.auth import Auth

auth = Auth()

def has_permission(required_role: str = "user"):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            token = await auth.oauth2_scheme()
            current_user_roles = await auth.get_current_user_role(token)
            if required_role not in current_user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have permission to access this resource",
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator
