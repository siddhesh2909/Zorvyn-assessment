from typing import Callable
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.config.settings import get_settings
from app.config.database import get_db
from app.exceptions import ApiError
from app.models.database import UserDB

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    if credentials is None:
        raise ApiError.unauthorized("Access token is required. Provide it as: Bearer <token>")

    token = credentials.credentials
    settings = get_settings()

    try:
        decoded = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise ApiError.unauthorized("Token has expired")
    except jwt.InvalidTokenError:
        raise ApiError.unauthorized("Invalid token")

    db = get_db()
    user = UserDB.find_by_id(db, decoded["id"])
    if user is None:
        raise ApiError.unauthorized("User no longer exists")

    if user["status"] == "inactive":
        raise ApiError.forbidden("Your account has been deactivated. Contact an administrator.")

    return UserDB.sanitize(user)


def require_roles(*allowed_roles: str) -> Callable:
    def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if current_user["role"] not in allowed_roles:
            raise ApiError.forbidden(
                f"Access denied. Required role(s): {', '.join(allowed_roles)}. "
                f"Your role: {current_user['role']}"
            )
        return current_user

    return role_checker
