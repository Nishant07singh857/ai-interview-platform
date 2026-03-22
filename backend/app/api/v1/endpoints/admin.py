"""
Admin Endpoints - Complete admin panel API
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from app.core.deps import get_current_admin_user
from app.models.user import User
from app.schemas.user import UserResponse, UserDetailResponse
from app.schemas.question import QuestionResponse
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])
logger = logging.getLogger(__name__)
admin_service = AdminService()

# Dashboard
@router.get("/dashboard")
async def get_dashboard(
    admin: User = Depends(get_current_admin_user)
):
    """Get admin dashboard data"""
    try:
        dashboard = await admin_service.get_dashboard_data()
        return dashboard
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard")

# User Management
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    role: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    admin: User = Depends(get_current_admin_user)
):
    """Get all users with filters"""
    try:
        users = await admin_service.get_all_users(skip, limit, role, status, search)
        return users
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get users")

@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user_details(
    user_id: str,
    admin: User = Depends(get_current_admin_user)
):
    """Get detailed user information"""
    try:
        user = await admin_service.get_user_details(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user details")

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: str,
    admin: User = Depends(get_current_admin_user)
):
    """Update user role"""
    try:
        await admin_service.update_user_role(user_id, role)
        return {"message": f"User role updated to {role}"}
    except Exception as e:
        logger.error(f"Error updating user role: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user role")

@router.post("/users/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    reason: str,
    admin: User = Depends(get_current_admin_user)
):
    """Suspend user account"""
    try:
        await admin_service.suspend_user(user_id, reason)
        return {"message": "User suspended"}
    except Exception as e:
        logger.error(f"Error suspending user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to suspend user")

@router.post("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    admin: User = Depends(get_current_admin_user)
):
    """Activate user account"""
    try:
        await admin_service.activate_user(user_id)
        return {"message": "User activated"}
    except Exception as e:
        logger.error(f"Error activating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to activate user")

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    admin: User = Depends(get_current_admin_user)
):
    """Delete user account"""
    try:
        await admin_service.delete_user(user_id)
        return {"message": "User deleted"}
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

# Question Management
@router.get("/questions", response_model=List[QuestionResponse])
async def get_all_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[str] = None,
    subject: Optional[str] = None,
    difficulty: Optional[str] = None,
    admin: User = Depends(get_current_admin_user)
):
    """Get all questions with filters"""
    try:
        questions = await admin_service.get_all_questions(
            skip, limit, status, subject, difficulty
        )
        return questions
    except Exception as e:
        logger.error(f"Error getting questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get questions")

@router.post("/questions/bulk-import")
async def bulk_import_questions(
    questions: List[dict],
    admin: User = Depends(get_current_admin_user)
):
    """Bulk import questions"""
    try:
        result = await admin_service.bulk_import_questions(questions, admin.uid)
        return result
    except Exception as e:
        logger.error(f"Error importing questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to import questions")

@router.post("/questions/{question_id}/approve")
async def approve_question(
    question_id: str,
    admin: User = Depends(get_current_admin_user)
):
    """Approve a question"""
    try:
        await admin_service.approve_question(question_id)
        return {"message": "Question approved"}
    except Exception as e:
        logger.error(f"Error approving question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to approve question")

@router.post("/questions/{question_id}/reject")
async def reject_question(
    question_id: str,
    reason: str,
    admin: User = Depends(get_current_admin_user)
):
    """Reject a question"""
    try:
        await admin_service.reject_question(question_id, reason)
        return {"message": "Question rejected"}
    except Exception as e:
        logger.error(f"Error rejecting question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reject question")

# Content Management
@router.get("/reports/content")
async def get_content_reports(
    status: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_current_admin_user)
):
    """Get content reports"""
    try:
        reports = await admin_service.get_content_reports(status, limit)
        return reports
    except Exception as e:
        logger.error(f"Error getting reports: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get reports")

@router.post("/reports/{report_id}/resolve")
async def resolve_report(
    report_id: str,
    action: str,
    admin: User = Depends(get_current_admin_user)
):
    """Resolve a content report"""
    try:
        await admin_service.resolve_report(report_id, action)
        return {"message": "Report resolved"}
    except Exception as e:
        logger.error(f"Error resolving report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resolve report")

# System Settings
@router.get("/settings")
async def get_system_settings(
    admin: User = Depends(get_current_admin_user)
):
    """Get system settings"""
    try:
        settings = await admin_service.get_system_settings()
        return settings
    except Exception as e:
        logger.error(f"Error getting settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get settings")

@router.put("/settings")
async def update_system_settings(
    settings: dict,
    admin: User = Depends(get_current_admin_user)
):
    """Update system settings"""
    try:
        updated = await admin_service.update_system_settings(settings)
        return updated
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update settings")

# Analytics
@router.get("/analytics/platform")
async def get_platform_analytics(
    days: int = Query(30, ge=1, le=365),
    admin: User = Depends(get_current_admin_user)
):
    """Get platform analytics"""
    try:
        analytics = await admin_service.get_platform_analytics(days)
        return analytics
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

@router.get("/analytics/user-growth")
async def get_user_growth(
    days: int = Query(30, ge=1, le=365),
    admin: User = Depends(get_current_admin_user)
):
    """Get user growth data"""
    try:
        growth = await admin_service.get_user_growth(days)
        return growth
    except Exception as e:
        logger.error(f"Error getting user growth: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user growth")

@router.get("/analytics/revenue")
async def get_revenue_analytics(
    days: int = Query(30, ge=1, le=365),
    admin: User = Depends(get_current_admin_user)
):
    """Get revenue analytics"""
    try:
        revenue = await admin_service.get_revenue_analytics(days)
        return revenue
    except Exception as e:
        logger.error(f"Error getting revenue analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get revenue analytics")

# Logs
@router.get("/logs")
async def get_system_logs(
    level: Optional[str] = None,
    limit: int = Query(100, ge=1, le=1000),
    admin: User = Depends(get_current_admin_user)
):
    """Get system logs"""
    try:
        logs = await admin_service.get_system_logs(level, limit)
        return logs
    except Exception as e:
        logger.error(f"Error getting logs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get logs")

# Maintenance
@router.post("/maintenance/cache-clear")
async def clear_cache(
    admin: User = Depends(get_current_admin_user)
):
    """Clear system cache"""
    try:
        await admin_service.clear_cache()
        return {"message": "Cache cleared"}
    except Exception as e:
        logger.error(f"Error clearing cache: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to clear cache")

@router.post("/maintenance/database-backup")
async def create_database_backup(
    admin: User = Depends(get_current_admin_user)
):
    """Create database backup"""
    try:
        backup = await admin_service.create_backup()
        return backup
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create backup")