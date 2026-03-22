"""
Notifications Endpoints - Complete notification system API
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.notification import (
    NotificationResponse, NotificationPreferencesResponse
)
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])
logger = logging.getLogger(__name__)
notification_service = NotificationService()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    unread_only: bool = False,
    current_user: User = Depends(get_current_user)
):
    """Get user notifications"""
    try:
        notifications = await notification_service.get_notifications(
            current_user.uid, limit, offset, unread_only
        )
        return notifications
    except Exception as e:
        logger.error(f"Error getting notifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get notifications")

@router.post("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Mark notification as read"""
    try:
        await notification_service.mark_as_read(current_user.uid, notification_id)
        return {"message": "Notification marked as read"}
    except Exception as e:
        logger.error(f"Error marking notification as read: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to mark as read")

@router.post("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user)
):
    """Mark all notifications as read"""
    try:
        count = await notification_service.mark_all_as_read(current_user.uid)
        return {"message": f"{count} notifications marked as read"}
    except Exception as e:
        logger.error(f"Error marking all as read: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to mark all as read")

@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a notification"""
    try:
        await notification_service.delete_notification(current_user.uid, notification_id)
        return {"message": "Notification deleted"}
    except Exception as e:
        logger.error(f"Error deleting notification: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete notification")

@router.delete("/")
async def delete_all_notifications(
    current_user: User = Depends(get_current_user)
):
    """Delete all notifications"""
    try:
        count = await notification_service.delete_all_notifications(current_user.uid)
        return {"message": f"{count} notifications deleted"}
    except Exception as e:
        logger.error(f"Error deleting all notifications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete all notifications")

@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_preferences(
    current_user: User = Depends(get_current_user)
):
    """Get notification preferences"""
    try:
        preferences = await notification_service.get_preferences(current_user.uid)
        return preferences
    except Exception as e:
        logger.error(f"Error getting preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get preferences")

@router.put("/preferences")
async def update_preferences(
    preferences: dict,
    current_user: User = Depends(get_current_user)
):
    """Update notification preferences"""
    try:
        updated = await notification_service.update_preferences(
            current_user.uid, preferences
        )
        return updated
    except Exception as e:
        logger.error(f"Error updating preferences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update preferences")

@router.post("/push/subscribe")
async def subscribe_push(
    subscription: dict,
    current_user: User = Depends(get_current_user)
):
    """Subscribe to push notifications"""
    try:
        await notification_service.subscribe_push(current_user.uid, subscription)
        return {"message": "Push subscription successful"}
    except Exception as e:
        logger.error(f"Error subscribing to push: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to subscribe to push")

@router.post("/push/unsubscribe")
async def unsubscribe_push(
    current_user: User = Depends(get_current_user)
):
    """Unsubscribe from push notifications"""
    try:
        await notification_service.unsubscribe_push(current_user.uid)
        return {"message": "Push unsubscription successful"}
    except Exception as e:
        logger.error(f"Error unsubscribing from push: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unsubscribe from push")

@router.get("/unread/count")
async def get_unread_count(
    current_user: User = Depends(get_current_user)
):
    """Get unread notifications count"""
    try:
        count = await notification_service.get_unread_count(current_user.uid)
        return {"count": count}
    except Exception as e:
        logger.error(f"Error getting unread count: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get unread count")