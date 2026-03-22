"""
Celery Application - Background task processing configuration
"""

from celery import Celery
from celery.schedules import crontab
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create Celery instance
celery_app = Celery(
    "ai_interview",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.analytics_tasks",
        "app.tasks.cleanup_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.report_tasks"
    ]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,  # 1 hour
    beat_schedule={
        # Daily tasks
        "send-daily-reminders": {
            "task": "app.tasks.notification_tasks.send_daily_reminders",
            "schedule": crontab(hour=9, minute=0),  # 9 AM daily
        },
        "cleanup-expired-sessions": {
            "task": "app.tasks.cleanup_tasks.cleanup_expired_sessions",
            "schedule": crontab(hour=0, minute=0),  # Midnight daily
        },
        
        # Weekly tasks
        "send-weekly-reports": {
            "task": "app.tasks.report_tasks.send_weekly_reports",
            "schedule": crontab(day_of_week="monday", hour=8, minute=0),  # Monday 8 AM
        },
        "generate-weekly-analytics": {
            "task": "app.tasks.analytics_tasks.generate_weekly_analytics",
            "schedule": crontab(day_of_week="sunday", hour=23, minute=59),  # Sunday midnight
        },
        
        # Monthly tasks
        "cleanup-old-logs": {
            "task": "app.tasks.cleanup_tasks.cleanup_old_logs",
            "schedule": crontab(day_of_month="1", hour=2, minute=0),  # 1st of month
        },
        "generate-monthly-reports": {
            "task": "app.tasks.report_tasks.generate_monthly_reports",
            "schedule": crontab(day_of_month="1", hour=3, minute=0),  # 1st of month
        },
        
        # Analytics tasks
        "update-user-streaks": {
            "task": "app.tasks.analytics_tasks.update_user_streaks",
            "schedule": crontab(hour="*/6"),  # Every 6 hours
        },
        "calculate-topic-mastery": {
            "task": "app.tasks.analytics_tasks.calculate_topic_mastery",
            "schedule": crontab(hour=2, minute=30),  # Daily at 2:30 AM
        },
        "update-leaderboards": {
            "task": "app.tasks.analytics_tasks.update_leaderboards",
            "schedule": crontab(hour="*/4"),  # Every 4 hours
        },
        
        # Maintenance tasks
        "backup-database": {
            "task": "app.tasks.cleanup_tasks.backup_database",
            "schedule": crontab(hour=3, minute=0),  # Daily at 3 AM
        },
        "optimize-database": {
            "task": "app.tasks.cleanup_tasks.optimize_database",
            "schedule": crontab(day_of_week="sunday", hour=4, minute=0),  # Weekly
        },
        
        # Email tasks
        "send-pending-emails": {
            "task": "app.tasks.email_tasks.process_email_queue",
            "schedule": crontab(minute="*/5"),  # Every 5 minutes
        },
        
        # Subscription tasks
        "check-expiring-subscriptions": {
            "task": "app.tasks.cleanup_tasks.check_expiring_subscriptions",
            "schedule": crontab(hour=10, minute=0),  # Daily at 10 AM
        },
        "process-failed-payments": {
            "task": "app.tasks.cleanup_tasks.process_failed_payments",
            "schedule": crontab(hour="*/6"),  # Every 6 hours
        },
    },
)

@celery_app.task(bind=True)
def debug_task(self):
    """Debug task to verify Celery is working"""
    logger.info(f"Request: {self.request!r}")
    return {"status": "ok", "task_id": self.request.id}

@celery_app.task
def test_task():
    """Simple test task"""
    logger.info("Test task executed")
    return {"message": "Test task completed successfully"}

# Task monitoring
@celery_app.task
def task_failure_handler(self, exc, task_id, args, kwargs, einfo):
    """Handle task failures"""
    logger.error(f"Task {task_id} failed: {exc}")
    logger.error(f"Error info: {einfo}")

# Startup and shutdown events
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup periodic tasks"""
    logger.info("Celery periodic tasks configured")

@celery_app.on_after_finalize.connect
def setup_tasks(sender, **kwargs):
    """Setup after finalization"""
    logger.info("Celery tasks finalized")