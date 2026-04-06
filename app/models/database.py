import sqlite3
import math


class UserDB:

    @staticmethod
    def create(db: sqlite3.Connection, *, username: str, email: str, password: str, role: str = "viewer") -> dict:
        cursor = db.execute(
            "INSERT INTO users (username, email, password, role) VALUES (?, ?, ?, ?)",
            (username, email, password, role),
        )
        db.commit()
        return UserDB.find_by_id(db, cursor.lastrowid)

    @staticmethod
    def find_by_id(db: sqlite3.Connection, user_id: int) -> dict | None:
        row = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def find_by_email(db: sqlite3.Connection, email: str) -> dict | None:
        row = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def find_by_username(db: sqlite3.Connection, username: str) -> dict | None:
        row = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def find_all(
        db: sqlite3.Connection,
        *,
        page: int = 1,
        limit: int = 10,
        role: str | None = None,
        status: str | None = None,
        search: str | None = None,
    ) -> dict:
        where_clause = "WHERE 1=1"
        params: list = []

        if role:
            where_clause += " AND role = ?"
            params.append(role)
        if status:
            where_clause += " AND status = ?"
            params.append(status)
        if search:
            where_clause += " AND (username LIKE ? OR email LIKE ?)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")

        count_row = db.execute(
            f"SELECT COUNT(*) as count FROM users {where_clause}", params
        ).fetchone()
        total = count_row["count"]

        offset = (page - 1) * limit
        rows = db.execute(
            f"SELECT id, username, email, role, status, created_at, updated_at "
            f"FROM users {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()

        return {
            "users": [dict(row) for row in rows],
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": math.ceil(total / limit) if limit > 0 else 0,
        }

    @staticmethod
    def update_role(db: sqlite3.Connection, user_id: int, role: str) -> dict:
        db.execute(
            "UPDATE users SET role = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (role, user_id),
        )
        db.commit()
        return UserDB.find_by_id(db, user_id)

    @staticmethod
    def update_status(db: sqlite3.Connection, user_id: int, status: str) -> dict:
        db.execute(
            "UPDATE users SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, user_id),
        )
        db.commit()
        return UserDB.find_by_id(db, user_id)

    @staticmethod
    def delete(db: sqlite3.Connection, user_id: int) -> bool:
        cursor = db.execute("DELETE FROM users WHERE id = ?", (user_id,))
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def sanitize(user: dict | None) -> dict | None:
        if user is None:
            return None
        return {k: v for k, v in user.items() if k != "password"}


class FinancialRecordDB:

    @staticmethod
    def create(
        db: sqlite3.Connection,
        *,
        user_id: int,
        amount: float,
        type: str,
        category: str,
        date: str,
        description: str | None = None,
    ) -> dict:
        cursor = db.execute(
            "INSERT INTO financial_records (user_id, amount, type, category, date, description) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, amount, type, category, date, description),
        )
        db.commit()
        return FinancialRecordDB.find_by_id(db, cursor.lastrowid)

    @staticmethod
    def find_by_id(db: sqlite3.Connection, record_id: int) -> dict | None:
        row = db.execute(
            "SELECT fr.*, u.username as created_by "
            "FROM financial_records fr "
            "JOIN users u ON fr.user_id = u.id "
            "WHERE fr.id = ? AND fr.is_deleted = 0",
            (record_id,),
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def find_all(
        db: sqlite3.Connection,
        *,
        page: int = 1,
        limit: int = 10,
        type: str | None = None,
        category: str | None = None,
        startDate: str | None = None,
        endDate: str | None = None,
        minAmount: float | None = None,
        maxAmount: float | None = None,
        search: str | None = None,
        sortBy: str = "date",
        order: str = "DESC",
        userId: int | None = None,
    ) -> dict:
        page = int(page)
        limit = int(limit)

        where_clause = "WHERE fr.is_deleted = 0"
        params: list = []

        if userId:
            where_clause += " AND fr.user_id = ?"
            params.append(userId)
        if type:
            where_clause += " AND fr.type = ?"
            params.append(type)
        if category:
            where_clause += " AND fr.category = ?"
            params.append(category)
        if startDate:
            where_clause += " AND fr.date >= ?"
            params.append(startDate)
        if endDate:
            where_clause += " AND fr.date <= ?"
            params.append(endDate)
        if minAmount is not None:
            where_clause += " AND fr.amount >= ?"
            params.append(minAmount)
        if maxAmount is not None:
            where_clause += " AND fr.amount <= ?"
            params.append(maxAmount)
        if search:
            where_clause += " AND (fr.description LIKE ? OR fr.category LIKE ?)"
            params.append(f"%{search}%")
            params.append(f"%{search}%")

        allowed_sort_columns = ["date", "amount", "type", "category", "created_at"]
        sort_column = sortBy if sortBy in allowed_sort_columns else "date"
        sort_order = "ASC" if order.upper() == "ASC" else "DESC"

        count_row = db.execute(
            f"SELECT COUNT(*) as count FROM financial_records fr {where_clause}",
            params,
        ).fetchone()
        total = count_row["count"]

        offset = (page - 1) * limit
        rows = db.execute(
            f"SELECT fr.*, u.username as created_by "
            f"FROM financial_records fr "
            f"JOIN users u ON fr.user_id = u.id "
            f"{where_clause} "
            f"ORDER BY fr.{sort_column} {sort_order} "
            f"LIMIT ? OFFSET ?",
            params + [limit, offset],
        ).fetchall()

        return {
            "records": [dict(row) for row in rows],
            "total": total,
            "page": page,
            "limit": limit,
            "totalPages": math.ceil(total / limit) if limit > 0 else 0,
        }

    @staticmethod
    def update(
        db: sqlite3.Connection,
        record_id: int,
        *,
        amount: float | None = None,
        type: str | None = None,
        category: str | None = None,
        date: str | None = None,
        description: str | None = None,
    ) -> dict:
        fields = []
        params = []

        if amount is not None:
            fields.append("amount = ?")
            params.append(amount)
        if type is not None:
            fields.append("type = ?")
            params.append(type)
        if category is not None:
            fields.append("category = ?")
            params.append(category)
        if date is not None:
            fields.append("date = ?")
            params.append(date)
        if description is not None:
            fields.append("description = ?")
            params.append(description)

        if not fields:
            return FinancialRecordDB.find_by_id(db, record_id)

        fields.append("updated_at = CURRENT_TIMESTAMP")
        params.append(record_id)

        db.execute(
            f"UPDATE financial_records SET {', '.join(fields)} "
            f"WHERE id = ? AND is_deleted = 0",
            params,
        )
        db.commit()
        return FinancialRecordDB.find_by_id(db, record_id)

    @staticmethod
    def soft_delete(db: sqlite3.Connection, record_id: int) -> bool:
        cursor = db.execute(
            "UPDATE financial_records SET is_deleted = 1, updated_at = CURRENT_TIMESTAMP "
            "WHERE id = ? AND is_deleted = 0",
            (record_id,),
        )
        db.commit()
        return cursor.rowcount > 0

    @staticmethod
    def get_summary(db: sqlite3.Connection, user_id: int | None = None) -> dict:
        where_clause = "WHERE is_deleted = 0"
        params = []

        if user_id:
            where_clause += " AND user_id = ?"
            params.append(user_id)

        row = db.execute(
            f"SELECT "
            f"COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as totalIncome, "
            f"COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as totalExpenses, "
            f"COUNT(*) as recordCount "
            f"FROM financial_records {where_clause}",
            params,
        ).fetchone()

        return {
            "totalIncome": row["totalIncome"],
            "totalExpenses": row["totalExpenses"],
            "netBalance": row["totalIncome"] - row["totalExpenses"],
            "recordCount": row["recordCount"],
        }

    @staticmethod
    def get_category_breakdown(db: sqlite3.Connection, user_id: int | None = None) -> list[dict]:
        where_clause = "WHERE is_deleted = 0"
        params = []

        if user_id:
            where_clause += " AND user_id = ?"
            params.append(user_id)

        rows = db.execute(
            f"SELECT category, type, SUM(amount) as total, COUNT(*) as count "
            f"FROM financial_records {where_clause} "
            f"GROUP BY category, type ORDER BY total DESC",
            params,
        ).fetchall()

        return [dict(row) for row in rows]

    @staticmethod
    def get_monthly_trends(db: sqlite3.Connection, user_id: int | None = None) -> list[dict]:
        where_clause = "WHERE is_deleted = 0"
        params = []

        if user_id:
            where_clause += " AND user_id = ?"
            params.append(user_id)

        rows = db.execute(
            f"SELECT "
            f"strftime('%Y-%m', date) as month, "
            f"COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as income, "
            f"COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as expenses, "
            f"COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) - "
            f"COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as net "
            f"FROM financial_records {where_clause} "
            f"GROUP BY month ORDER BY month ASC",
            params,
        ).fetchall()

        return [dict(row) for row in rows]

    @staticmethod
    def get_recent_activity(db: sqlite3.Connection, limit: int = 10, user_id: int | None = None) -> list[dict]:
        where_clause = "WHERE fr.is_deleted = 0"
        params = []

        if user_id:
            where_clause += " AND fr.user_id = ?"
            params.append(user_id)

        rows = db.execute(
            f"SELECT fr.*, u.username as created_by "
            f"FROM financial_records fr "
            f"JOIN users u ON fr.user_id = u.id "
            f"{where_clause} "
            f"ORDER BY fr.created_at DESC LIMIT ?",
            params + [limit],
        ).fetchall()

        return [dict(row) for row in rows]

    @staticmethod
    def get_categories(db: sqlite3.Connection) -> list[str]:
        rows = db.execute(
            "SELECT DISTINCT category FROM financial_records "
            "WHERE is_deleted = 0 ORDER BY category ASC"
        ).fetchall()
        return [row["category"] for row in rows]
