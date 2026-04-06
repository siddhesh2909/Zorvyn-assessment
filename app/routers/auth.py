from fastapi import APIRouter, Depends
from app.schemas.auth import RegisterRequest, LoginRequest
from app.services.auth import AuthService
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    result = AuthService.register(
        username=body.username,
        email=body.email,
        password=body.password,
        role=body.role,
    )
    return {
        "success": True,
        "message": "User registered successfully",
        "data": result,
    }


@router.post("/login")
def login(body: LoginRequest):
    result = AuthService.login(email=body.email, password=body.password)
    return {
        "success": True,
        "message": "Login successful",
        "data": result,
    }


@router.get("/me")
def get_me(current_user: dict = Depends(get_current_user)):
    return {
        "success": True,
        "data": {"user": current_user},
    }
