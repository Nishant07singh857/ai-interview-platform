"""
Email Tasks - Background email processing tasks
"""

from celery import shared_task
from app.core.email import email_sender
from app.core.database import firebase_client
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def send_email(self, to_email: str, subject: str, template: str, context: Dict[str, Any]):
    """Send email with retry logic"""
    try:
        email_sender.send_template_email(to_email, subject, template, context)
        logger.info(f"Email sent to {to_email}")
        return {"status": "sent", "email": to_email}
    except Exception as exc:
        logger.error(f"Failed to send email to {to_email}: {str(exc)}")
        self.retry(exc=exc, countdown=60 * (self.request.retries + 1))

@shared_task
def send_bulk_emails(emails: List[Dict[str, Any]]):
    """Send emails in bulk"""
    results = {"success": 0, "failed": 0, "errors": []}
    
    for email_data in emails:
        try:
            send_email.delay(
                email_data["to"],
                email_data["subject"],
                email_data["template"],
                email_data["context"]
            )
            results["success"] += 1
        except Exception as e:
            results["failed"] += 1
            results["errors"].append({
                "email": email_data["to"],
                "error": str(e)
            })
    
    return results

@shared_task
def process_email_queue():
    """Process pending emails from queue"""
    queue = firebase_client.get_data("email_queue") or {}
    
    results = {"processed": 0, "failed": 0}
    
    for email_id, email_data in queue.items():
        try:
            send_email.delay(
                email_data["to"],
                email_data["subject"],
                email_data["template"],
                email_data["context"]
            )
            # Remove from queue
            firebase_client.delete_data(f"email_queue/{email_id}")
            results["processed"] += 1
        except Exception as e:
            logger.error(f"Error processing email {email_id}: {str(e)}")
            results["failed"] += 1
    
    return results

@shared_task
def send_welcome_email(user_id: str, email: str, name: str):
    """Send welcome email to new user"""
    context = {
        "user_name": name,
        "login_url": "https://aiinterview.com/login",
        "getting_started_url": "https://aiinterview.com/getting-started"
    }
    
    send_email.delay(
        email,
        "Welcome to AI Interview Platform!",
        "welcome",
        context
    )

@shared_task
def send_password_reset_email(email: str, reset_token: str):
    """Send password reset email"""
    context = {
        "reset_url": f"https://aiinterview.com/reset-password?token={reset_token}",
        "expires_in": "1 hour"
    }
    
    send_email.delay(
        email,
        "Reset Your Password",
        "password_reset",
        context
    )

@shared_task
def send_verification_email(email: str, verification_token: str):
    """Send email verification email"""
    context = {
        "verify_url": f"https://aiinterview.com/verify-email?token={verification_token}",
        "expires_in": "24 hours"
    }
    
    send_email.delay(
        email,
        "Verify Your Email",
        "email_verification",
        context
    )

@shared_task
def send_practice_reminder(user_id: str, email: str, name: str, days_inactive: int):
    """Send practice reminder email"""
    context = {
        "user_name": name,
        "days_inactive": days_inactive,
        "practice_url": "https://aiinterview.com/practice",
        "streak_url": "https://aiinterview.com/dashboard"
    }
    
    send_email.delay(
        email,
        "Don't Break Your Streak!",
        "practice_reminder",
        context
    )

@shared_task
def send_weekly_report_email(user_id: str, email: str, name: str, report_data: Dict[str, Any]):
    """Send weekly progress report email"""
    context = {
        "user_name": name,
        "week_start": report_data.get("week_start"),
        "week_end": report_data.get("week_end"),
        "questions_attempted": report_data.get("questions_attempted", 0),
        "accuracy": report_data.get("accuracy", 0),
        "time_spent": report_data.get("time_spent", 0),
        "streak": report_data.get("streak", 0),
        "improved_topics": report_data.get("improved_topics", []),
        "report_url": "https://aiinterview.com/analytics"
    }
    
    send_email.delay(
        email,
        f"Your Weekly Progress Report - {context['week_start']}",
        "weekly_report",
        context
    )

@shared_task
def send_achievement_unlocked_email(user_id: str, email: str, name: str, achievement: Dict[str, Any]):
    """Send achievement unlocked email"""
    context = {
        "user_name": name,
        "achievement_name": achievement.get("name"),
        "achievement_description": achievement.get("description"),
        "achievement_icon": achievement.get("icon"),
        "share_url": f"https://aiinterview.com/achievements/{achievement.get('id')}"
    }
    
    send_email.delay(
        email,
        f"🏆 Achievement Unlocked: {achievement.get('name')}",
        "achievement_unlocked",
        context
    )

@shared_task
def send_subscription_confirmation(user_id: str, email: str, name: str, plan: str):
    """Send subscription confirmation email"""
    context = {
        "user_name": name,
        "plan": plan.capitalize(),
        "features": get_plan_features(plan),
        "billing_url": "https://aiinterview.com/billing",
        "support_email": "support@aiinterview.com"
    }
    
    send_email.delay(
        email,
        f"Welcome to {plan.capitalize()} Plan!",
        "subscription_confirmed",
        context
    )

@shared_task
def send_payment_failed_email(user_id: str, email: str, name: str, reason: str):
    """Send payment failed notification email"""
    context = {
        "user_name": name,
        "reason": reason,
        "update_payment_url": "https://aiinterview.com/billing/payment-methods",
        "support_email": "support@aiinterview.com"
    }
    
    send_email.delay(
        email,
        "Action Required: Payment Failed",
        "payment_failed",
        context
    )

@shared_task
def send_subscription_cancelled_email(user_id: str, email: str, name: str, effective_date: str):
    """Send subscription cancellation confirmation email"""
    context = {
        "user_name": name,
        "effective_date": effective_date,
        "reactivate_url": "https://aiinterview.com/billing/subscription",
        "feedback_url": "https://aiinterview.com/feedback"
    }
    
    send_email.delay(
        email,
        "Subscription Cancelled",
        "subscription_cancelled",
        context
    )

def get_plan_features(plan: str) -> List[str]:
    """Get features for a plan"""
    features = {
        "pro": [
            "Unlimited practice questions",
            "Company-specific grids",
            "Advanced analytics",
            "Resume analysis",
            "Priority support"
        ],
        "premium": [
            "Everything in Pro",
            "AI Interviewer with voice/video",
            "Personalized learning roadmap",
            "Mock interviews",
            "1-on-1 mentorship"
        ]
    }
    return features.get(plan.lower(), [])

@shared_task
def cleanup_old_emails(days: int = 30):
    """Clean up old email records"""
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    email_logs = firebase_client.get_data("email_logs") or {}
    deleted = 0
    
    for log_id, log in email_logs.items():
        if log.get("sent_at", "") < cutoff:
            firebase_client.delete_data(f"email_logs/{log_id}")
            deleted += 1
    
    logger.info(f"Cleaned up {deleted} old email logs")
    return {"deleted": deleted}