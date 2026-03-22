"""
Analytics Service - Complete analytics business logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
import logging
import statistics
from collections import defaultdict
import json
import tempfile

from app.core.database import firebase_client
from app.core.cache import cache_manager
from app.models.analytics import TimeFrame
from app.core.deps import get_current_user, get_current_admin_user, get_current_pro_user, get_current_user_optional
from app.models.analytics import (
    UserAnalytics, DailyProgress, WeeklyReport,
    SubjectMastery, CompanyReadiness, SkillGap,
    LearningPath, PerformancePrediction, PeerComparison
)
from app.services.practice_service import PracticeService
from app.services.question_service import QuestionService

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Analytics service with complete business logic"""
    
    def __init__(self):
        self.practice_service = PracticeService()
        self.question_service = QuestionService()

    async def _safe_get_question(self, question_id: str):
        """Get question safely without breaking analytics on bad data"""
        try:
            return await self.question_service.get_question(question_id)
        except Exception as e:
            logger.warning(f"Failed to load question {question_id}: {str(e)}")
            return None
    
    async def get_summary(self, user_id: str) -> Dict[str, Any]:
        """Get analytics summary for user"""
        
        # Try cache first
        cache_key = f"analytics_summary:{user_id}"
        cached = await cache_manager.get(cache_key)
        if cached:
            return cached
        
        # Get all attempts
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        # Calculate basic stats
        total_questions = len(attempts)
        correct = sum(1 for a in attempts.values() if a.get("is_correct", False))
        accuracy = (correct / total_questions * 100) if total_questions > 0 else 0
        
        # Get practice sessions
        sessions = firebase_client.get_data(f"practice_sessions/{user_id}") or {}
        
        total_time = 0
        for session in sessions.values():
            total_time += session.get("total_time_spent", 0) // 60  # Convert to minutes
        
        # Get streak
        streak_info = await self._calculate_streak(user_id)
        
        # Calculate average daily time
        days_active = len(await self._get_active_days(user_id))
        avg_daily = total_time / days_active if days_active > 0 else 0
        
        summary = {
            "user_id": user_id,
            "overall_accuracy": round(accuracy, 2),
            "total_questions": total_questions,
            "current_streak": streak_info["current"],
            "longest_streak": streak_info["longest"],
            "total_practice_time": total_time,
            "average_daily_time": round(avg_daily, 2)
        }
        
        # Cache for 1 hour
        await cache_manager.set(cache_key, summary, ttl=3600)
        
        return summary
    
    async def get_trends(self, user_id: str, days: int) -> Dict[str, Any]:
        """Get performance trends over time"""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get daily progress
        progress = firebase_client.get_data(f"progress/{user_id}") or {}
        
        dates = []
        accuracy_trend = []
        volume_trend = []
        time_trend = []
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            day_data = progress.get(date_str, {})
            
            dates.append(date_str)
            accuracy_trend.append(day_data.get("accuracy", 0))
            volume_trend.append(day_data.get("questions_attempted", 0))
            time_trend.append(day_data.get("time_spent", 0))
            
            current_date += timedelta(days=1)
        
        return {
            "dates": dates,
            "accuracy": accuracy_trend,
            "volume": volume_trend,
            "time_spent": time_trend
        }
    
    async def get_subject_performance(self, user_id: str) -> Dict[str, Any]:
        """Get performance by subject"""
        
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        subjects = defaultdict(lambda: {
            "total": 0,
            "correct": 0,
            "incorrect": 0,
            "accuracy": 0,
            "time_spent": 0,
            "trend": []
        })
        
        for attempt_id, attempt in attempts.items():
            question_id = attempt.get("question_id")
            question = await self._safe_get_question(question_id)
            
            if question:
                subject = question.subject.value if hasattr(question.subject, 'value') else question.subject
                
                subjects[subject]["total"] += 1
                if attempt.get("is_correct"):
                    subjects[subject]["correct"] += 1
                else:
                    subjects[subject]["incorrect"] += 1
                
                subjects[subject]["time_spent"] += attempt.get("time_taken_seconds", 0) // 60
        
        # Calculate accuracy
        for subject, data in subjects.items():
            if data["total"] > 0:
                data["accuracy"] = round(data["correct"] / data["total"] * 100, 2)
        
        # Get recent trend (last 7 days)
        for subject in subjects:
            subjects[subject]["trend"] = await self._get_subject_trend(user_id, subject, 7)
        
        return {"subjects": dict(subjects)}
    
    async def _get_subject_trend(self, user_id: str, subject: str, days: int) -> List[float]:
        """Get subject performance trend"""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        progress = firebase_client.get_data(f"progress/{user_id}") or {}
        
        trend = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            day_data = progress.get(date_str, {})
            
            # Get subject-specific accuracy for that day
            subjects_practiced = day_data.get("subjects_practiced", [])
            if subject in subjects_practiced:
                # Would need more detailed data per subject per day
                # Simplified for now
                trend.append(day_data.get("accuracy", 0))
            else:
                trend.append(0)
            
            current_date += timedelta(days=1)
        
        return trend
    
    async def get_subject_details(self, user_id: str, subject: str) -> Dict[str, Any]:
        """Get detailed performance for a specific subject"""
        
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        # Filter attempts for this subject
        subject_attempts = []
        for attempt_id, attempt in attempts.items():
            question_id = attempt.get("question_id")
            question = await self._safe_get_question(question_id)
            
            if question and (question.subject == subject or question.subject.value == subject):
                subject_attempts.append({
                    **attempt,
                    "question": question
                })
        
        # Topic breakdown
        topics = defaultdict(lambda: {
            "total": 0,
            "correct": 0,
            "accuracy": 0,
            "time_spent": 0
        })
        
        for attempt in subject_attempts:
            topic = attempt["question"].topic
            
            topics[topic]["total"] += 1
            if attempt.get("is_correct"):
                topics[topic]["correct"] += 1
            topics[topic]["time_spent"] += attempt.get("time_taken_seconds", 0) // 60
        
        for topic, data in topics.items():
            if data["total"] > 0:
                data["accuracy"] = round(data["correct"] / data["total"] * 100, 2)
        
        # Difficulty breakdown
        difficulties = defaultdict(lambda: {
            "total": 0,
            "correct": 0,
            "accuracy": 0
        })
        
        for attempt in subject_attempts:
            difficulty = attempt["question"].difficulty.value if hasattr(attempt["question"].difficulty, 'value') else attempt["question"].difficulty
            
            difficulties[difficulty]["total"] += 1
            if attempt.get("is_correct"):
                difficulties[difficulty]["correct"] += 1
        
        for difficulty, data in difficulties.items():
            if data["total"] > 0:
                data["accuracy"] = round(data["correct"] / data["total"] * 100, 2)
        
        return {
            "subject": subject,
            "total_attempts": len(subject_attempts),
            "correct": sum(1 for a in subject_attempts if a.get("is_correct")),
            "accuracy": round(sum(1 for a in subject_attempts if a.get("is_correct")) / len(subject_attempts) * 100, 2) if subject_attempts else 0,
            "topics": dict(topics),
            "difficulties": dict(difficulties),
            "time_analysis": await self._get_subject_time_analysis(subject_attempts)
        }
    
    async def _get_subject_time_analysis(self, attempts: List[Dict]) -> Dict[str, Any]:
        """Get time analysis for subject"""
        
        if not attempts:
            return {}
        
        times = [a.get("time_taken_seconds", 0) for a in attempts]
        
        return {
            "average_time": round(statistics.mean(times), 2),
            "median_time": round(statistics.median(times), 2) if times else 0,
            "min_time": min(times) if times else 0,
            "max_time": max(times) if times else 0,
            "total_time": sum(times) // 60  # minutes
        }
    
    async def get_topic_mastery(self, user_id: str, subject: Optional[str]) -> Dict[str, Any]:
        """Get topic mastery levels"""
        
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        topics = defaultdict(lambda: {
            "total": 0,
            "correct": 0,
            "accuracy": 0,
            "mastery_level": "not_started",
            "last_practiced": None,
            "time_spent": 0
        })
        
        for attempt_id, attempt in attempts.items():
            question_id = attempt.get("question_id")
            question = await self._safe_get_question(question_id)
            
            if question and (not subject or question.subject == subject or question.subject.value == subject):
                topic = question.topic
                
                topics[topic]["total"] += 1
                if attempt.get("is_correct"):
                    topics[topic]["correct"] += 1
                
                attempted_at = attempt.get("attempted_at")
                if attempted_at and (not topics[topic]["last_practiced"] or attempted_at > topics[topic]["last_practiced"]):
                    topics[topic]["last_practiced"] = attempted_at
                
                topics[topic]["time_spent"] += attempt.get("time_taken_seconds", 0) // 60
        
        # Calculate mastery levels
        mastered = []
        in_progress = []
        not_started = []
        
        for topic, data in topics.items():
            if data["total"] == 0:
                not_started.append({
                    "topic": topic,
                    "status": "not_started"
                })
            else:
                data["accuracy"] = round(data["correct"] / data["total"] * 100, 2)
                
                if data["total"] >= 10 and data["accuracy"] >= 80:
                    level = "mastered"
                    mastered.append({"topic": topic, **data})
                elif data["total"] >= 5:
                    level = "in_progress"
                    in_progress.append({"topic": topic, **data})
                else:
                    level = "just_started"
                    in_progress.append({"topic": topic, **data})
                
                data["mastery_level"] = level
        
        return {
            "mastered_topics": mastered,
            "in_progress_topics": in_progress,
            "not_started_topics": not_started
        }
    
    async def get_weak_topics(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get weakest topics"""
        
        mastery = await self.get_topic_mastery(user_id, None)
        
        # Combine in_progress and filter by accuracy
        weak_topics = []
        for topic in mastery["in_progress_topics"]:
            if topic.get("accuracy", 100) < 60:
                weak_topics.append({
                    "topic": topic["topic"],
                    "accuracy": topic["accuracy"],
                    "attempts": topic["total"],
                    "priority": "high" if topic["accuracy"] < 40 else "medium"
                })
        
        # Sort by accuracy (lowest first)
        weak_topics.sort(key=lambda x: x["accuracy"])
        
        return weak_topics[:limit]
    
    async def get_strong_topics(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get strongest topics"""
        
        mastery = await self.get_topic_mastery(user_id, None)
        
        strong_topics = []
        for topic in mastery["mastered_topics"] + mastery["in_progress_topics"]:
            if topic.get("accuracy", 0) >= 80:
                strong_topics.append({
                    "topic": topic["topic"],
                    "accuracy": topic["accuracy"],
                    "attempts": topic["total"],
                    "mastery_level": topic.get("mastery_level", "strong")
                })
        
        # Sort by accuracy (highest first)
        strong_topics.sort(key=lambda x: x["accuracy"], reverse=True)
        
        return strong_topics[:limit]
    
    async def get_company_readiness(self, user_id: str) -> Dict[str, Any]:
        """Get readiness scores for target companies"""
        
        # Get user's target companies
        user = firebase_client.get_data(f"users/{user_id}")
        target_companies = user.get("target_companies", [])
        
        if not target_companies:
            # Get top recommended companies
            target_companies = ["Google", "Amazon", "Microsoft", "Meta", "Apple"]
        
        companies = []
        for company in target_companies:
            readiness = await self._calculate_company_readiness(user_id, company)
            companies.append(readiness)
        
        # Get top matches
        all_companies = await self._get_all_company_matches(user_id)
        
        return {
            "companies": companies,
            "top_matches": all_companies[:5]
        }
    
    async def _calculate_company_readiness(self, user_id: str, company: str) -> Dict[str, Any]:
        """Calculate readiness for a specific company"""
        
        # Get company requirements
        requirements = await self._get_company_requirements(company)
        
        # Get user performance
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        # Calculate technical score (based on relevant questions)
        relevant_questions = []
        for attempt_id, attempt in attempts.items():
            question_id = attempt.get("question_id")
            question = await self._safe_get_question(question_id)
            
            if question and company in question.companies:
                relevant_questions.append(attempt)
        
        if relevant_questions:
            technical_score = sum(1 for a in relevant_questions if a.get("is_correct")) / len(relevant_questions) * 100
        else:
            # Estimate based on overall performance
            overall = await self.get_summary(user_id)
            technical_score = overall["overall_accuracy"]
        
        # Behavioral score (placeholder - would come from behavioral assessments)
        behavioral_score = 70
        
        # System design score (placeholder - would come from system design questions)
        system_design_score = 65
        
        # Overall score
        overall_score = (
            technical_score * 0.5 +
            behavioral_score * 0.2 +
            system_design_score * 0.3
        )
        
        # Determine readiness level
        if overall_score >= 85:
            level = "highly_ready"
        elif overall_score >= 70:
            level = "ready"
        elif overall_score >= 50:
            level = "almost_ready"
        else:
            level = "not_ready"
        
        # Calculate success probability (simplified)
        success_prob = min(overall_score * 0.8 + 20, 95)
        
        # Estimate preparation time
        if level == "not_ready":
            prep_time = 90
        elif level == "almost_ready":
            prep_time = 60
        elif level == "ready":
            prep_time = 30
        else:
            prep_time = 0
        
        return {
            "company": company,
            "overall_score": round(overall_score, 2),
            "readiness_level": level,
            "technical_score": round(technical_score, 2),
            "behavioral_score": round(behavioral_score, 2),
            "system_design_score": round(system_design_score, 2),
            "interview_success_probability": round(success_prob, 2),
            "estimated_preparation_time": prep_time,
            "critical_gaps": await self._get_critical_gaps(user_id, company, requirements)
        }
    
    async def _get_company_requirements(self, company: str) -> Dict[str, Any]:
        """Get requirements for a company"""
        # In production, this would come from a database
        requirements_db = {
            "Google": {
                "topics": ["algorithms", "system_design", "machine_learning", "python"],
                "difficulty": "hard"
            },
            "Amazon": {
                "topics": ["system_design", "distributed_systems", "aws", "leadership"],
                "difficulty": "hard"
            },
            "Microsoft": {
                "topics": ["algorithms", "csharp", "azure", "system_design"],
                "difficulty": "hard"
            }
        }
        
        return requirements_db.get(company, {
            "topics": ["general"],
            "difficulty": "medium"
        })
    
    async def _get_critical_gaps(self, user_id: str, company: str, requirements: Dict) -> List[str]:
        """Get critical gaps for a company"""
        
        mastery = await self.get_topic_mastery(user_id, None)
        mastered_topics = {t["topic"] for t in mastery["mastered_topics"]}
        
        required_topics = set(requirements.get("topics", []))
        
        gaps = required_topics - mastered_topics
        return list(gaps)[:5]
    
    async def _get_all_company_matches(self, user_id: str) -> List[Dict[str, Any]]:
        """Get matches for all companies"""
        
        companies = ["Google", "Amazon", "Microsoft", "Meta", "Apple", "Netflix", "Uber", "Airbnb"]
        
        matches = []
        for company in companies:
            readiness = await self._calculate_company_readiness(user_id, company)
            matches.append({
                "company": company,
                "score": readiness["overall_score"],
                "level": readiness["readiness_level"]
            })
        
        matches.sort(key=lambda x: x["score"], reverse=True)
        return matches
    
    async def get_company_details(self, user_id: str, company: str) -> Dict[str, Any]:
        """Get detailed readiness for a specific company"""
        
        # Get base readiness
        readiness = await self._calculate_company_readiness(user_id, company)
        
        # Get topic readiness
        requirements = await self._get_company_requirements(company)
        topic_readiness = {}
        
        for topic in requirements.get("topics", []):
            # Get user performance on this topic
            attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
            topic_attempts = []
            
            for attempt_id, attempt in attempts.items():
                question_id = attempt.get("question_id")
                question = await self._safe_get_question(question_id)
                
                if question and question.topic.lower() == topic.lower():
                    topic_attempts.append(attempt)
            
            if topic_attempts:
                correct = sum(1 for a in topic_attempts if a.get("is_correct"))
                topic_readiness[topic] = round(correct / len(topic_attempts) * 100, 2)
            else:
                topic_readiness[topic] = 0
        
        # Get comparison data
        peers = await self.compare_with_peers(user_id, {"peer_group": "target_company"})
        
        readiness.update({
            "topic_readiness": topic_readiness,
            "vs_peers": peers.get("vs_average", {}),
            "recommended_topics": await self._get_recommended_topics(user_id, company)
        })
        
        return readiness
    
    async def _get_recommended_topics(self, user_id: str, company: str) -> List[str]:
        """Get recommended topics for company"""
        
        mastery = await self.get_topic_mastery(user_id, None)
        weak_topics = await self.get_weak_topics(user_id, 10)
        
        requirements = await self._get_company_requirements(company)
        required_topics = set(requirements.get("topics", []))
        
        # Topics that are both required and weak
        recommendations = [
            t["topic"] for t in weak_topics
            if t["topic"].lower() in {rt.lower() for rt in required_topics}
        ]
        
        return recommendations[:5]
    
    async def get_difficulty_performance(self, user_id: str) -> Dict[str, Any]:
        """Get performance by difficulty level"""
        
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        difficulties = defaultdict(lambda: {
            "total": 0,
            "correct": 0,
            "accuracy": 0,
            "average_time": 0,
            "times": []
        })
        
        for attempt_id, attempt in attempts.items():
            question_id = attempt.get("question_id")
            question = await self._safe_get_question(question_id)
            
            if question:
                difficulty = question.difficulty.value if hasattr(question.difficulty, 'value') else question.difficulty
                
                difficulties[difficulty]["total"] += 1
                if attempt.get("is_correct"):
                    difficulties[difficulty]["correct"] += 1
                
                difficulties[difficulty]["times"].append(attempt.get("time_taken_seconds", 0))
        
        # Calculate averages
        for difficulty, data in difficulties.items():
            if data["total"] > 0:
                data["accuracy"] = round(data["correct"] / data["total"] * 100, 2)
                data["average_time"] = round(statistics.mean(data["times"]), 2)
            
            # Remove raw times list
            del data["times"]
        
        return dict(difficulties)
    
    async def get_question_type_performance(self, user_id: str) -> Dict[str, Any]:
        """Get performance by question type"""
        
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        types = defaultdict(lambda: {
            "total": 0,
            "correct": 0,
            "accuracy": 0,
            "average_time": 0,
            "times": []
        })
        
        for attempt_id, attempt in attempts.items():
            question_id = attempt.get("question_id")
            question = await self._safe_get_question(question_id)
            
            if question:
                qtype = question.type.value if hasattr(question.type, 'value') else question.type
                
                types[qtype]["total"] += 1
                if attempt.get("is_correct"):
                    types[qtype]["correct"] += 1
                
                types[qtype]["times"].append(attempt.get("time_taken_seconds", 0))
        
        # Calculate averages
        for qtype, data in types.items():
            if data["total"] > 0:
                data["accuracy"] = round(data["correct"] / data["total"] * 100, 2)
                data["average_time"] = round(statistics.mean(data["times"]), 2)
            
            del data["times"]
        
        return dict(types)
    
    async def get_time_analysis(self, user_id: str) -> Dict[str, Any]:
        """Get time-based analysis"""
        
        attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        times = [a.get("time_taken_seconds", 0) for a in attempts.values() if a.get("time_taken_seconds")]
        
        if not times:
            return {
                "average_time": 0,
                "median_time": 0,
                "fastest_time": 0,
                "slowest_time": 0,
                "by_difficulty": {},
                "by_type": {}
            }
        
        # Overall stats
        analysis = {
            "average_time": round(statistics.mean(times), 2),
            "median_time": round(statistics.median(times), 2),
            "fastest_time": min(times),
            "slowest_time": max(times)
        }
        
        # By difficulty
        difficulties = await self.get_difficulty_performance(user_id)
        analysis["by_difficulty"] = {
            d: {"average_time": data["average_time"]}
            for d, data in difficulties.items()
        }
        
        # By type
        types = await self.get_question_type_performance(user_id)
        analysis["by_type"] = {
            t: {"average_time": data["average_time"]}
            for t, data in types.items()
        }
        
        return analysis
    
    async def get_weekly_report(self, user_id: str, week_start_str: Optional[str]) -> WeeklyReport:
        """Get weekly performance report"""
        
        # Determine week range
        if week_start_str:
            week_start = date.fromisoformat(week_start_str)
        else:
            # Default to last week
            today = date.today()
            week_start = today - timedelta(days=today.weekday() + 7)  # Previous Monday
        
        week_end = week_start + timedelta(days=6)
        
        # Get progress for the week
        progress = firebase_client.get_data(f"progress/{user_id}") or {}
        
        week_progress = []
        current_date = week_start
        while current_date <= week_end:
            date_str = current_date.isoformat()
            if date_str in progress:
                week_progress.append(progress[date_str])
            else:
                week_progress.append({
                    "questions_attempted": 0,
                    "correct_answers": 0,
                    "accuracy": 0,
                    "time_spent": 0,
                    "subjects_practiced": []
                })
            current_date += timedelta(days=1)
        
        # Calculate totals
        total_questions = sum(d.get("questions_attempted", 0) for d in week_progress)
        total_correct = sum(d.get("correct_answers", 0) for d in week_progress)
        avg_accuracy = (total_correct / total_questions * 100) if total_questions > 0 else 0
        total_time = sum(d.get("time_spent", 0) for d in week_progress)
        active_days = sum(1 for d in week_progress if d.get("questions_attempted", 0) > 0)
        
        # Trends
        accuracy_trend = [d.get("accuracy", 0) for d in week_progress]
        volume_trend = [d.get("questions_attempted", 0) for d in week_progress]
        time_trend = [d.get("time_spent", 0) for d in week_progress]
        
        # Best day
        best_day_index = max(range(len(week_progress)), key=lambda i: week_progress[i].get("accuracy", 0))
        best_day_date = (week_start + timedelta(days=best_day_index)).isoformat()
        
        # Best subject
        subjects_performance = defaultdict(lambda: {"total": 0, "correct": 0})
        for day in week_progress:
            # Would need more detailed data
            pass
        
        # Improvements and declines
        improved_areas = await self._get_improved_areas(user_id, week_start, week_end)
        declined_areas = await self._get_declined_areas(user_id, week_start, week_end)
        
        # Achievements
        achievements = await self._get_weekly_achievements(user_id, week_progress)
        
        # Recommendations
        recommendations = await self._get_weekly_recommendations(user_id, week_progress)
        
        return WeeklyReport(
            user_id=user_id,
            week_start=week_start,
            week_end=week_end,
            total_questions=total_questions,
            average_accuracy=round(avg_accuracy, 2),
            total_time=total_time,
            active_days=active_days,
            accuracy_trend=accuracy_trend,
            volume_trend=volume_trend,
            time_trend=time_trend,
            best_day={"date": best_day_date, "accuracy": week_progress[best_day_index].get("accuracy", 0)},
            best_subject={},  # Would be populated
            best_topic={},    # Would be populated
            improved_areas=improved_areas,
            declined_areas=declined_areas,
            focus_areas=recommendations,
            achievements=achievements
        )
    
    async def _get_improved_areas(self, user_id: str, week_start: date, week_end: date) -> List[Dict]:
        """Get areas that improved this week"""
        # Placeholder - would compare with previous week
        return []
    
    async def _get_declined_areas(self, user_id: str, week_start: date, week_end: date) -> List[Dict]:
        """Get areas that declined this week"""
        # Placeholder - would compare with previous week
        return []
    
    async def _get_weekly_achievements(self, user_id: str, week_progress: List[Dict]) -> List[str]:
        """Get achievements for the week"""
        achievements = []
        
        total_questions = sum(d.get("questions_attempted", 0) for d in week_progress)
        if total_questions >= 100:
            achievements.append("Completed 100+ questions this week")
        elif total_questions >= 50:
            achievements.append("Completed 50+ questions this week")
        
        active_days = sum(1 for d in week_progress if d.get("questions_attempted", 0) > 0)
        if active_days == 7:
            achievements.append("Perfect attendance - practiced every day!")
        elif active_days >= 5:
            achievements.append("Great consistency - practiced 5+ days")
        
        avg_accuracy = statistics.mean([d.get("accuracy", 0) for d in week_progress if d.get("accuracy", 0) > 0]) if any(d.get("accuracy", 0) > 0 for d in week_progress) else 0
        if avg_accuracy >= 80:
            achievements.append(f"Maintained {avg_accuracy:.0f}% average accuracy")
        
        return achievements
    
    async def _get_weekly_recommendations(self, user_id: str, week_progress: List[Dict]) -> List[str]:
        """Get recommendations based on weekly performance"""
        recommendations = []
        
        # Check for consistency issues
        active_days = sum(1 for d in week_progress if d.get("questions_attempted", 0) > 0)
        if active_days < 5:
            recommendations.append("Try to practice more consistently next week")
        
        # Check for accuracy issues
        avg_accuracy = statistics.mean([d.get("accuracy", 0) for d in week_progress if d.get("accuracy", 0) > 0]) if any(d.get("accuracy", 0) > 0 for d in week_progress) else 0
        if avg_accuracy < 60:
            recommendations.append("Focus on reviewing fundamentals to improve accuracy")
        
        # Get weak topics
        weak_topics = await self.get_weak_topics(user_id, 3)
        if weak_topics:
            topics_str = ", ".join([t["topic"] for t in weak_topics])
            recommendations.append(f"Focus on improving: {topics_str}")
        
        return recommendations[:5]
    
    async def generate_learning_path(
        self,
        user_id: str,
        target_role: Optional[str],
        target_companies: List[str]
    ) -> Dict[str, Any]:
        """Generate personalized learning path"""
        
        # Get current state
        weak_topics = await self.get_weak_topics(user_id, 20)
        strong_topics = await self.get_strong_topics(user_id, 10)
        
        # Get company requirements if specified
        required_topics = set()
        if target_companies:
            for company in target_companies:
                reqs = await self._get_company_requirements(company)
                required_topics.update(reqs.get("topics", []))
        
        # Prioritize topics
        priority_topics = []
        for topic in weak_topics:
            if required_topics and topic["topic"].lower() in {rt.lower() for rt in required_topics}:
                priority_topics.append({
                    **topic,
                    "priority": "critical"
                })
            else:
                priority_topics.append({
                    **topic,
                    "priority": "high" if topic["accuracy"] < 50 else "medium"
                })
        
        # Sort by priority
        priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        priority_topics.sort(key=lambda x: priority_order[x["priority"]])
        
        # Generate milestones
        milestones = []
        for i, topic in enumerate(priority_topics[:10]):
            milestones.append({
                "id": f"milestone_{i+1}",
                "title": f"Master {topic['topic']}",
                "description": f"Achieve 80% accuracy in {topic['topic']}",
                "category": "skill",
                "target_date": (date.today() + timedelta(days=(i+1)*7)).isoformat(),
                "completed": False,
                "progress": 0,
                "tasks": [
                    f"Complete 20 questions on {topic['topic']}",
                    f"Review theory and common patterns",
                    f"Take topic-wise practice test"
                ]
            })
        
        # Generate weekly focus
        weekly_focus = []
        for i in range(0, len(priority_topics), 3):
            week_topics = priority_topics[i:i+3]
            weekly_focus.append({
                "week": i//3 + 1,
                "focus_topics": [t["topic"] for t in week_topics],
                "goal": f"Master {len(week_topics)} topics",
                "estimated_hours": len(week_topics) * 5
            })
        
        # Estimate completion date
        total_weeks = len(weekly_focus)
        estimated_completion = date.today() + timedelta(weeks=total_weeks)
        
        return {
            "target_role": target_role,
            "target_companies": target_companies,
            "milestones": milestones,
            "weekly_focus": weekly_focus,
            "estimated_completion": estimated_completion.isoformat()
        }
    
    async def compare_with_peers(self, user_id: str, request: Dict) -> Dict[str, Any]:
        """Compare performance with peers"""
        
        # Get all users
        all_users = firebase_client.get_data("users") or {}
        
        # Get current user's stats
        user_summary = await self.get_summary(user_id)
        
        # Get all user summaries (simplified - would use batch processing)
        peer_summaries = []
        for peer_id in all_users.keys():
            if peer_id != user_id:
                summary = await self.get_summary(peer_id)
                peer_summaries.append(summary)
        
        if not peer_summaries:
            return {
                "percentile": 50,
                "vs_average": {},
                "strengths": [],
                "weaknesses": [],
                "rank": 1
            }
        
        # Calculate percentile for accuracy
        accuracies = [s["overall_accuracy"] for s in peer_summaries]
        user_accuracy = user_summary["overall_accuracy"]
        
        accuracies.sort()
        below_count = sum(1 for a in accuracies if a < user_accuracy)
        percentile = (below_count / len(accuracies)) * 100
        
        # Calculate averages
        avg_accuracy = statistics.mean(accuracies)
        avg_questions = statistics.mean([s["total_questions"] for s in peer_summaries])
        avg_time = statistics.mean([s["total_practice_time"] for s in peer_summaries])
        
        # Calculate rank
        rank = sum(1 for a in accuracies if a > user_accuracy) + 1
        
        # Identify strengths and weaknesses (would use more detailed comparison)
        strengths = ["Overall accuracy is above average"] if user_accuracy > avg_accuracy else []
        weaknesses = ["Overall accuracy is below average"] if user_accuracy < avg_accuracy else []
        
        return {
            "percentile": round(percentile, 2),
            "vs_average": {
                "accuracy": round(user_accuracy - avg_accuracy, 2),
                "questions": round(user_summary["total_questions"] - avg_questions, 2),
                "time": round(user_summary["total_practice_time"] - avg_time, 2)
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "rank": rank
        }
    
    async def get_predictions(self, user_id: str) -> Dict[str, Any]:
        """Get performance predictions"""
        
        # Get historical data
        trends = await self.get_trends(user_id, 90)
        
        # Simple prediction based on recent trend
        recent_accuracies = trends["accuracy"][-14:]  # Last 14 days
        if recent_accuracies:
            avg_recent = statistics.mean([a for a in recent_accuracies if a > 0])
            trend = recent_accuracies[-1] - recent_accuracies[0] if len(recent_accuracies) > 1 else 0
            
            predicted_next_week = avg_recent + trend * 0.3  # Simple projection
            predicted_next_week = min(max(predicted_next_week, 0), 100)
        else:
            predicted_next_week = 0
        
        # Predict topics to master
        weak_topics = await self.get_weak_topics(user_id, 5)
        predicted_topics = [t["topic"] for t in weak_topics if t["accuracy"] > 60]  # Close to mastery
        
        # Predict streak
        streak_info = await self._calculate_streak(user_id)
        predicted_streak = streak_info["current"] + 7  # Assume continue for next week
        
        # Readiness timeline
        readiness_timeline = []
        for weeks in [2, 4, 8, 12]:
            date_val = date.today() + timedelta(weeks=weeks)
            # Simple projection - improve by 5% every 4 weeks
            predicted_readiness = min(100, user_summary["overall_accuracy"] + weeks * 1.25)
            readiness_timeline.append({
                "date": date_val.isoformat(),
                "predicted_readiness": round(predicted_readiness, 2)
            })
        
        # Risk areas
        risk_areas = []
        for topic in weak_topics[:3]:
            if topic["accuracy"] < 40:
                risk_areas.append({
                    "area": topic["topic"],
                    "risk": "high",
                    "reason": f"Low accuracy ({topic['accuracy']}%)"
                })
        
        # Preventive actions
        preventive_actions = [
            "Increase daily practice time",
            "Focus on weak topics identified",
            "Take weekly mock tests"
        ]
        
        return {
            "predicted_accuracy": round(predicted_next_week, 2),
            "predicted_topics_to_master": predicted_topics,
            "predicted_streak": predicted_streak,
            "readiness_timeline": readiness_timeline,
            "risk_areas": risk_areas,
            "recommendations": preventive_actions
        }
    
    async def get_skill_gaps(self, user_id: str, target_role: Optional[str]) -> List[Dict[str, Any]]:
        """Get skill gap analysis"""
        
        # Get user's skills from resume
        resumes = firebase_client.get_data(f"resumes/{user_id}") or {}
        parsed_resumes = []
        
        for resume_id, resume in resumes.items():
            if resume.get("status") in ["parsed", "analyzed"]:
                parsed = firebase_client.get_data(f"resumes_parsed/{user_id}/{resume_id}")
                if parsed:
                    parsed_resumes.append(parsed)
        
        if not parsed_resumes:
            return []
        
        # Use most recent parsed resume
        latest_resume = max(parsed_resumes, key=lambda x: x.get("parsed_at", ""))
        skills = latest_resume.get("parsed_data", {}).get("skills", {})
        
        # Get role requirements
        requirements = await self._get_role_requirements(target_role) if target_role else {}
        
        skill_gaps = []
        for category, skill_list in skills.items():
            for skill in skill_list:
                skill_name = skill.get("name") if isinstance(skill, dict) else skill
                
                # Determine current level
                years = skill.get("years", 0) if isinstance(skill, dict) else 0
                if years >= 5:
                    current_level = "expert"
                elif years >= 3:
                    current_level = "advanced"
                elif years >= 1:
                    current_level = "intermediate"
                else:
                    current_level = "beginner"
                
                # Determine required level for role
                required_level = "intermediate"  # Default
                if requirements:
                    for req_skill in requirements.get("skills", []):
                        if req_skill.get("skill", "").lower() == skill_name.lower():
                            required_level = req_skill.get("level", "intermediate")
                
                # Calculate gap severity
                level_values = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
                current_val = level_values.get(current_level, 1)
                required_val = level_values.get(required_level, 2)
                
                gap = required_val - current_val
                if gap > 0:
                    if gap >= 2:
                        severity = "high"
                        time_to_close = 90
                    elif gap == 1:
                        severity = "medium"
                        time_to_close = 30
                    else:
                        severity = "low"
                        time_to_close = 0
                    
                    skill_gaps.append({
                        "skill_name": skill_name,
                        "current_level": current_level,
                        "required_level": required_level,
                        "gap_severity": severity,
                        "estimated_time_to_close": time_to_close,
                        "resources": await self._get_skill_resources(skill_name)
                    })
        
        return skill_gaps
    
    async def _get_skill_resources(self, skill: str) -> List[Dict[str, str]]:
        """Get learning resources for a skill"""
        # In production, this would fetch from a database
        return [
            {"type": "course", "name": f"Learn {skill}", "url": "#"},
            {"type": "practice", "name": f"{skill} Practice Questions", "url": "#"}
        ]
    
    async def get_recommendations(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        """Get personalized recommendations"""
        
        recommendations = []
        
        # Get weak topics
        weak_topics = await self.get_weak_topics(user_id, 3)
        for topic in weak_topics:
            recommendations.append({
                "type": "topic",
                "title": f"Practice {topic['topic']}",
                "description": f"Your accuracy is only {topic['accuracy']}%. Focus on improving this topic.",
                "priority": topic.get("priority", "medium"),
                "action": f"/practice/topic-wise/{topic['topic']}"
            })
        
        # Check for consistency
        streak_info = await self._calculate_streak(user_id)
        if streak_info["current"] < 3:
            recommendations.append({
                "type": "streak",
                "title": "Build a streak",
                "description": "Practice daily to build momentum and improve retention.",
                "priority": "medium",
                "action": "/practice/quick-quiz"
            })
        
        # Check for mock tests
        sessions = firebase_client.get_data(f"practice_sessions/{user_id}") or {}
        mock_tests = [s for s in sessions.values() if s.get("type") == "mock_test"]
        
        if len(mock_tests) < 2:
            recommendations.append({
                "type": "mock_test",
                "title": "Take a mock test",
                "description": "Mock tests help you prepare for real interview conditions.",
                "priority": "high",
                "action": "/practice/mock-test"
            })
        
        # Company-specific
        user = firebase_client.get_data(f"users/{user_id}")
        if user.get("target_companies"):
            company = user["target_companies"][0]
            readiness = await self._calculate_company_readiness(user_id, company)
            if readiness["overall_score"] < 70:
                recommendations.append({
                    "type": "company",
                    "title": f"Prepare for {company}",
                    "description": f"Your readiness for {company} is {readiness['overall_score']}%. Focus on company-specific questions.",
                    "priority": "high",
                    "action": f"/practice/company-grid/{company}"
                })
        
        return recommendations[:limit]
    
    async def export_analytics(self, user_id: str, format: str, timeframe: TimeFrame) -> Dict[str, Any]:
        """Export analytics data"""
        
        # Gather all analytics data
        data = {
            "user_id": user_id,
            "exported_at": datetime.utcnow().isoformat(),
            "summary": await self.get_summary(user_id),
            "subject_performance": await self.get_subject_performance(user_id),
            "topic_mastery": await self.get_topic_mastery(user_id, None),
            "difficulty_performance": await self.get_difficulty_performance(user_id),
            "time_analysis": await self.get_time_analysis(user_id)
        }
        
        if format == "json":
            # Return JSON data
            return {
                "format": "json",
                "data": data
            }
        elif format == "csv":
            # Generate CSV
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(["Metric", "Value"])
            
            # Write summary
            for key, value in data["summary"].items():
                if key != "user_id":
                    writer.writerow([key, value])
            
            # In production, would create a file and upload to storage
            return {
                "format": "csv",
                "url": "#",
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
        elif format == "pdf":
            # Generate PDF (would use reportlab or similar)
            return {
                "format": "pdf",
                "url": "#",
                "expires_at": (datetime.utcnow() + timedelta(hours=1)).isoformat()
            }
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    async def get_streak_info(self, user_id: str) -> Dict[str, Any]:
        """Get detailed streak information"""
        
        progress = firebase_client.get_data(f"progress/{user_id}") or {}
        
        streak = await self._calculate_streak(user_id)
        
        # Get streak history
        dates = sorted(progress.keys(), reverse=True)
        streak_dates = []
        
        current_streak_dates = []
        for date_str in dates:
            if progress[date_str].get("questions_attempted", 0) > 0:
                current_streak_dates.append(date_str)
            else:
                break
        
        return {
            "current_streak": streak["current"],
            "longest_streak": streak["longest"],
            "streak_dates": current_streak_dates[:streak["current"]],
            "last_active": dates[0] if dates else None
        }
    
    async def _calculate_streak(self, user_id: str) -> Dict[str, int]:
        """Calculate user streak"""
        
        progress = firebase_client.get_data(f"progress/{user_id}") or {}
        
        if not progress:
            return {"current": 0, "longest": 0}
        
        dates = sorted(progress.keys(), reverse=True)
        
        current_streak = 0
        longest_streak = 0
        streak = 0
        last_date = None
        
        for date_str in dates:
            current_date = date.fromisoformat(date_str)
            
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
        today = date.today()
        if dates and date.fromisoformat(dates[0]) == today:
            current_streak = streak
        
        return {
            "current": current_streak,
            "longest": longest_streak
        }
    
    async def _get_active_days(self, user_id: str) -> List[date]:
        """Get list of active days"""
        
        progress = firebase_client.get_data(f"progress/{user_id}") or {}
        
        active_days = []
        for date_str, day_data in progress.items():
            if day_data.get("questions_attempted", 0) > 0:
                active_days.append(date.fromisoformat(date_str))
        
        return active_days
    
    async def get_activity_heatmap(self, user_id: str, year: Optional[int]) -> Dict[str, Any]:
        """Get activity heatmap data for GitHub-style calendar"""
        
        if not year:
            year = date.today().year
        
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        progress = firebase_client.get_data(f"progress/{user_id}") or {}
        
        heatmap = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            day_data = progress.get(date_str, {})
            
            count = day_data.get("questions_attempted", 0)
            
            # Determine intensity (0-4)
            if count == 0:
                intensity = 0
            elif count < 5:
                intensity = 1
            elif count < 10:
                intensity = 2
            elif count < 20:
                intensity = 3
            else:
                intensity = 4
            
            heatmap.append({
                "date": date_str,
                "count": count,
                "intensity": intensity
            })
            
            current_date += timedelta(days=1)
        
        return {
            "year": year,
            "total_active_days": sum(1 for d in heatmap if d["count"] > 0),
            "total_questions": sum(d["count"] for d in heatmap),
            "data": heatmap
        }
    
    async def get_milestones(self, user_id: str) -> List[Dict[str, Any]]:
        """Get achieved milestones"""
        
        summary = await self.get_summary(user_id)
        
        milestones = []
        
        # Question count milestones
        if summary["total_questions"] >= 1000:
            milestones.append({
                "title": "1,000 Questions Club",
                "description": "Successfully completed 1,000 practice questions",
                "achieved_at": "recent",  # Would track actual date
                "icon": "🎯"
            })
        elif summary["total_questions"] >= 500:
            milestones.append({
                "title": "500 Questions",
                "description": "Completed 500 practice questions",
                "achieved_at": "recent",
                "icon": "📊"
            })
        
        # Streak milestones
        if summary["longest_streak"] >= 30:
            milestones.append({
                "title": "30-Day Streak",
                "description": "Practiced for 30 days in a row",
                "achieved_at": "recent",
                "icon": "🔥"
            })
        elif summary["longest_streak"] >= 7:
            milestones.append({
                "title": "7-Day Streak",
                "description": "Practiced for a full week",
                "achieved_at": "recent",
                "icon": "📅"
            })
        
        # Accuracy milestones
        if summary["overall_accuracy"] >= 90:
            milestones.append({
                "title": "Accuracy Master",
                "description": "Achieved 90%+ overall accuracy",
                "achieved_at": "recent",
                "icon": "🎓"
            })
        elif summary["overall_accuracy"] >= 80:
            milestones.append({
                "title": "Accuracy Expert",
                "description": "Achieved 80%+ overall accuracy",
                "achieved_at": "recent",
                "icon": "⭐"
            })
        
        # Time milestones
        if summary["total_practice_time"] >= 10000:  # ~167 hours
            milestones.append({
                "title": "10,000 Minutes",
                "description": "Spent 10,000 minutes practicing",
                "achieved_at": "recent",
                "icon": "⏱️"
            })
        
        return milestones
    
    async def get_dashboard_data(self, user_id: str) -> Dict[str, Any]:
        """Get all dashboard data in one request"""
        
        # Fetch all required data in parallel (in production)
        summary = await self.get_summary(user_id)
        trends = await self.get_trends(user_id, 30)
        subject_performance = await self.get_subject_performance(user_id)
        weak_topics = await self.get_weak_topics(user_id, 5)
        strong_topics = await self.get_strong_topics(user_id, 5)
        streak_info = await self.get_streak_info(user_id)
        recommendations = await self.get_recommendations(user_id, 3)
        
        # Get user info
        user = firebase_client.get_data(f"users/{user_id}")
        
        return {
            "user": {
                "display_name": user.get("display_name"),
                "photo_url": user.get("photo_url"),
                "target_companies": user.get("target_companies", [])
            },
            "summary": summary,
            "trends": trends,
            "subject_performance": subject_performance,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "streak": streak_info,
            "recommendations": recommendations
        }
    
    async def get_platform_stats(self) -> Dict[str, Any]:
        """Get platform-wide statistics (admin)"""
        
        all_users = firebase_client.get_data("users") or {}
        all_questions = firebase_client.get_data("questions") or {}
        
        # Count active users (last 30 days)
        thirty_days_ago = (datetime.utcnow() - timedelta(days=30)).isoformat()
        active_users = 0
        
        for user_id, user in all_users.items():
            last_login = user.get("last_login")
            if last_login and last_login > thirty_days_ago:
                active_users += 1
        
        # Count total attempts
        total_attempts = 0
        total_correct = 0
        
        all_attempts = firebase_client.get_data("attempts") or {}
        for user_id, user_attempts in all_attempts.items():
            total_attempts += len(user_attempts)
            total_correct += sum(1 for a in user_attempts.values() if a.get("is_correct", False))
        
        # Calculate average accuracy
        avg_accuracy = (total_correct / total_attempts * 100) if total_attempts > 0 else 0
        
        # Count premium users
        premium_users = sum(1 for u in all_users.values() if u.get("role") in ["pro", "premium"])
        
        return {
            "total_users": len(all_users),
            "active_users_30d": active_users,
            "total_questions": len(all_questions),
            "total_attempts": total_attempts,
            "average_accuracy": round(avg_accuracy, 2),
            "premium_users": premium_users,
            "free_users": len(all_users) - premium_users,
            "questions_by_subject": await self._count_questions_by_subject(all_questions)
        }
    
    async def _count_questions_by_subject(self, questions: Dict) -> Dict[str, int]:
        """Count questions by subject"""
        
        counts = {}
        for qid, question in questions.items():
            subject = question.get("subject")
            if subject:
                counts[subject] = counts.get(subject, 0) + 1
        
        return counts
    
    async def get_user_growth(self, days: int) -> Dict[str, Any]:
        """Get user growth analytics (admin)"""
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        all_users = firebase_client.get_data("users") or {}
        
        growth = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            
            # Count users created on or before this date
            users_before = sum(
                1 for u in all_users.values()
                if u.get("created_at", "").split("T")[0] <= date_str
            )
            
            growth.append({
                "date": date_str,
                "total_users": users_before
            })
            
            current_date += timedelta(days=1)
        
        return {
            "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
            "data": growth,
            "total_growth": len(all_users) - growth[0]["total_users"] if growth else 0
        }
    
    async def _get_role_requirements(self, role: str) -> Dict[str, Any]:
        """Get requirements for a role"""
        # In production, this would come from a database
        requirements_db = {
            "data_scientist": {
                "skills": [
                    {"skill": "Python", "level": "advanced"},
                    {"skill": "SQL", "level": "intermediate"},
                    {"skill": "Machine Learning", "level": "advanced"},
                    {"skill": "Statistics", "level": "advanced"}
                ],
                "min_experience": 3
            },
            "ml_engineer": {
                "skills": [
                    {"skill": "Python", "level": "advanced"},
                    {"skill": "TensorFlow", "level": "advanced"},
                    {"skill": "PyTorch", "level": "intermediate"},
                    {"skill": "Docker", "level": "intermediate"}
                ],
                "min_experience": 2
            }
        }
        
        return requirements_db.get(role.replace(" ", "_").lower(), {})
