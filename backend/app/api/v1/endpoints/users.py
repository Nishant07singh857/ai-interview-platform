"""
User Endpoints - Complete user management API
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import List, Optional
import logging

from app.core.database import firebase_client
from app.core.security import security_manager
from app.core.deps import get_current_user, get_current_admin_user
from app.models.user import User, UserProfile, UserRole
from app.schemas.user import (
    UserUpdate, UserResponse, UserDetailResponse, 
    UserProfileResponse, UserPreferencesUpdate,
    UserTargetUpdate, UserStatsResponse
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])
logger = logging.getLogger(__name__)
user_service = UserService()

@router.get("/me", response_model=UserDetailResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user details"""
    try:
        user = await user_service.get_user_details(current_user.uid)
        return user
    except Exception as e:
        logger.error(f"Error getting user details: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user details")

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    try:
        updated_user = await user_service.update_user(
            current_user.uid,
            user_update.dict(exclude_unset=True)
        )
        return updated_user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user")

@router.delete("/me")
async def delete_current_user(
    current_user: User = Depends(get_current_user)
):
    """Delete current user account"""
    try:
        await user_service.delete_user(current_user.uid)
        logger.info(f"User deleted: {current_user.uid}")
        return {"message": "User account deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete user")

@router.get("/me/profile", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user public profile"""
    try:
        profile = await user_service.get_user_profile(current_user.uid)
        return profile
    except Exception as e:
        logger.error(f"Error getting user profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.put("/me/preferences")
async def update_user_preferences(
    preferences: UserPreferencesUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update user preferences"""
    try:
        await user_service.update_preferences(
            current_user.uid,
            preferences.dict(exclude_unset=True)
        )
        return {"message": "Preferences updated successfully"}
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")

@router.put("/me/targets")
async def update_user_targets(
    targets: UserTargetUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update target companies and roles"""
    try:
        await user_service.update_targets(
            current_user.uid,
            targets.dict(exclude_unset=True)
        )
        return {"message": "Targets updated successfully"}
    except Exception as e:
        logger.error(f"Error updating targets: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update targets")

@router.get("/me/stats", response_model=UserStatsResponse)
async def get_user_stats(
    current_user: User = Depends(get_current_user)
):
    """Get user statistics"""
    try:
        stats = await user_service.get_user_stats(current_user.uid)
        return stats
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user statistics")

@router.post("/me/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload profile picture"""
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Validate file size (max 5MB)
        file_size = 0
        content = await file.read()
        file_size = len(content)
        if file_size > 5 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size too large (max 5MB)")
        
        # Upload to Firebase Storage
        photo_url = await user_service.upload_profile_picture(
            current_user.uid,
            content,
            file.filename
        )
        
        return {"photo_url": photo_url}
    except Exception as e:
        logger.error(f"Error uploading profile picture: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload profile picture")

@router.get("/me/progress")
async def get_user_progress(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user)
):
    """Get user progress over time"""
    try:
        progress = await user_service.get_progress_over_time(current_user.uid, days)
        return progress
    except Exception as e:
        logger.error(f"Error getting progress: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get progress")

@router.get("/me/activity")
async def get_user_activity(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user)
):
    """Get recent user activity"""
    try:
        activity = await user_service.get_recent_activity(current_user.uid, limit)
        return {"activities": activity}
    except Exception as e:
        logger.error(f"Error getting activity: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get activity")

@router.get("/me/achievements")
async def get_user_achievements(
    current_user: User = Depends(get_current_user)
):
    """Get user achievements and badges"""
    try:
        achievements = await user_service.get_achievements(current_user.uid)
        return achievements
    except Exception as e:
        logger.error(f"Error getting achievements: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get achievements")

@router.get("/me/weak-areas")
async def get_weak_areas(
    current_user: User = Depends(get_current_user)
):
    """Get user's weak areas for improvement"""
    try:
        weak_areas = await user_service.analyze_weak_areas(current_user.uid)
        return weak_areas
    except Exception as e:
        logger.error(f"Error analyzing weak areas: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze weak areas")

@router.get("/me/recommendations")
async def get_personalized_recommendations(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user)
):
    """Get personalized question recommendations"""
    try:
        recommendations = await user_service.get_recommendations(current_user.uid, limit)
        return {"recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

# Admin endpoints
@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    role: Optional[UserRole] = None,
    admin: User = Depends(get_current_admin_user)
):
    """Get all users (admin only)"""
    try:
        users = await user_service.get_all_users(skip, limit, role)
        return users
    except Exception as e:
        logger.error(f"Error getting users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get users")

@router.get("/{user_id}", response_model=UserDetailResponse)
async def get_user_by_id(
    user_id: str,
    admin: User = Depends(get_current_admin_user)
):
    """Get user by ID (admin only)"""
    try:
        user = await user_service.get_user_details(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user")

@router.put("/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: UserRole,
    admin: User = Depends(get_current_admin_user)
):
    """Update user role (admin only)"""
    try:
        await user_service.update_user_role(user_id, role)
        logger.info(f"User role updated: {user_id} -> {role}")
        return {"message": f"User role updated to {role}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user role: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update user role")

@router.post("/{user_id}/suspend")
async def suspend_user(
    user_id: str,
    reason: str,
    admin: User = Depends(get_current_admin_user)
):
    """Suspend user account (admin only)"""
    try:
        await user_service.suspend_user(user_id, reason)
        logger.info(f"User suspended: {user_id}")
        return {"message": "User suspended successfully"}
    except Exception as e:
        logger.error(f"Error suspending user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to suspend user")

@router.post("/{user_id}/activate")
async def activate_user(
    user_id: str,
    admin: User = Depends(get_current_admin_user)
):
    """Activate user account (admin only)"""
    try:
        await user_service.activate_user(user_id)
        logger.info(f"User activated: {user_id}")
        return {"message": "User activated successfully"}
    except Exception as e:
        logger.error(f"Error activating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to activate user")

@router.get("/search/{query}")
async def search_users(
    query: str,
    limit: int = Query(10, ge=1, le=50),
    admin: User = Depends(get_current_admin_user)
):
    """Search users (admin only)"""
    try:
        users = await user_service.search_users(query, limit)
        return {"users": users}
    except Exception as e:
        logger.error(f"Error searching users: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search users")

@router.get("/stats/overall")
async def get_overall_stats(
    admin: User = Depends(get_current_admin_user)
):
    """Get overall platform statistics (admin only)"""
    try:
        stats = await user_service.get_platform_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting platform stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get platform stats")