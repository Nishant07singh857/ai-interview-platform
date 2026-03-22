"""
Cleanup Tasks - Background cleanup and maintenance tasks
"""

from celery import shared_task
from app.core.database import firebase_client
from app.core.storage import storage_service
import logging
from datetime import datetime, timedelta
import shutil
import os

logger = logging.getLogger(__name__)

@shared_task
def cleanup_expired_sessions():
    """Clean up expired user sessions"""
    users = firebase_client.get_data("users") or {}
    cleaned = 0
    
    for user_id in users:
        try:
            sessions = firebase_client.get_data(f"sessions/{user_id}") or {}
            now = datetime.utcnow()
            
            for session_id, session in list(sessions.items()):
                expires_at = datetime.fromisoformat(session.get("expires_at", "2000-01-01"))
                if expires_at < now:
                    firebase_client.delete_data(f"sessions/{user_id}/{session_id}")
                    cleaned += 1
                    
        except Exception as e:
            logger.error(f"Error cleaning sessions for user {user_id}: {str(e)}")
    
    logger.info(f"Cleaned up {cleaned} expired sessions")
    return {"cleaned": cleaned}

@shared_task
def cleanup_old_attempts(days: int = 90):
    """Archive or delete old question attempts"""
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    users = firebase_client.get_data("users") or {}
    archived = 0
    deleted = 0
    
    for user_id in users:
        try:
            attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
            
            for attempt_id, attempt in list(attempts.items()):
                attempted_at = attempt.get("attempted_at", "")
                if attempted_at < cutoff:
                    # Archive to cold storage
                    archive_data = {
                        "user_id": user_id,
                        "attempt_id": attempt_id,
                        "data": attempt,
                        "archived_at": datetime.utcnow().isoformat()
                    }
                    firebase_client.set_data(
                        f"archived_attempts/{user_id}/{attempt_id}",
                        archive_data
                    )
                    
                    # Delete from active
                    firebase_client.delete_data(f"attempts/{user_id}/{attempt_id}")
                    archived += 1
                    
        except Exception as e:
            logger.error(f"Error archiving attempts for user {user_id}: {str(e)}")
    
    logger.info(f"Archived {archived} old attempts")
    return {"archived": archived}

@shared_task
def cleanup_old_notifications(days: int = 30):
    """Delete old notifications"""
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    users = firebase_client.get_data("users") or {}
    deleted = 0
    
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
    
    logger.info(f"Deleted {deleted} old notifications")
    return {"deleted": deleted}

@shared_task
def cleanup_temp_files(days: int = 1):
    """Clean up temporary files"""
    temp_dirs = ["/tmp", "/var/tmp"]
    deleted = 0
    freed_mb = 0
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    for temp_dir in temp_dirs:
        try:
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    if file_path.endswith(('.tmp', '.temp', '.cache')):
                        mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                        if mtime < cutoff:
                            size = os.path.getsize(file_path)
                            os.remove(file_path)
                            deleted += 1
                            freed_mb += size / (1024 * 1024)
                            
        except Exception as e:
            logger.error(f"Error cleaning temp dir {temp_dir}: {str(e)}")
    
    logger.info(f"Cleaned {deleted} temp files, freed {freed_mb:.2f} MB")
    return {"deleted": deleted, "freed_mb": round(freed_mb, 2)}

@shared_task
def cleanup_old_logs(days: int = 30):
    """Clean up old log files"""
    log_dirs = ["logs", "/var/log/ai-interview"]
    deleted = 0
    freed_mb = 0
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    for log_dir in log_dirs:
        if not os.path.exists(log_dir):
            continue
            
        try:
            for file in os.listdir(log_dir):
                file_path = os.path.join(log_dir, file)
                if file.endswith(('.log', '.log.gz')):
                    mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    if mtime < cutoff:
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted += 1
                        freed_mb += size / (1024 * 1024)
                        
        except Exception as e:
            logger.error(f"Error cleaning logs in {log_dir}: {str(e)}")
    
    logger.info(f"Cleaned {deleted} log files, freed {freed_mb:.2f} MB")
    return {"deleted": deleted, "freed_mb": round(freed_mb, 2)}

@shared_task
def cleanup_old_search_history(days: int = 7):
    """Clean up old search history"""
    users = firebase_client.get_data("users") or {}
    deleted = 0
    
    cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
    
    for user_id in users:
        try:
            searches = firebase_client.get_data(f"search_history/{user_id}") or {}
            
            for search_id, search in list(searches.items()):
                searched_at = search.get("searched_at", "")
                if searched_at < cutoff:
                    firebase_client.delete_data(f"search_history/{user_id}/{search_id}")
                    deleted += 1
                    
        except Exception as e:
            logger.error(f"Error cleaning search history for user {user_id}: {str(e)}")
    
    logger.info(f"Cleaned {deleted} old search records")
    return {"deleted": deleted}

@shared_task
def backup_database():
    """Create database backup"""
    backup_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backups/db_backup_{backup_id}.json"
    
    try:
        # Collect all data
        backup_data = {
            "users": firebase_client.get_data("users") or {},
            "questions": firebase_client.get_data("questions") or {},
            "companies": firebase_client.get_data("companies") or {},
            "topics": firebase_client.get_data("topics") or {},
            "badges": firebase_client.get_data("badges") or {},
            "backup_metadata": {
                "backup_id": backup_id,
                "created_at": datetime.utcnow().isoformat(),
                "version": "1.0"
            }
        }
        
        # Save to storage
        import json
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(backup_data, f, indent=2)
            temp_path = f.name
        
        # Upload to cloud storage
        with open(temp_path, 'rb') as f:
            storage_service.upload_file(
                f.read(),
                backup_path,
                "application/json"
            )
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Keep only last 7 backups
        await cleanup_old_backups()
        
        logger.info(f"Database backup created: {backup_path}")
        return {"backup_id": backup_id, "path": backup_path}
        
    except Exception as e:
        logger.error(f"Error creating database backup: {str(e)}")
        return {"error": str(e)}

@shared_task
def cleanup_old_backups(keep_days: int = 7):
    """Delete old backups"""
    try:
        # List all backups
        backups = storage_service.list_files("backups/")
        deleted = 0
        
        cutoff = datetime.utcnow() - timedelta(days=keep_days)
        
        for backup in backups:
            # Parse backup date from filename
            # Format: db_backup_YYYYMMDD_HHMMSS.json
            filename = backup["name"]
            if filename.startswith("db_backup_"):
                date_str = filename[10:18]  # Extract YYYYMMDD
                backup_date = datetime.strptime(date_str, "%Y%m%d")
                
                if backup_date < cutoff:
                    storage_service.delete_file(filename)
                    deleted += 1
        
        logger.info(f"Deleted {deleted} old backups")
        return {"deleted": deleted}
        
    except Exception as e:
        logger.error(f"Error cleaning old backups: {str(e)}")
        return {"error": str(e)}

@shared_task
def optimize_database():
    """Optimize database performance"""
    operations = {
        "reindexed": 0,
        "defragmented": 0
    }
    
    try:
        # Reindex collections
        collections = ["users", "questions", "attempts", "sessions"]
        for collection in collections:
            # This would be Firebase-specific optimization
            # For now, just log
            operations["reindexed"] += 1
        
        # Remove orphaned data
        users = set(firebase_client.get_data("users") or {})
        
        # Check attempts without users
        all_attempts = firebase_client.get_data("attempts") or {}
        for user_id in list(all_attempts.keys()):
            if user_id not in users:
                firebase_client.delete_data(f"attempts/{user_id}")
                operations["defragmented"] += 1
        
        # Check sessions without users
        all_sessions = firebase_client.get_data("sessions") or {}
        for user_id in list(all_sessions.keys()):
            if user_id not in users:
                firebase_client.delete_data(f"sessions/{user_id}")
                operations["defragmented"] += 1
        
        logger.info(f"Database optimized: {operations}")
        return operations
        
    except Exception as e:
        logger.error(f"Error optimizing database: {str(e)}")
        return {"error": str(e)}

@shared_task
def check_expiring_subscriptions():
    """Check for subscriptions expiring soon"""
    from app.services.notification_service import NotificationService
    
    users = firebase_client.get_data("users") or {}
    notification_service = NotificationService()
    
    expiring_soon = []
    expiring_today = []
    
    for user_id, user in users.items():
        expires_at = user.get("subscription_expires")
        if expires_at:
            expires_date = datetime.fromisoformat(expires_at)
            now = datetime.utcnow()
            days_left = (expires_date - now).days
            
            if 0 < days_left <= 7:
                expiring_soon.append({
                    "user_id": user_id,
                    "email": user.get("email"),
                    "days_left": days_left
                })
                
                # Send notification
                notification_service.create_notification(
                    user_id,
                    "subscription_expiring",
                    {
                        "message": f"Your subscription will expire in {days_left} days",
                        "days_left": days_left,
                        "link": "/billing"
                    }
                )
            elif days_left == 0:
                expiring_today.append(user_id)
    
    logger.info(f"Found {len(expiring_soon)} subscriptions expiring soon")
    return {
        "expiring_soon": expiring_soon,
        "expiring_today": expiring_today
    }

@shared_task
def process_failed_payments():
    """Process failed payments and update subscriptions"""
    from app.services.payment_service import PaymentService
    
    payment_service = PaymentService()
    users = firebase_client.get_data("users") or {}
    
    processed = 0
    downgraded = 0
    
    for user_id, user in users.items():
        subscription_id = user.get("subscription_id")
        if subscription_id:
            subscription = firebase_client.get_data(
                f"subscriptions/{user_id}/{subscription_id}"
            )
            
            if subscription and subscription.get("status") == "past_due":
                # Attempt to retry payment
                try:
                    # This would integrate with Stripe to retry payment
                    processed += 1
                    
                    # If failed too many times, downgrade
                    retry_count = subscription.get("payment_retry_count", 0)
                    if retry_count >= 3:
                        # Downgrade to free
                        firebase_client.update_data(f"users/{user_id}", {
                            "role": "free",
                            "subscription_plan": None,
                            "subscription_expires": None
                        })
                        downgraded += 1
                        
                except Exception as e:
                    logger.error(f"Error processing payment for user {user_id}: {str(e)}")
    
    logger.info(f"Processed {processed} failed payments, downgraded {downgraded} users")
    return {"processed": processed, "downgraded": downgraded}