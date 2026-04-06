from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from app.config.database import get_database, close_database
from app.config.seed import seed_database
from app.config.settings import get_settings
from app.exceptions import ApiError, api_error_handler, validation_error_handler
from app.middleware.rate_limiter import limiter, rate_limit_exceeded_handler
from app.routers import auth, users, records, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    print("🔧 Initializing database...")
    get_database()
    seed_database()

    print(f"\n🚀 Finance Dashboard API is running!")
    print(f"   Server:        http://localhost:{settings.PORT}")
    print(f"   API Docs:      http://localhost:{settings.PORT}/api-docs")
    print(f"   Health Check:  http://localhost:{settings.PORT}/health")
    print(f"   Environment:   {settings.NODE_ENV}\n")

    yield
    close_database()


app = FastAPI(
    title="Finance Dashboard API",
    version="1.0.0",
    description=(
        "A RESTful API for a finance dashboard system with role-based access control.\n\n"
        "## Roles\n"
        "- **Viewer**: Can view own records and dashboard data\n"
        "- **Analyst**: Can view all records and access detailed analytics\n"
        "- **Admin**: Full access — manage users, create/update/delete records\n\n"
        "## Default Users (after seeding)\n"
        "| Email | Password | Role |\n"
        "|-------|----------|------|\n"
        "| admin@finance.com | admin123 | Admin |\n"
        "| analyst@finance.com | analyst123 | Analyst |\n"
        "| viewer@finance.com | viewer123 | Viewer |"
    ),
    lifespan=lifespan,
    docs_url="/api-docs",
    redoc_url="/redoc",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ApiError, api_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)


@app.get("/health", tags=["System"])
def health_check():
    settings = get_settings()
    return {
        "success": True,
        "message": "Finance Dashboard API is running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "environment": settings.NODE_ENV,
    }


@app.get("/", tags=["System"])
def root():
    return {
        "success": True,
        "message": "Finance Dashboard API",
        "version": "1.0.0",
        "documentation": "/api-docs",
        "endpoints": {
            "auth": "/api/auth",
            "users": "/api/users",
            "records": "/api/records",
            "dashboard": "/api/dashboard",
        },
    }


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)
