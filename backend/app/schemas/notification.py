"""
Notification Schemas - Pydantic models for notifications
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Request Schemas
class NotificationPreferencesUpdate(BaseModel):
    """Update notification preferences request"""
    email: Optional[bool] = None
    push: Optional[bool] = None
    daily_reminder: Optional[bool] = None
    weekly_report: Optional[bool] = None

# Response Schemas
class NotificationResponse(BaseModel):
    """Notification response"""
    notification_id: str
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    read: bool = False
    created_at: str
    link: Optional[str] = None
    
    class Config:
        from_attributes = True

class NotificationPreferencesResponse(BaseModel):
    """Notification preferences response"""
    email: bool = True
    push: bool = True
    daily_reminder: bool = True
    weekly_report: bool = True
    
    class Config:
        from_attributes = True

# Export all schemas
__all__ = [
    'NotificationPreferencesUpdate',
    'NotificationResponse',
    'NotificationPreferencesResponse'
]