from fastapi import APIRouter, Depends, Query
from app.schemas.record import CreateRecordRequest, UpdateRecordRequest
from app.services.record import RecordService
from app.dependencies.auth import get_current_user, require_roles

router = APIRouter(prefix="/api/records", tags=["Financial Records"])


@router.post("/", status_code=201)
def create_record(
    body: CreateRecordRequest,
    current_user: dict = Depends(require_roles("admin")),
):
    record = RecordService.create(body.model_dump(), current_user["id"])
    return {"success": True, "message": "Financial record created successfully", "data": {"record": record}}


@router.get("/")
def list_records(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    type: str | None = Query(default=None, pattern="^(income|expense)$"),
    category: str | None = Query(default=None, max_length=50),
    startDate: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    endDate: str | None = Query(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$"),
    minAmount: float | None = Query(default=None, gt=0),
    maxAmount: float | None = Query(default=None, gt=0),
    search: str | None = Query(default=None, max_length=100),
    sortBy: str = Query(default="date", pattern="^(date|amount|type|category|created_at)$"),
    order: str = Query(default="DESC", pattern="^(ASC|DESC|asc|desc)$"),
    current_user: dict = Depends(get_current_user),
):
    query = {k: v for k, v in {
        "page": page, "limit": limit, "type": type, "category": category,
        "startDate": startDate, "endDate": endDate, "minAmount": minAmount,
        "maxAmount": maxAmount, "search": search, "sortBy": sortBy, "order": order,
    }.items() if v is not None}

    result = RecordService.get_all(query, current_user)
    return {"success": True, "data": result}


@router.get("/categories")
def get_categories(current_user: dict = Depends(get_current_user)):
    categories = RecordService.get_categories()
    return {"success": True, "data": {"categories": categories}}


@router.get("/{record_id}")
def get_record(record_id: int, current_user: dict = Depends(get_current_user)):
    record = RecordService.get_by_id(record_id, current_user)
    return {"success": True, "data": {"record": record}}


@router.put("/{record_id}")
def update_record(
    record_id: int,
    body: UpdateRecordRequest,
    current_user: dict = Depends(require_roles("admin")),
):
    update_data = {k: v for k, v in body.model_dump().items() if v is not None}
    record = RecordService.update(record_id, update_data)
    return {"success": True, "message": "Financial record updated successfully", "data": {"record": record}}


@router.delete("/{record_id}")
def delete_record(record_id: int, current_user: dict = Depends(require_roles("admin"))):
    RecordService.delete(record_id)
    return {"success": True, "message": "Financial record deleted successfully"}
