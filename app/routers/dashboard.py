from fastapi import APIRouter, Depends, Query
from app.services.dashboard import DashboardService
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary")
def get_summary(current_user: dict = Depends(get_current_user)):
    summary = DashboardService.get_summary(current_user)
    return {"success": True, "data": {"summary": summary}}


@router.get("/category-breakdown")
def get_category_breakdown(current_user: dict = Depends(get_current_user)):
    breakdown = DashboardService.get_category_breakdown(current_user)
    return {"success": True, "data": {"breakdown": breakdown}}


@router.get("/trends")
def get_trends(current_user: dict = Depends(get_current_user)):
    trends = DashboardService.get_trends(current_user)
    return {"success": True, "data": {"trends": trends}}


@router.get("/recent-activity")
def get_recent_activity(
    limit: int = Query(default=10, ge=1),
    current_user: dict = Depends(get_current_user),
):
    activity = DashboardService.get_recent_activity(limit, current_user)
    return {"success": True, "data": {"recentActivity": activity}}


@router.get("/full")
def get_full_dashboard(current_user: dict = Depends(get_current_user)):
    dashboard = DashboardService.get_full_dashboard(current_user)
    return {"success": True, "data": {"dashboard": dashboard}}
