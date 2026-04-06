from app.config.database import get_db
from app.exceptions import ApiError
from app.models.database import FinancialRecordDB


class RecordService:

    @staticmethod
    def create(data: dict, user_id: int) -> dict:
        db = get_db()
        return FinancialRecordDB.create(
            db,
            user_id=user_id,
            amount=data["amount"],
            type=data["type"],
            category=data["category"],
            date=data["date"],
            description=data.get("description"),
        )

    @staticmethod
    def get_all(query: dict, user: dict) -> dict:
        db = get_db()
        options = {**query}

        if user["role"] == "viewer":
            options["userId"] = user["id"]

        return FinancialRecordDB.find_all(db, **options)

    @staticmethod
    def get_by_id(record_id: int, user: dict) -> dict:
        db = get_db()
        record = FinancialRecordDB.find_by_id(db, record_id)
        if not record:
            raise ApiError.not_found(f"Financial record with ID {record_id} not found")

        if user["role"] == "viewer" and record["user_id"] != user["id"]:
            raise ApiError.forbidden("You do not have access to this record")

        return record

    @staticmethod
    def update(record_id: int, data: dict) -> dict:
        db = get_db()
        record = FinancialRecordDB.find_by_id(db, record_id)
        if not record:
            raise ApiError.not_found(f"Financial record with ID {record_id} not found")

        return FinancialRecordDB.update(db, record_id, **data)

    @staticmethod
    def delete(record_id: int) -> None:
        db = get_db()
        record = FinancialRecordDB.find_by_id(db, record_id)
        if not record:
            raise ApiError.not_found(f"Financial record with ID {record_id} not found")

        deleted = FinancialRecordDB.soft_delete(db, record_id)
        if not deleted:
            raise ApiError.internal("Failed to delete record")

    @staticmethod
    def get_categories() -> list[str]:
        db = get_db()
        return FinancialRecordDB.get_categories(db)
