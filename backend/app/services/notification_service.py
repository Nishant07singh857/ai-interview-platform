"""
Notification Service - Complete notification system logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from uuid import uuid4

from app.core.database import firebase_client
from app.core.email import email_sender
from app.core.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    """Notification service with complete business logic"""
    
    def __init__(self):
        self.notification_types = {
            "welcome": {
                "title": "Welcome to AI Interview Platform!",
                "template": "welcome_email"
            },
            "streak_milestone": {
                "title": "🔥 Streak Milestone Achieved!",
                "template": "streak_milestone"
            },
            "achievement_unlocked": {
                "title": "🏆 Achievement Unlocked!",
                "template": "achievement_unlocked"
            },
            "practice_reminder": {
                "title": "⏰ Time to Practice!",
                "template": "practice_reminder"
            },
            "weekly_report": {
                "title": "📊 Your Weekly Progress Report",
                "template": "weekly_report"
            },
            "payment_succeeded": {
                "title": "✅ Payment Successful",
                "template": "payment_succeeded"
            },
            "payment_failed": {
                "title": "❌ Payment Failed",
                "template": "payment_failed"
            },
            "subscription_canceled": {
                "title": "📦 Subscription Canceled",
                "template": "subscription_canceled"
            },
            "new_feature": {
                "title": "✨ New Feature Available!",
                "template": "new_feature"
            },
            "tip_of_day": {
                "title": "💡 Tip of the Day",
                "template": "tip_of_day"
            }
        }
    
    async def get_notifications(
        self,
        user_id: str,
        limit: int,
        offset: int,
        unread_only: bool
    ) -> List[Dict[str, Any]]:
        """Get user notifications"""
        
        notifications = firebase_client.get_data(f"notifications/{user_id}") or {}
        
        result = []
        for notif_id, notif in notifications.items():
            if unread_only and notif.get("read", False):
                continue
            
            result.append({
                "notification_id": notif_id,
                "type": notif.get("type"),
                "title": notif.get("title"),
                "message": notif.get("message"),
                "data": notif.get("data"),
                "read": notif.get("read", False),
                "created_at": notif.get("created_at"),
                "link": notif.get("link")
            })
        
        # Sort by created_at desc
        result.sort(key=lambda x: x["created_at"], reverse=True)
        
        return result[offset:offset + limit]
    
    async def create_notification(
        self,
        user_id: str,
        notification_type: str,
        data: Dict[str, Any]
    ) -> str:
        """Create a new notification"""
        
        if notification_type not in self.notification_types:
            logger.warning(f"Unknown notification type: {notification_type}")
            notification_type = "tip_of_day"
        
        type_config = self.notification_types[notification_type]
        
        notification_id = str(uuid4())
        notification = {
            "notification_id": notification_id,
            "type": notification_type,
            "title": type_config["title"],
            "message": data.get("message", ""),
            "data": data,
            "read": False,
            "created_at": datetime.utcnow().isoformat(),
            "link": data.get("link")
        }
        
        firebase_client.set_data(
            f"notifications/{user_id}/{notification_id}",
            notification
        )
        
        # Send email if enabled
        user = firebase_client.get_data(f"users/{user_id}")
        if user and user.get("preferences", {}).get("notifications", {}).get("email", True):
            await self._send_email_notification(
                user["email"],
                notification_type,
                data
            )
        
        # Send push if enabled
        if user and user.get("preferences", {}).get("notifications", {}).get("push", True):
            await self._send_push_notification(
                user_id,
                notification
            )
        
        return notification_id
    
    async def _send_email_notification(
        self,
        email: str,
        notification_type: str,
        data: Dict[str, Any]
    ):
        """Send email notification"""
        
        template = self.notification_types[notification_type]["template"]
        
        try:
            await email_sender.send_template_email(
                to_email=email,
                template_name=template,
                context=data
            )
        except Exception as e:
            logger.error(f"Error sending email notification: {str(e)}")
    
    async def _send_push_notification(self, user_id: str, notification: Dict):
        """Send push notification"""
        
        # Get user's push subscriptions
        subscriptions = firebase_client.get_data(f"push_subscriptions/{user_id}") or {}
        
        for sub_id, subscription in subscriptions.items():
            try:
                # Send push notification using web-push
                # This would integrate with web-push library
                await self._send_web_push(subscription, notification)
            except Exception as e:
                logger.error(f"Error sending push notification: {str(e)}")
                # Remove invalid subscription
                if "expired" in str(e).lower():
                    firebase_client.delete_data(f"push_subscriptions/{user_id}/{sub_id}")
    
    async def _send_web_push(self, subscription: Dict, notification: Dict):
        """Send web push notification"""
        # Implementation would use web-push library
        # This is a placeholder for the actual implementation
        pass
    
    async def mark_as_read(self, user_id: str, notification_id: str):
        """Mark notification as read"""
        
        notification = firebase_client.get_data(
            f"notifications/{user_id}/{notification_id}"
        )
        
        if notification:
            notification["read"] = True
            firebase_client.set_data(
                f"notifications/{user_id}/{notification_id}",
                notification
            )
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Mark all notifications as read"""
        
        notifications = firebase_client.get_data(f"notifications/{user_id}") or {}
        count = 0
        
        for notif_id, notif in notifications.items():
            if not notif.get("read", False):
                notif["read"] = True
                firebase_client.set_data(
                    f"notifications/{user_id}/{notif_id}",
                    notif
                )
                count += 1
        
        return count
    
    async def delete_notification(self, user_id: str, notification_id: str):
        """Delete a notification"""
        
        firebase_client.delete_data(f"notifications/{user_id}/{notification_id}")
    
    async def delete_all_notifications(self, user_id: str) -> int:
        """Delete all notifications"""
        
        notifications = firebase_client.get_data(f"notifications/{user_id}") or {}
        count = len(notifications)
        
        firebase_client.delete_data(f"notifications/{user_id}")
        
        return count
    
    async def get_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get notification preferences"""
        
        user = firebase_client.get_data(f"users/{user_id}")
        if user:
            return user.get("preferences", {}).get("notifications", {
                "email": True,
                "push": True,
                "daily_reminder": True,
                "weekly_report": True
            })
        
        return {
            "email": True,
            "push": True,
            "daily_reminder": True,
            "weekly_report": True
        }
    
    async def update_preferences(self, user_id: str, preferences: Dict) -> Dict:
        """Update notification preferences"""
        
        user = firebase_client.get_data(f"users/{user_id}")
        if user:
            current_prefs = user.get("preferences", {})
            current_prefs["notifications"] = preferences
            firebase_client.update_data(f"users/{user_id}", {
                "preferences": current_prefs
            })
        
        return preferences
    
    async def subscribe_push(self, user_id: str, subscription: Dict):
        """Subscribe to push notifications"""
        
        sub_id = str(uuid4())
        firebase_client.set_data(
            f"push_subscriptions/{user_id}/{sub_id}",
            subscription
        )
    
    async def unsubscribe_push(self, user_id: str):
        """Unsubscribe from push notifications"""
        
        firebase_client.delete_data(f"push_subscriptions/{user_id}")
    
    async def get_unread_count(self, user_id: str) -> int:
        """Get unread notifications count"""
        
        notifications = firebase_client.get_data(f"notifications/{user_id}") or {}
        
        return sum(1 for n in notifications.values() if not n.get("read", False))
    
    # Scheduled notifications
    async def send_daily_reminders(self):
        """Send daily practice reminders"""
        
        users = firebase_client.get_data("users") or {}
        
        for user_id, user in users.items():
            # Check if user wants daily reminders
            prefs = user.get("preferences", {}).get("notifications", {})
            if not prefs.get("daily_reminder", True):
                continue
            
            # Check if user has practiced today
            today = datetime.utcnow().strftime("%Y-%m-%d")
            progress = firebase_client.get_data(f"progress/{user_id}/{today}")
            
            if not progress or progress.get("questions_attempted", 0) == 0:
                await self.create_notification(
                    user_id,
                    "practice_reminder",
                    {
                        "message": "Don't forget to practice today!",
                        "link": "/practice"
                    }
                )
    
    async def send_weekly_reports(self):
        """Send weekly progress reports"""
        
        users = firebase_client.get_data("users") or {}
        
        for user_id, user in users.items():
            # Check if user wants weekly reports
            prefs = user.get("preferences", {}).get("notifications", {})
            if not prefs.get("weekly_report", True):
                continue
            
            # Calculate weekly stats
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
            
            week_attempts = [
                a for a in attempts.values()
                if a.get("attempted_at", "") >= week_ago
            ]
            
            total = len(week_attempts)
            correct = sum(1 for a in week_attempts if a.get("is_correct", False))
            accuracy = round(correct / total * 100, 2) if total > 0 else 0
            
            await self.create_notification(
                user_id,
                "weekly_report",
                {
                    "message": f"Last week you completed {total} questions with {accuracy}% accuracy",
                    "total_questions": total,
                    "accuracy": accuracy,
                    "link": "/analytics"
                }
            )