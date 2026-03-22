"""
Admin Service - Admin panel functionality
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from uuid import uuid4

from app.core.database import firebase_client
from app.core.cache import cache_manager
from app.core.storage import storage_service
from app.services.user_service import UserService
from app.services.payment_service import PaymentService

logger = logging.getLogger(__name__)

class AdminService:
    """Admin service for platform management"""
    
    def __init__(self):
        self.user_service = UserService()
        self.payment_service = PaymentService()
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """Get admin dashboard data"""
        
        # Get counts
        users = firebase_client.get_data("users") or {}
        questions = firebase_client.get_data("questions") or {}
        companies = firebase_client.get_data("companies") or {}
        
        # Calculate active users (last 30 days)
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        active_users = 0
        for user in users.values():
            last_login = user.get("last_login", "")
            if last_login > thirty_days_ago:
                active_users += 1
        
        # Get recent users
        recent_users = []
        for user_id, user in list(users.items())[:10]:
            recent_users.append({
                "uid": user_id,
                "email": user.get("email"),
                "display_name": user.get("display_name"),
                "created_at": user.get("created_at"),
                "role": user.get("role")
            })
        
        # Get storage usage
        storage_usage = await self._get_storage_usage()
        
        return {
            "total_users": len(users),
            "total_questions": len(questions),
            "total_companies": len(companies),
            "active_users_30d": active_users,
            "premium_users": sum(1 for u in users.values() if u.get("role") in ["pro", "premium"]),
            "recent_users": recent_users,
            "storage_usage": storage_usage
        }
    
    async def _get_storage_usage(self) -> Dict[str, Any]:
        """Get storage usage statistics"""
        try:
            files = await storage_service.list_files()
            total_size = sum(f.get("size", 0) for f in files)
            return {
                "total_files": len(files),
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "by_type": self._group_files_by_type(files)
            }
        except:
            return {
                "total_files": 0,
                "total_size_mb": 0,
                "by_type": {}
            }
    
    def _group_files_by_type(self, files: List[Dict]) -> Dict[str, int]:
        """Group files by extension"""
        groups = {}
        for f in files:
            name = f.get("name", "")
            ext = name.split(".")[-1] if "." in name else "unknown"
            groups[ext] = groups.get(ext, 0) + 1
        return groups
    
    async def get_all_users(
        self,
        skip: int,
        limit: int,
        role: Optional[str],
        status: Optional[str],
        search: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get all users with filters"""
        
        users_data = firebase_client.get_data("users") or {}
        
        users = []
        for user_id, user in users_data.items():
            # Apply filters
            if role and user.get("role") != role:
                continue
            if status and user.get("status") != status:
                continue
            if search:
                search_lower = search.lower()
                email = user.get("email", "").lower()
                name = user.get("display_name", "").lower()
                if search_lower not in email and search_lower not in name:
                    continue
            
            users.append({
                "uid": user_id,
                "email": user.get("email"),
                "display_name": user.get("display_name"),
                "role": user.get("role"),
                "status": user.get("status", "active"),
                "created_at": user.get("created_at"),
                "last_login": user.get("last_login")
            })
        
        # Sort by created_at desc
        users.sort(key=lambda x: x["created_at"], reverse=True)
        
        return users[skip:skip + limit]
    
    async def get_user_details(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed user information"""
        
        user = firebase_client.get_data(f"users/{user_id}")
        if not user:
            return None
        
        # Get user's attempts
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        total_attempts = len(attempts)
        correct_attempts = sum(1 for a in attempts.values() if a.get("is_correct", False))
        
        # Get user's subscriptions
        subscriptions = firebase_client.get_data(f"subscriptions/{user_id}") or {}
        
        # Get user's practice sessions
        sessions = firebase_client.get_data(f"practice_sessions/{user_id}") or {}
        
        return {
            **user,
            "uid": user_id,
            "stats": {
                "total_attempts": total_attempts,
                "correct_attempts": correct_attempts,
                "accuracy": round(correct_attempts / total_attempts * 100, 2) if total_attempts > 0 else 0,
                "total_sessions": len(sessions)
            },
            "subscriptions": list(subscriptions.values()),
            "recent_activity": await self._get_user_recent_activity(user_id, 10)
        }
    
    async def _get_user_recent_activity(self, user_id: str, limit: int) -> List[Dict]:
        """Get user's recent activity"""
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        activities = []
        for attempt_id, attempt in list(attempts.items())[:limit]:
            activities.append({
                "type": "attempt",
                "question_id": attempt.get("question_id"),
                "is_correct": attempt.get("is_correct"),
                "timestamp": attempt.get("attempted_at")
            })
        
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]
    
    async def update_user_role(self, user_id: str, role: str):
        """Update user role"""
        firebase_client.update_data(f"users/{user_id}", {
            "role": role,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        # Clear cache
        await cache_manager.delete(f"user:{user_id}")
    
    async def suspend_user(self, user_id: str, reason: str):
        """Suspend user account"""
        firebase_client.update_data(f"users/{user_id}", {
            "status": "suspended",
            "suspension_reason": reason,
            "suspended_at": datetime.utcnow().isoformat(),
            "suspended_by": "admin"
        })
    
    async def activate_user(self, user_id: str):
        """Activate user account"""
        firebase_client.update_data(f"users/{user_id}", {
            "status": "active",
            "activated_at": datetime.utcnow().isoformat()
        })
        # Remove suspension data
        firebase_client.update_data(f"users/{user_id}", {
            "suspension_reason": None,
            "suspended_at": None,
            "suspended_by": None
        })
    
    async def delete_user(self, user_id: str):
        """Delete user account"""
        # Delete user data
        firebase_client.delete_data(f"users/{user_id}")
        firebase_client.delete_data(f"attempts/{user_id}")
        firebase_client.delete_data(f"sessions/{user_id}")
        firebase_client.delete_data(f"subscriptions/{user_id}")
        
        # Clear cache
        await cache_manager.delete(f"user:{user_id}")
    
    async def get_all_questions(
        self,
        skip: int,
        limit: int,
        status: Optional[str],
        subject: Optional[str],
        difficulty: Optional[str]
    ) -> List[Dict[str, Any]]:
        """Get all questions with filters"""
        
        questions_data = firebase_client.get_data("questions") or {}
        
        questions = []
        for qid, question in questions_data.items():
            if status and question.get("status") != status:
                continue
            if subject and question.get("subject") != subject:
                continue
            if difficulty and question.get("difficulty") != difficulty:
                continue
            
            questions.append({
                "question_id": qid,
                "title": question.get("title"),
                "subject": question.get("subject"),
                "topic": question.get("topic"),
                "difficulty": question.get("difficulty"),
                "status": question.get("status"),
                "created_at": question.get("created_at"),
                "times_used": question.get("times_used", 0),
                "correct_rate": question.get("correct_rate", 0)
            })
        
        questions.sort(key=lambda x: x["created_at"], reverse=True)
        return questions[skip:skip + limit]
    
    async def bulk_import_questions(self, questions: List[Dict], created_by: str) -> Dict:
        """Bulk import questions"""
        imported = 0
        errors = []
        
        for q_data in questions:
            try:
                qid = str(uuid4())
                question = {
                    "question_id": qid,
                    "status": "approved",
                    "times_used": 0,
                    "times_correct": 0,
                    "correct_rate": 0,
                    "created_at": datetime.utcnow().isoformat(),
                    "created_by": created_by,
                    **q_data
                }
                firebase_client.set_data(f"questions/{qid}", question)
                imported += 1
            except Exception as e:
                errors.append({"question": q_data.get("title"), "error": str(e)})
        
        return {
            "imported": imported,
            "failed": len(errors),
            "errors": errors
        }
    
    async def approve_question(self, question_id: str):
        """Approve a question"""
        firebase_client.update_data(f"questions/{question_id}", {
            "status": "approved",
            "reviewed_at": datetime.utcnow().isoformat()
        })
    
    async def reject_question(self, question_id: str, reason: str):
        """Reject a question"""
        firebase_client.update_data(f"questions/{question_id}", {
            "status": "rejected",
            "rejection_reason": reason,
            "reviewed_at": datetime.utcnow().isoformat()
        })
    
    async def get_content_reports(self, status: Optional[str], limit: int) -> List[Dict]:
        """Get content reports"""
        reports = firebase_client.get_data("reports") or {}
        
        result = []
        for report_id, report in reports.items():
            if status and report.get("status") != status:
                continue
            result.append({
                "report_id": report_id,
                **report
            })
        
        result.sort(key=lambda x: x["created_at"], reverse=True)
        return result[:limit]
    
    async def resolve_report(self, report_id: str, action: str):
        """Resolve a content report"""
        firebase_client.update_data(f"reports/{report_id}", {
            "status": "resolved",
            "resolution": action,
            "resolved_at": datetime.utcnow().isoformat()
        })
    
    async def get_system_settings(self) -> Dict[str, Any]:
        """Get system settings"""
        settings = firebase_client.get_data("system_settings") or {}
        return settings
    
    async def update_system_settings(self, settings: Dict) -> Dict:
        """Update system settings"""
        current = firebase_client.get_data("system_settings") or {}
        current.update(settings)
        current["updated_at"] = datetime.utcnow().isoformat()
        
        firebase_client.set_data("system_settings", current)
        return current
    
    async def get_platform_analytics(self, days: int) -> Dict[str, Any]:
        """Get platform analytics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        users = firebase_client.get_data("users") or {}
        attempts = firebase_client.get_data("attempts") or {}
        
        # User growth
        user_growth = []
        current = start_date
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            count = sum(1 for u in users.values() 
                       if u.get("created_at", "").startswith(date_str))
            user_growth.append({"date": date_str, "new_users": count})
            current += timedelta(days=1)
        
        # Activity metrics
        total_attempts = 0
        for user_attempts in attempts.values():
            total_attempts += len(user_attempts)
        
        return {
            "user_growth": user_growth,
            "total_users": len(users),
            "total_attempts": total_attempts,
            "average_daily_users": self._calculate_average_daily_users(users, days),
            "premium_conversion_rate": self._calculate_premium_rate(users)
        }
    
    def _calculate_average_daily_users(self, users: Dict, days: int) -> float:
        """Calculate average daily active users"""
        thirty_days_ago = (datetime.utcnow() - timedelta(days=days)).isoformat()
        active = sum(1 for u in users.values() 
                    if u.get("last_login", "") > thirty_days_ago)
        return round(active / days, 2)
    
    def _calculate_premium_rate(self, users: Dict) -> float:
        """Calculate premium conversion rate"""
        total = len(users)
        if total == 0:
            return 0
        premium = sum(1 for u in users.values() 
                     if u.get("role") in ["pro", "premium"])
        return round(premium / total * 100, 2)
    
    async def get_user_growth(self, days: int) -> List[Dict]:
        """Get user growth data"""
        users = firebase_client.get_data("users") or {}
        
        growth = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
            count = sum(1 for u in users.values() 
                       if u.get("created_at", "").startswith(date))
            growth.append({"date": date, "new_users": count})
        
        return growth
    
    async def get_revenue_analytics(self, days: int) -> Dict[str, Any]:
        """Get revenue analytics"""
        return await self.payment_service.get_revenue_report(days)
    
    async def get_system_logs(self, level: Optional[str], limit: int) -> List[Dict]:
        """Get system logs"""
        # This would read from actual log files
        return []
    
    async def clear_cache(self):
        """Clear system cache"""
        await cache_manager.clear_pattern("*")
    
    async def create_backup(self) -> Dict[str, Any]:
        """Create database backup"""
        from scripts.backup_db import DatabaseBackup
        backup = DatabaseBackup()
        return await backup.create_backup()