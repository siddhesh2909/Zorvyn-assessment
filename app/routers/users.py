from fastapi import APIRouter, Depends, Query
from app.schemas.user import UpdateRoleRequest, UpdateStatusRequest
from app.services.user import UserService
from app.dependencies.auth import require_roles

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/")
def list_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    role: str | None = Query(default=None, pattern="^(viewer|analyst|admin)$"),
    status: str | None = Query(default=None, pattern="^(active|inactive)$"),
    search: str | None = Query(default=None, max_length=100),
    current_user: dict = Depends(require_roles("admin")),
):
    result = UserService.get_all(page=page, limit=limit, role=role, status=status, search=search)
    return {"success": True, "data": result}


@router.get("/{user_id}")
def get_user(user_id: int, current_user: dict = Depends(require_roles("admin"))):
    user = UserService.get_by_id(user_id)
    return {"success": True, "data": {"user": user}}


@router.patch("/{user_id}/role")
def update_role(
    user_id: int,
    body: UpdateRoleRequest,
    current_user: dict = Depends(require_roles("admin")),
):
    user = UserService.update_role(user_id, body.role, current_user["id"])
    return {"success": True, "message": "User role updated successfully", "data": {"user": user}}


@router.patch("/{user_id}/status")
def update_status(
    user_id: int,
    body: UpdateStatusRequest,
    current_user: dict = Depends(require_roles("admin")),
):
    user = UserService.update_status(user_id, body.status, current_user["id"])
    action = "activated" if body.status == "active" else "deactivated"
    return {"success": True, "message": f"User {action} successfully", "data": {"user": user}}


@router.delete("/{user_id}")
def delete_user(user_id: int, current_user: dict = Depends(require_roles("admin"))):
    UserService.delete(user_id, current_user["id"])
    return {"success": True, "message": "User deleted successfully"}
