# Finance Dashboard API

Backend API for a finance dashboard — handles users, financial records, and analytics with role-based access.

Built with FastAPI, SQLite, and JWT auth.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy the example env file and tweak if needed:

```bash
cp .env.example .env
```

## Run

```bash
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload
```

Server starts at `http://localhost:3000`

API docs at `http://localhost:3000/api-docs`

## Default Users

The database seeds itself on first run with these accounts:

| Email | Password | Role |
|-------|----------|------|
| admin@finance.com | admin123 | Admin |
| analyst@finance.com | analyst123 | Analyst |
| viewer@finance.com | viewer123 | Viewer |

## Endpoints

**Auth** — `/api/auth`
- `POST /register` — create account
- `POST /login` — get JWT token
- `GET /me` — current user (needs token)

**Records** — `/api/records`
- `POST /` — create record (admin)
- `GET /` — list with filters, pagination, sorting
- `GET /:id` — single record
- `PUT /:id` — update (admin)
- `DELETE /:id` — soft delete (admin)

**Dashboard** — `/api/dashboard`
- `GET /summary` — income, expenses, balance
- `GET /category-breakdown` — totals by category
- `GET /trends` — monthly trends
- `GET /recent-activity` — latest transactions
- `GET /full` — everything in one call

**Users** — `/api/users` (admin only)
- `GET /` — list users
- `GET /:id` — get user
- `PATCH /:id/role` — change role
- `PATCH /:id/status` — activate/deactivate
- `DELETE /:id` — remove user

## Roles

- **Viewer** — sees only their own records
- **Analyst** — sees all records, read-only
- **Admin** — full access, manages users and records

## Auth

All protected routes need a Bearer token in the header:

```
Authorization: Bearer <your-token>
```

Get a token by hitting `/api/auth/login`.
