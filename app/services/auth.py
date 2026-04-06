import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

from app.config.settings import get_settings
from app.config.database import get_db
from app.exceptions import ApiError
from app.models.database import UserDB

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:

    @staticmethod
    def register(*, username: str, email: str, password: str, role: str = "viewer") -> dict:
        db = get_db()

        if UserDB.find_by_email(db, email):
            raise ApiError.conflict("A user with this email already exists")

        if UserDB.find_by_username(db, username):
            raise ApiError.conflict("This username is already taken")

        hashed_password = pwd_context.hash(password)

        user = UserDB.create(db, username=username, email=email, password=hashed_password, role=role)
        token = AuthService.generate_token(user)

        return {"user": UserDB.sanitize(user), "token": token}

    @staticmethod
    def login(*, email: str, password: str) -> dict:
        db = get_db()

        user = UserDB.find_by_email(db, email)
        if not user:
            raise ApiError.unauthorized("Invalid email or password")

        if user["status"] == "inactive":
            raise ApiError.forbidden("Your account has been deactivated. Contact an administrator.")

        if not pwd_context.verify(password, user["password"]):
            raise ApiError.unauthorized("Invalid email or password")

        token = AuthService.generate_token(user)
        return {"user": UserDB.sanitize(user), "token": token}

    @staticmethod
    def generate_token(user: dict) -> str:
        settings = get_settings()
        payload = {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "exp": datetime.now(timezone.utc) + timedelta(seconds=settings.jwt_expiry_seconds),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")

    @staticmethod
    def get_profile(user_id: int) -> dict:
        db = get_db()
        user = UserDB.find_by_id(db, user_id)
        if not user:
            raise ApiError.not_found("User not found")
        return UserDB.sanitize(user)
