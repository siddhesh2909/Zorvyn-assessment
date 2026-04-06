import sqlite3
import os
from app.config.settings import get_settings

_db: sqlite3.Connection | None = None


def get_database(db_path: str | None = None) -> sqlite3.Connection:
    global _db
    if _db is not None:
        return _db

    settings = get_settings()
    resolved_path = db_path or settings.DB_PATH

    directory = os.path.dirname(resolved_path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    _db = sqlite3.connect(resolved_path, check_same_thread=False)
    _db.row_factory = sqlite3.Row
    _db.execute("PRAGMA journal_mode = WAL")
    _db.execute("PRAGMA foreign_keys = ON")

    _initialize_tables(_db)
    return _db


def _initialize_tables(db: sqlite3.Connection) -> None:
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            username    TEXT UNIQUE NOT NULL,
            email       TEXT UNIQUE NOT NULL,
            password    TEXT NOT NULL,
            role        TEXT NOT NULL DEFAULT 'viewer' CHECK(role IN ('viewer', 'analyst', 'admin')),
            status      TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS financial_records (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            amount      REAL NOT NULL CHECK(amount > 0),
            type        TEXT NOT NULL CHECK(type IN ('income', 'expense')),
            category    TEXT NOT NULL,
            date        TEXT NOT NULL,
            description TEXT,
            is_deleted  INTEGER DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );

        CREATE INDEX IF NOT EXISTS idx_records_user_id ON financial_records(user_id);
        CREATE INDEX IF NOT EXISTS idx_records_type ON financial_records(type);
        CREATE INDEX IF NOT EXISTS idx_records_category ON financial_records(category);
        CREATE INDEX IF NOT EXISTS idx_records_date ON financial_records(date);
        CREATE INDEX IF NOT EXISTS idx_records_is_deleted ON financial_records(is_deleted);
    """)
    db.commit()


def close_database() -> None:
    global _db
    if _db is not None:
        _db.close()
        _db = None


def reset_database() -> None:
    global _db
    _db = None


def get_db() -> sqlite3.Connection:
    return get_database()
