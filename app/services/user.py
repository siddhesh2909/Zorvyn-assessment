from app.config.database import get_db
from app.exceptions import ApiError
from app.models.database import UserDB


class UserService:

    @staticmethod
    def get_all(
        *,
        page: int = 1,
        limit: int = 10,
        role: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> dict:
        db = get_db()
        return UserDB.find_all(db, page=page, limit=limit, role=role, status=status, search=search)

    @staticmethod
    def get_by_id(user_id: int) -> dict:
        db = get_db()
        user = UserDB.find_by_id(db, user_id)
        if not user:
            raise ApiError.not_found(f"User with ID {user_id} not found")
        return UserDB.sanitize(user)

    @staticmethod
    def update_role(user_id: int, role: str, current_user_id: int) -> dict:
        db = get_db()
        user = UserDB.find_by_id(db, user_id)
        if not user:
            raise ApiError.not_found(f"User with ID {user_id} not found")

        if user_id == current_user_id:
            raise ApiError.bad_request("You cannot change your own role")

        updated = UserDB.update_role(db, user_id, role)
        return UserDB.sanitize(updated)

    @staticmethod
    def update_status(user_id: int, status: str, current_user_id: int) -> dict:
        db = get_db()
        user = UserDB.find_by_id(db, user_id)
        if not user:
            raise ApiError.not_found(f"User with ID {user_id} not found")

        if user_id == current_user_id:
            raise ApiError.bad_request("You cannot change your own status")

        updated = UserDB.update_status(db, user_id, status)
        return UserDB.sanitize(updated)

    @staticmethod
    def delete(user_id: int, current_user_id: int) -> None:
        db = get_db()
        user = UserDB.find_by_id(db, user_id)
        if not user:
            raise ApiError.not_found(f"User with ID {user_id} not found")

        if user_id == current_user_id:
            raise ApiError.bad_request("You cannot delete your own account")

        deleted = UserDB.delete(db, user_id)
        if not deleted:
            raise ApiError.internal("Failed to delete user")
