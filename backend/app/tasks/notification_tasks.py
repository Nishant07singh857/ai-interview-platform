"""
Notification Tasks - Background notification processing
"""

from celery import shared_task
from app.core.database import firebase_client
from app.services.notification_service import NotificationService
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
notification_service = NotificationService()

@shared_task
def send_daily_reminders():
    """Send daily practice reminders"""
    users = firebase_client.get_data("users") or {}
    sent = 0
    
    for user_id, user in users.items():
        try:
            # Check user preferences
            prefs = user.get("preferences", {}).get("notifications", {})
            if not prefs.get("daily_reminder", True):
                continue
            
            # Check if user has practiced today
            today = datetime.utcnow().strftime("%Y-%m-%d")
            progress = firebase_client.get_data(f"progress/{user_id}/{today}")
            
            if not progress or progress.get("questions_attempted", 0) == 0:
                # Calculate days since last practice
                last_practice = await get_last_practice_date(user_id)
                days_inactive = (datetime.utcnow().date() - last_practice).days if last_practice else 0
                
                notification_service.create_notification(
                    user_id,
                    "practice_reminder",
                    {
                        "message": "Don't forget to practice today!",
                        "days_inactive": days_inactive,
                        "link": "/practice"
                    }
                )
                sent += 1
                
        except Exception as e:
            logger.error(f"Error sending reminder to user {user_id}: {str(e)}")
    
    logger.info(f"Sent {sent} daily reminders")
    return {"sent": sent}

async def get_last_practice_date(user_id: str):
    """Get user's last practice date"""
    progress = firebase_client.get_data(f"progress/{user_id}") or {}
    if progress:
        dates = sorted(progress.keys(), reverse=True)
        if dates:
            return datetime.strptime(dates[0], "%Y-%m-%d").date()
    return None

@shared_task
def send_achievement_notifications():
    """Send notifications for new achievements"""
    users = firebase_client.get_data("users") or {}
    sent = 0
    
    for user_id in users:
        try:
            # Check for new achievements
            achievements = firebase_client.get_data(f"achievements/{user_id}") or {}
            
            for achievement_id, achievement in achievements.items():
                if not achievement.get("notified", False):
                    # Send notification
                    notification_service.create_notification(
                        user_id,
                        "achievement_unlocked",
                        {
                            "message": f"🏆 Achievement Unlocked: {achievement.get('name')}",
                            "achievement_name": achievement.get("name"),
                            "achievement_description": achievement.get("description"),
                            "achievement_icon": achievement.get("icon"),
                            "link": f"/profile?achievement={achievement_id}"
                        }
                    )
                    
                    # Mark as notified
                    achievement["notified"] = True
                    firebase_client.set_data(
                        f"achievements/{user_id}/{achievement_id}",
                        achievement
                    )
                    sent += 1
                    
        except Exception as e:
            logger.error(f"Error sending achievement notification to user {user_id}: {str(e)}")
    
    logger.info(f"Sent {sent} achievement notifications")
    return {"sent": sent}

@shared_task
def send_streak_milestone_notifications():
    """Send notifications for streak milestones"""
    users = firebase_client.get_data("users") or {}
    sent = 0
    
    milestones = [7, 14, 30, 60, 90, 180, 365]
    
    for user_id, user in users.items():
        try:
            stats = user.get("stats", {})
            current_streak = stats.get("current_streak", 0)
            
            # Check if streak hit a milestone
            if current_streak in milestones:
                # Check if already notified for this milestone
                notified_streaks = user.get("notified_streaks", [])
                if current_streak not in notified_streaks:
                    notification_service.create_notification(
                        user_id,
                        "streak_milestone",
                        {
                            "message": f"🔥 Amazing! You've reached a {current_streak}-day streak!",
                            "streak": current_streak,
                            "link": "/dashboard"
                        }
                    )
                    
                    # Update notified streaks
                    notified_streaks.append(current_streak)
                    firebase_client.update_data(f"users/{user_id}", {
                        "notified_streaks": notified_streaks
                    })
                    sent += 1
                    
        except Exception as e:
            logger.error(f"Error sending streak notification to user {user_id}: {str(e)}")
    
    logger.info(f"Sent {sent} streak milestone notifications")
    return {"sent": sent}

@shared_task
def send_question_suggestion_notifications():
    """Send notifications with question suggestions based on weak areas"""
    from app.services.analytics_service import AnalyticsService
    
    analytics_service = AnalyticsService()
    users = firebase_client.get_data("users") or {}
    sent = 0
    
    for user_id in users:
        try:
            # Get user's weak areas
            weak_areas = analytics_service.get_weak_topics(user_id, 3)
            
            if weak_areas:
                topics = [area["topic"] for area in weak_areas]
                
                notification_service.create_notification(
                    user_id,
                    "question_suggestion",
                    {
                        "message": f"Based on your performance, practice these topics: {', '.join(topics)}",
                        "topics": topics,
                        "link": "/practice/topic-wise"
                    }
                )
                sent += 1
                
        except Exception as e:
            logger.error(f"Error sending question suggestion to user {user_id}: {str(e)}")
    
    logger.info(f"Sent {sent} question suggestion notifications")
    return {"sent": sent}

@shared_task
def send_weekly_summary_notifications():
    """Send weekly summary notifications"""
    from app.services.analytics_service import AnalyticsService
    
    analytics_service = AnalyticsService()
    users = firebase_client.get_data("users") or {}
    sent = 0
    
    for user_id, user in users.items():
        try:
            # Check preferences
            prefs = user.get("preferences", {}).get("notifications", {})
            if not prefs.get("weekly_report", True):
                continue
            
            # Get weekly stats
            week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
            attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
            
            week_attempts = [
                a for a in attempts.values()
                if a.get("attempted_at", "") >= week_ago
            ]
            
            if week_attempts:
                total = len(week_attempts)
                correct = sum(1 for a in week_attempts if a.get("is_correct", False))
                accuracy = round(correct / total * 100, 2) if total > 0 else 0
                
                notification_service.create_notification(
                    user_id,
                    "weekly_summary",
                    {
                        "message": f"📊 Weekly Summary: {total} questions, {accuracy}% accuracy",
                        "total_questions": total,
                        "accuracy": accuracy,
                        "link": "/analytics"
                    }
                )
                sent += 1
                
        except Exception as e:
            logger.error(f"Error sending weekly summary to user {user_id}: {str(e)}")
    
    logger.info(f"Sent {sent} weekly summary notifications")
    return {"sent": sent}

@shared_task
def send_company_update_notifications():
    """Send notifications about company interview updates"""
    users = firebase_client.get_data("users") or {}
    sent = 0
    
    # Get companies with recent updates
    recent_companies = get_recently_updated_companies()
    
    for user_id, user in users.items():
        try:
            target_companies = user.get("target_companies", [])
            
            for company in recent_companies:
                if company["name"] in target_companies:
                    notification_service.create_notification(
                        user_id,
                        "company_update",
                        {
                            "message": f"📢 New interview experiences added for {company['name']}",
                            "company": company["name"],
                            "new_count": company["new_count"],
                            "link": f"/companies/{company['id']}"
                        }
                    )
                    sent += 1
                    
        except Exception as e:
            logger.error(f"Error sending company update to user {user_id}: {str(e)}")
    
    logger.info(f"Sent {sent} company update notifications")
    return {"sent": sent}

def get_recently_updated_companies() -> list:
    """Get companies with recent updates"""
    companies = firebase_client.get_data("companies") or {}
    recent = []
    
    for company_id, company in companies.items():
        # Check for new interview experiences in last 7 days
        experiences = firebase_client.query_firestore(
            "interview_experiences",
            "company_id",
            "==",
            company_id
        )
        
        week_ago = (datetime.utcnow() - timedelta(days=7)).isoformat()
        new_experiences = [
            e for e in experiences
            if e.get("created_at", "") >= week_ago
        ]
        
        if new_experiences:
            recent.append({
                "id": company_id,
                "name": company.get("name"),
                "new_count": len(new_experiences)
            })
    
    return recent

@shared_task
def cleanup_old_notifications(days: int = 30):
    """Delete old read notifications"""
    users = firebase_client.get_data("users") or {}
    deleted = 0
    
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    for user_id in users:
        try:
            notifications = firebase_client.get_data(f"notifications/{user_id}") or {}
            
            for notif_id, notif in list(notifications.items()):
                created_at = notif.get("created_at", "")
                if created_at < cutoff and notif.get("read", False):
                    firebase_client.delete_data(f"notifications/{user_id}/{notif_id}")
                    deleted += 1
                    
        except Exception as e:
            logger.error(f"Error cleaning notifications for user {user_id}: {str(e)}")
    
    logger.info(f"Cleaned up {deleted} old notifications")
    return {"deleted": deleted}