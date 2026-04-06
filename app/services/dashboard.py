from app.config.database import get_db
from app.models.database import FinancialRecordDB


class DashboardService:

    @staticmethod
    def get_summary(user: dict) -> dict:
        db = get_db()
        user_id = user["id"] if user["role"] == "viewer" else None
        return FinancialRecordDB.get_summary(db, user_id)

    @staticmethod
    def get_category_breakdown(user: dict) -> dict:
        db = get_db()
        user_id = user["id"] if user["role"] == "viewer" else None
        breakdown = FinancialRecordDB.get_category_breakdown(db, user_id)

        income = [item for item in breakdown if item["type"] == "income"]
        expense = [item for item in breakdown if item["type"] == "expense"]

        return {
            "income": [
                {"category": item["category"], "total": item["total"], "count": item["count"]}
                for item in income
            ],
            "expense": [
                {"category": item["category"], "total": item["total"], "count": item["count"]}
                for item in expense
            ],
        }

    @staticmethod
    def get_trends(user: dict) -> list[dict]:
        db = get_db()
        user_id = user["id"] if user["role"] == "viewer" else None
        return FinancialRecordDB.get_monthly_trends(db, user_id)

    @staticmethod
    def get_recent_activity(limit: int, user: dict) -> list[dict]:
        db = get_db()
        user_id = user["id"] if user["role"] == "viewer" else None
        return FinancialRecordDB.get_recent_activity(db, limit, user_id)

    @staticmethod
    def get_full_dashboard(user: dict) -> dict:
        return {
            "summary": DashboardService.get_summary(user),
            "categoryBreakdown": DashboardService.get_category_breakdown(user),
            "trends": DashboardService.get_trends(user),
            "recentActivity": DashboardService.get_recent_activity(5, user),
        }
