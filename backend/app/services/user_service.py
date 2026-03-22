"""
User Service - Complete user management business logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import hashlib
from uuid import uuid4

from app.core.database import firebase_client
from app.core.security import security_manager
from app.core.storage import storage_service
from app.models.user import User, UserRole, UserStatus, ExperienceLevel
from app.schemas.user import UserResponse, UserDetailResponse, UserProfileResponse

logger = logging.getLogger(__name__)

class UserService:
    """User service with complete business logic"""
    
    async def get_user_details(self, user_id: str) -> Optional[UserDetailResponse]:
        """Get detailed user information"""
        
        # Get user from Firestore
        user_data = firebase_client.get_data(f"users/{user_id}")
        
        if not user_data:
            return None
        
        # Get user stats
        stats = await self.get_user_stats(user_id)
        
        # Get user achievements
        achievements = await self.get_achievements(user_id)
        
        # Combine data
        user_data["stats"] = stats.dict() if stats else {}
        user_data["achievements"] = achievements
        
        return UserDetailResponse(**user_data)
    
    async def get_user_profile(self, user_id: str) -> Optional[UserProfileResponse]:
        """Get public user profile"""
        
        user_data = firebase_client.get_data(f"users/{user_id}")
        
        if not user_data:
            return None
        
        # Only include public fields
        profile_data = {
            "uid": user_data.get("uid"),
            "display_name": user_data.get("display_name"),
            "photo_url": user_data.get("photo_url"),
            "bio": user_data.get("bio"),
            "current_company": user_data.get("current_company"),
            "current_role": user_data.get("current_role"),
            "experience_level": user_data.get("experience_level", ExperienceLevel.BEGINNER),
            "skills": user_data.get("skills", {"technical": [], "soft": [], "domain": []}),
            "stats": user_data.get("stats", {}),
            "created_at": user_data.get("created_at")
        }
        
        return UserProfileResponse(**profile_data)
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> UserResponse:
        """Update user information"""
        
        # Add updated timestamp
        update_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Update in Firestore
        success = firebase_client.update_data(f"users/{user_id}", update_data)
        
        if not success:
            raise ValueError("Failed to update user")
        
        # Get updated user
        user_data = firebase_client.get_data(f"users/{user_id}")
        
        return UserResponse(**user_data)
    
    async def delete_user(self, user_id: str):
        """Delete user account"""
        
        # Delete user from Firebase Auth
        firebase_client.delete_user(user_id)
        
        # Delete user data from Firestore
        firebase_client.delete_data(f"users/{user_id}")
        
        # Delete user sessions
        firebase_client.delete_data(f"sessions/{user_id}")
        
        # Delete user progress
        firebase_client.delete_data(f"progress/{user_id}")
        
        # Delete user attempts
        firebase_client.delete_data(f"attempts/{user_id}")
    
    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]):
        """Update user preferences"""
        
        current_preferences = firebase_client.get_data(f"users/{user_id}/preferences") or {}
        current_preferences.update(preferences)
        
        firebase_client.update_data(f"users/{user_id}", {
            "preferences": current_preferences
        })
    
    async def update_targets(self, user_id: str, targets: Dict[str, Any]):
        """Update user targets"""
        
        firebase_client.update_data(f"users/{user_id}", targets)
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user statistics"""
        
        # Get all attempts
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        total_questions = len(attempts)
        correct_answers = sum(1 for a in attempts.values() if a.get("is_correct", False))
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        # Get practice sessions
        sessions = firebase_client.get_data(f"sessions/{user_id}/practice") or {}
        total_tests = len([s for s in sessions.values() if s.get("type") == "mock_test"])
        
        # Calculate average score
        scores = [s.get("score", 0) for s in sessions.values() if s.get("score")]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Get streak
        streak_data = await self._calculate_streak(user_id)
        
        # Subject breakdown
        subject_breakdown = await self._get_subject_breakdown(user_id, attempts)
        
        return {
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "accuracy": round(accuracy, 2),
            "current_streak": streak_data["current_streak"],
            "longest_streak": streak_data["longest_streak"],
            "total_practice_time": await self._get_total_practice_time(user_id),
            "total_tests_taken": total_tests,
            "average_score": round(avg_score, 2),
            "subjects_breakdown": subject_breakdown,
            "recent_activity": await self._get_recent_activity(user_id, 10)
        }
    
    async def _calculate_streak(self, user_id: str) -> Dict[str, int]:
        """Calculate user streak"""
        
        progress = firebase_client.get_data(f"progress/{user_id}") or {}
        
        if not progress:
            return {"current_streak": 0, "longest_streak": 0}
        
        # Sort dates
        dates = sorted(progress.keys(), reverse=True)
        
        current_streak = 0
        longest_streak = 0
        streak = 0
        last_date = None
        
        for date_str in dates:
            current_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            if last_date:
                # Check if consecutive
                if (last_date - current_date).days == 1:
                    streak += 1
                else:
                    streak = 1
            else:
                streak = 1
            
            longest_streak = max(longest_streak, streak)
            last_date = current_date
        
        # Check if today is included in streak
        today = datetime.utcnow().date()
        if dates and datetime.strptime(dates[0], "%Y-%m-%d").date() == today:
            current_streak = streak
        
        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak
        }
    
    async def _get_subject_breakdown(self, user_id: str, attempts: Dict) -> Dict:
        """Get performance breakdown by subject"""
        
        subjects = {}
        
        for attempt_id, attempt in attempts.items():
            question_id = attempt.get("question_id")
            
            # Get question details
            question = firebase_client.get_data(f"questions/{question_id}")
            
            if question:
                subject = question.get("subject")
                
                if subject not in subjects:
                    subjects[subject] = {
                        "total": 0,
                        "correct": 0,
                        "incorrect": 0,
                        "accuracy": 0
                    }
                
                subjects[subject]["total"] += 1
                if attempt.get("is_correct"):
                    subjects[subject]["correct"] += 1
                else:
                    subjects[subject]["incorrect"] += 1
                
                subjects[subject]["accuracy"] = round(
                    subjects[subject]["correct"] / subjects[subject]["total"] * 100, 2
                )
        
        return subjects
    
    async def _get_total_practice_time(self, user_id: str) -> int:
        """Get total practice time in minutes"""
        
        sessions = firebase_client.get_data(f"sessions/{user_id}/practice") or {}
        
        total_time = 0
        for session in sessions.values():
            if session.get("time_spent"):
                total_time += session["time_spent"]
        
        return total_time // 60  # Convert seconds to minutes
    
    async def _get_recent_activity(self, user_id: str, limit: int) -> List[Dict]:
        """Get recent user activity"""
        
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        activities = []
        for attempt_id, attempt in attempts.items():
            activities.append({
                "type": "attempt",
                "question_id": attempt.get("question_id"),
                "is_correct": attempt.get("is_correct"),
                "timestamp": attempt.get("attempted_at")
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return activities[:limit]
    
    async def get_progress_over_time(self, user_id: str, days: int) -> List[Dict]:
        """Get user progress over specified time period"""
        
        progress = firebase_client.get_data(f"progress/{user_id}") or {}
        
        # Calculate date range
        end_date = datetime.utcnow().date()
        start_date = end_date - timedelta(days=days)
        
        result = []
        current_date = start_date
        
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            day_progress = progress.get(date_str, {})
            
            result.append({
                "date": date_str,
                "questions_attempted": day_progress.get("questions_attempted", 0),
                "correct_answers": day_progress.get("correct_answers", 0),
                "accuracy": day_progress.get("accuracy", 0),
                "time_spent": day_progress.get("time_spent", 0)
            })
            
            current_date += timedelta(days=1)
        
        return result
    
    async def get_recent_activity(self, user_id: str, limit: int) -> List[Dict]:
        """Get recent user activity with details"""
        
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        activities = []
        for attempt_id, attempt in list(attempts.items())[:limit]:
            # Get question details
            question = firebase_client.get_data(f"questions/{attempt.get('question_id')}")
            
            activities.append({
                "id": attempt_id,
                "type": "question_attempt",
                "question_title": question.get("title") if question else "Unknown Question",
                "subject": question.get("subject") if question else None,
                "difficulty": question.get("difficulty") if question else None,
                "is_correct": attempt.get("is_correct"),
                "time_taken": attempt.get("time_taken_seconds"),
                "timestamp": attempt.get("attempted_at")
            })
        
        # Add practice sessions
        sessions = firebase_client.get_data(f"sessions/{user_id}/practice") or {}
        for session_id, session in list(sessions.items())[:limit]:
            activities.append({
                "id": session_id,
                "type": "practice_session",
                "session_type": session.get("session_type"),
                "score": session.get("score"),
                "accuracy": session.get("accuracy"),
                "questions_answered": session.get("questions_answered"),
                "timestamp": session.get("start_time")
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return activities[:limit]
    
    async def get_achievements(self, user_id: str) -> List[Dict]:
        """Get user achievements and badges"""
        
        achievements = firebase_client.get_data(f"achievements/{user_id}") or {}
        
        result = []
        for achievement_id, achievement in achievements.items():
            result.append({
                "id": achievement_id,
                "name": achievement.get("name"),
                "description": achievement.get("description"),
                "icon": achievement.get("icon"),
                "category": achievement.get("category"),
                "earned_at": achievement.get("earned_at"),
                "progress": achievement.get("progress", 100)
            })
        
        return result
    
    async def analyze_weak_areas(self, user_id: str) -> Dict[str, Any]:
        """Analyze user's weak areas for improvement"""
        
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        # Group by subject and topic
        performance = {}
        
        for attempt_id, attempt in attempts.items():
            question_id = attempt.get("question_id")
            question = firebase_client.get_data(f"questions/{question_id}")
            
            if question:
                subject = question.get("subject")
                topic = question.get("topic")
                
                if subject not in performance:
                    performance[subject] = {}
                
                if topic not in performance[subject]:
                    performance[subject][topic] = {
                        "total": 0,
                        "correct": 0,
                        "incorrect": 0
                    }
                
                performance[subject][topic]["total"] += 1
                if attempt.get("is_correct"):
                    performance[subject][topic]["correct"] += 1
                else:
                    performance[subject][topic]["incorrect"] += 1
        
        # Calculate accuracy and identify weak areas
        weak_areas = []
        for subject, topics in performance.items():
            for topic, stats in topics.items():
                if stats["total"] >= 5:  # Only consider topics with enough attempts
                    accuracy = stats["correct"] / stats["total"] * 100
                    if accuracy < 60:  # Weak if accuracy below 60%
                        weak_areas.append({
                            "subject": subject,
                            "topic": topic,
                            "accuracy": round(accuracy, 2),
                            "total_attempts": stats["total"],
                            "correct": stats["correct"],
                            "incorrect": stats["incorrect"],
                            "priority": "high" if accuracy < 40 else "medium"
                        })
        
        # Sort by accuracy (lowest first)
        weak_areas.sort(key=lambda x: x["accuracy"])
        
        return {
            "weak_areas": weak_areas,
            "total_weak_topics": len(weak_areas),
            "recommendations": await self._generate_recommendations(weak_areas)
        }
    
    async def _generate_recommendations(self, weak_areas: List[Dict]) -> List[str]:
        """Generate recommendations based on weak areas"""
        
        recommendations = []
        
        for area in weak_areas[:5]:  # Top 5 weak areas
            if area["priority"] == "high":
                recommendations.append(
                    f"Focus on mastering {area['topic']} in {area['subject']} - "
                    f"your accuracy is only {area['accuracy']}%"
                )
            else:
                recommendations.append(
                    f"Practice more {area['topic']} questions in {area['subject']} "
                    f"to improve your {area['accuracy']}% accuracy"
                )
        
        return recommendations
    
    async def get_recommendations(self, user_id: str, limit: int) -> List[Dict]:
        """Get personalized question recommendations"""
        
        # Get weak areas
        weak_areas_analysis = await self.analyze_weak_areas(user_id)
        weak_areas = weak_areas_analysis["weak_areas"]
        
        recommendations = []
        
        for area in weak_areas[:limit]:
            # Find questions in this topic that user hasn't attempted or got wrong
            questions = firebase_client.query_firestore(
                "questions",
                "topic",
                "==",
                area["topic"]
            )
            
            for question in questions[:3]:  # Limit per topic
                # Check if user has attempted this question
                attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
                attempted = any(
                    a.get("question_id") == question["question_id"]
                    for a in attempts.values()
                )
                
                if not attempted or any(
                    a.get("question_id") == question["question_id"] and not a.get("is_correct")
                    for a in attempts.values()
                ):
                    recommendations.append({
                        "question_id": question["question_id"],
                        "title": question["title"],
                        "subject": question["subject"],
                        "topic": question["topic"],
                        "difficulty": question["difficulty"],
                        "reason": f"This will help improve your {area['topic']} skills",
                        "priority": area["priority"]
                    })
        
        return recommendations[:limit]
    
    async def upload_profile_picture(self, user_id: str, file_content: bytes, filename: str) -> str:
        """Upload profile picture to storage"""
        
        # Generate unique filename
        file_ext = filename.split('.')[-1]
        new_filename = f"profile_pictures/{user_id}/{uuid4()}.{file_ext}"
        
        # Upload to storage
        photo_url = await storage_service.upload_file(
            file_content,
            new_filename,
            content_type=f"image/{file_ext}"
        )
        
        # Update user profile
        firebase_client.update_data(f"users/{user_id}", {
            "photo_url": photo_url
        })
        
        return photo_url
    
    async def get_all_users(self, skip: int, limit: int, role: Optional[UserRole]) -> List[UserResponse]:
        """Get all users (admin)"""
        
        users_data = firebase_client.get_data("users") or {}
        
        users = []
        for user_id, user_data in users_data.items():
            if role and user_data.get("role") != role:
                continue
            users.append(UserResponse(**user_data))
        
        # Sort by created_at
        users.sort(key=lambda x: x.created_at, reverse=True)
        
        return users[skip:skip + limit]
    
    async def update_user_role(self, user_id: str, role: UserRole):
        """Update user role (admin)"""
        
        firebase_client.update_data(f"users/{user_id}", {
            "role": role,
            "updated_at": datetime.utcnow().isoformat()
        })
    
    async def suspend_user(self, user_id: str, reason: str):
        """Suspend user account (admin)"""
        
        firebase_client.update_data(f"users/{user_id}", {
            "status": "suspended",
            "suspension_reason": reason,
            "suspended_at": datetime.utcnow().isoformat(),
            "suspended_by": "admin"
        })
    
    async def activate_user(self, user_id: str):
        """Activate user account (admin)"""
        
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
    
    async def search_users(self, query: str, limit: int) -> List[UserResponse]:
        """Search users (admin)"""
        
        users_data = firebase_client.get_data("users") or {}
        
        results = []
        query = query.lower()
        
        for user_id, user_data in users_data.items():
            # Search in email, display_name, etc.
            if (query in user_data.get("email", "").lower() or
                query in user_data.get("display_name", "").lower() or
                query in user_data.get("current_company", "").lower()):
                results.append(UserResponse(**user_data))
            
            if len(results) >= limit:
                break
        
        return results
    
    async def get_platform_stats(self) -> Dict[str, Any]:
        """Get overall platform statistics (admin)"""
        
        users = firebase_client.get_data("users") or {}
        questions = firebase_client.get_data("questions") or {}
        attempts = firebase_client.get_data("attempts") or {}
        
        # Count active users (last 30 days)
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        active_users = 0
        
        for user_id, user_data in users.items():
            last_login = user_data.get("last_login")
            if last_login and last_login > thirty_days_ago:
                active_users += 1
        
        # Calculate average accuracy
        total_attempts = 0
        total_correct = 0
        
        for user_id, user_attempts in attempts.items():
            for attempt_id, attempt in user_attempts.items():
                total_attempts += 1
                if attempt.get("is_correct"):
                    total_correct += 1
        
        avg_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            "total_users": len(users),
            "active_users_last_30_days": active_users,
            "total_questions": len(questions),
            "total_attempts": total_attempts,
            "average_accuracy": round(avg_accuracy, 2),
            "premium_users": sum(1 for u in users.values() if u.get("role") in ["pro", "premium"]),
            "questions_by_subject": await self._count_questions_by_subject(questions),
            "users_by_role": await self._count_users_by_role(users)
        }
    
    async def _count_questions_by_subject(self, questions: Dict) -> Dict[str, int]:
        """Count questions by subject"""
        
        counts = {}
        for question_id, question in questions.items():
            subject = question.get("subject")
            counts[subject] = counts.get(subject, 0) + 1
        
        return counts
    
    async def _count_users_by_role(self, users: Dict) -> Dict[str, int]:
        """Count users by role"""
        
        counts = {}
        for user_id, user in users.items():
            role = user.get("role", "free")
            counts[role] = counts.get(role, 0) + 1
        
        return counts