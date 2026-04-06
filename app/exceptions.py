from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


class ApiError(Exception):
    def __init__(self, status_code: int, message: str, is_operational: bool = True):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.is_operational = is_operational
        self.status = "fail" if str(status_code).startswith("4") else "error"

    @classmethod
    def bad_request(cls, message: str = "Bad request") -> "ApiError":
        return cls(400, message)

    @classmethod
    def unauthorized(cls, message: str = "Unauthorized") -> "ApiError":
        return cls(401, message)

    @classmethod
    def forbidden(cls, message: str = "Forbidden") -> "ApiError":
        return cls(403, message)

    @classmethod
    def not_found(cls, message: str = "Resource not found") -> "ApiError":
        return cls(404, message)

    @classmethod
    def conflict(cls, message: str = "Conflict") -> "ApiError":
        return cls(409, message)

    @classmethod
    def internal(cls, message: str = "Internal server error") -> "ApiError":
        return cls(500, message, is_operational=False)

    @classmethod
    def too_many_requests(cls, message: str = "Too many requests, please try again later.") -> "ApiError":
        return cls(429, message)


async def api_error_handler(request: Request, exc: ApiError) -> JSONResponse:
    response = {
        "success": False,
        "status": exc.status,
        "statusCode": exc.status_code,
        "message": exc.message,
    }

    if not exc.is_operational:
        print(f"❌ Unexpected Error: {exc}")

    return JSONResponse(status_code=exc.status_code, content=response)


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body" and loc != "query" and loc != "path")
        errors.append({
            "field": field or str(error["loc"][-1]) if error["loc"] else "unknown",
            "message": error["msg"],
        })

    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "status": "fail",
            "statusCode": 400,
            "message": "Validation failed",
            "errors": errors,
        },
    )
