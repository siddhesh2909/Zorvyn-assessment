from passlib.context import CryptContext
from app.config.database import get_database

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def seed_database() -> None:
    db = get_database()

    row = db.execute("SELECT COUNT(*) as count FROM users").fetchone()
    if row["count"] > 0:
        print("📦 Database already seeded, skipping...")
        return

    print("🌱 Seeding database...")

    admin_password = pwd_context.hash("admin123")
    analyst_password = pwd_context.hash("analyst123")
    viewer_password = pwd_context.hash("viewer123")

    cursor = db.execute(
        "INSERT INTO users (username, email, password, role, status) VALUES (?, ?, ?, ?, 'active')",
        ("admin", "admin@finance.com", admin_password, "admin"),
    )
    admin_id = cursor.lastrowid

    cursor = db.execute(
        "INSERT INTO users (username, email, password, role, status) VALUES (?, ?, ?, ?, 'active')",
        ("analyst", "analyst@finance.com", analyst_password, "analyst"),
    )
    analyst_id = cursor.lastrowid

    cursor = db.execute(
        "INSERT INTO users (username, email, password, role, status) VALUES (?, ?, ?, ?, 'active')",
        ("viewer", "viewer@finance.com", viewer_password, "viewer"),
    )
    viewer_id = cursor.lastrowid

    sample_records = [
        (admin_id, 5000.00, "income", "Salary", "2024-01-15", "Monthly salary - January"),
        (admin_id, 150.00, "expense", "Utilities", "2024-01-18", "Electricity bill"),
        (admin_id, 85.50, "expense", "Groceries", "2024-01-20", "Weekly groceries"),
        (admin_id, 5000.00, "income", "Salary", "2024-02-15", "Monthly salary - February"),
        (admin_id, 200.00, "expense", "Transport", "2024-02-10", "Monthly bus pass"),
        (admin_id, 1200.00, "expense", "Rent", "2024-02-01", "Monthly rent payment"),
        (admin_id, 500.00, "income", "Freelance", "2024-02-20", "Website design project"),
        (admin_id, 45.00, "expense", "Entertainment", "2024-02-22", "Movie tickets"),
        (admin_id, 5000.00, "income", "Salary", "2024-03-15", "Monthly salary - March"),
        (admin_id, 320.00, "expense", "Groceries", "2024-03-05", "Bulk grocery shopping"),
        (admin_id, 1200.00, "expense", "Rent", "2024-03-01", "Monthly rent payment"),
        (admin_id, 75.00, "expense", "Healthcare", "2024-03-10", "Doctor visit copay"),
        (admin_id, 2000.00, "income", "Investment", "2024-03-20", "Dividend payout"),
        (admin_id, 60.00, "expense", "Entertainment", "2024-03-25", "Concert tickets"),
        (admin_id, 5000.00, "income", "Salary", "2024-04-15", "Monthly salary - April"),
        (analyst_id, 3500.00, "income", "Salary", "2024-01-15", "Analyst monthly salary"),
        (analyst_id, 120.00, "expense", "Utilities", "2024-01-20", "Internet bill"),
        (analyst_id, 900.00, "expense", "Rent", "2024-02-01", "Monthly rent"),
        (viewer_id, 2500.00, "income", "Salary", "2024-01-15", "Viewer monthly salary"),
        (viewer_id, 50.00, "expense", "Groceries", "2024-01-22", "Quick grocery run"),
    ]

    db.executemany(
        "INSERT INTO financial_records (user_id, amount, type, category, date, description) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        sample_records,
    )

    db.commit()

    print("✅ Database seeded successfully!")
    print("   Default users:")
    print("   - admin@finance.com / admin123 (Admin)")
    print("   - analyst@finance.com / analyst123 (Analyst)")
    print("   - viewer@finance.com / viewer123 (Viewer)")
