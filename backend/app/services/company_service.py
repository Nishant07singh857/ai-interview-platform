"""
Company Service - Complete company-specific preparation logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from uuid import uuid4

from app.core.database import firebase_client
from app.core.cache import cache_manager
from app.models.company import Company, CompanyStats, InterviewExperience
from app.services.question_service import QuestionService
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)

class CompanyService:
    """Company service with complete business logic"""
    
    def __init__(self):
        self.question_service = QuestionService()
        self.analytics_service = AnalyticsService()
    
    async def get_all_companies(self) -> List[Dict[str, Any]]:
        """Get all companies with preparation materials"""
        
        # Try cache first
        cached = await cache_manager.get("all_companies")
        if cached:
            return cached
        
        companies = firebase_client.get_data("companies") or {}
        
        result = []
        for company_id, company in companies.items():
            # Get question count
            questions = firebase_client.query_firestore(
                "questions",
                "companies",
                "array_contains",
                company.get("name")
            )
            
            result.append({
                "company_id": company_id,
                "name": company.get("name"),
                "description": company.get("description"),
                "logo": company.get("logo"),
                "difficulty": company.get("difficulty", "hard"),
                "question_count": len(questions),
                "topics": company.get("topics", []),
                "roles": company.get("roles", []),
            })
        
        # Cache for 1 hour
        await cache_manager.set("all_companies", result, ttl=3600)
        
        return result
    
    async def get_company(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed company information"""
        
        # Try cache
        cached = await cache_manager.get(f"company:{company_id}")
        if cached:
            return cached
        
        company = firebase_client.get_data(f"companies/{company_id}")
        
        if not company:
            return None
        
        # Get interview experiences
        experiences = firebase_client.query_firestore(
            "interview_experiences",
            "company_id",
            "==",
            company_id
        )
        
        # Get preparation tips
        tips = firebase_client.get_data(f"company_tips/{company_id}") or {}
        
        result = {
            **company,
            "company_id": company_id,
            "interview_count": len(experiences),
            "average_rating": self._calculate_average_rating(experiences),
            "preparation_tips": tips.get("tips", []),
            "recent_experiences": experiences[:5],
        }
        
        # Cache for 1 hour
        await cache_manager.set(f"company:{company_id}", result, ttl=3600)
        
        return result
    
    def _calculate_average_rating(self, experiences: List[Dict]) -> float:
        """Calculate average rating from experiences"""
        if not experiences:
            return 0.0
        
        ratings = [exp.get("rating", 0) for exp in experiences if exp.get("rating")]
        return sum(ratings) / len(ratings) if ratings else 0.0
    
    async def get_company_questions(
        self,
        company_id: str,
        role: Optional[str],
        difficulty: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get questions commonly asked at a company"""
        
        company = await self.get_company(company_id)
        if not company:
            return []
        
        # Get questions tagged with this company
        questions = firebase_client.query_firestore(
            "questions",
            "companies",
            "array_contains",
            company.get("name")
        )
        
        # Apply filters
        filtered = []
        for q in questions:
            if role and role not in q.get("roles", []):
                continue
            if difficulty and q.get("difficulty") != difficulty:
                continue
            filtered.append(q)
        
        # Sort by relevance (times used, recency)
        filtered.sort(key=lambda x: x.get("times_used", 0), reverse=True)
        
        return filtered[:limit]
    
    async def get_company_stats(self, company_id: str, user_id: str) -> Dict[str, Any]:
        """Get company statistics including user's performance"""
        
        company = await self.get_company(company_id)
        if not company:
            return {}
        
        # Get all attempts for this company's questions
        company_questions = await self.get_company_questions(company_id, None, None, 1000)
        question_ids = [q["question_id"] for q in company_questions]
        
        # Get user's attempts
        user_attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        company_attempts = []
        for attempt_id, attempt in user_attempts.items():
            if attempt.get("question_id") in question_ids:
                company_attempts.append(attempt)
        
        # Calculate stats
        total_attempts = len(company_attempts)
        correct_attempts = sum(1 for a in company_attempts if a.get("is_correct", False))
        
        # Get global stats
        all_attempts = []
        for qid in question_ids:
            q_attempts = firebase_client.get_data(f"question_attempts/{qid}") or {}
            all_attempts.extend(q_attempts.values())
        
        global_correct = sum(1 for a in all_attempts if a.get("is_correct", False))
        global_total = len(all_attempts)
        
        return CompanyStats(
            company_id=company_id,
            company_name=company.get("name"),
            total_questions=len(company_questions),
            user_attempts=total_attempts,
            user_correct=correct_attempts,
            user_accuracy=round(correct_attempts / total_attempts * 100, 2) if total_attempts > 0 else 0,
            global_attempts=global_total,
            global_accuracy=round(global_correct / global_total * 100, 2) if global_total > 0 else 0,
            popular_roles=company.get("roles", []),
            difficulty_breakdown=self._get_difficulty_breakdown(company_questions),
            topic_breakdown=self._get_topic_breakdown(company_questions),
        ).dict()
    
    def _get_difficulty_breakdown(self, questions: List[Dict]) -> Dict[str, int]:
        """Get breakdown of questions by difficulty"""
        breakdown = {"easy": 0, "medium": 0, "hard": 0, "expert": 0}
        for q in questions:
            difficulty = q.get("difficulty", "medium")
            breakdown[difficulty] = breakdown.get(difficulty, 0) + 1
        return breakdown
    
    def _get_topic_breakdown(self, questions: List[Dict]) -> Dict[str, int]:
        """Get breakdown of questions by topic"""
        breakdown = {}
        for q in questions:
            topic = q.get("topic", "other")
            breakdown[topic] = breakdown.get(topic, 0) + 1
        return breakdown
    
    async def get_interview_experiences(
        self,
        company_id: str,
        role: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get interview experiences shared by users"""
        
        experiences = firebase_client.query_firestore(
            "interview_experiences",
            "company_id",
            "==",
            company_id
        )
        
        if role:
            experiences = [e for e in experiences if e.get("role") == role]
        
        # Sort by date (newest first)
        experiences.sort(key=lambda x: x.get("date", ""), reverse=True)
        
        result = []
        for exp in experiences[:limit]:
            # Get user details
            user = firebase_client.get_data(f"users/{exp.get('user_id')}")
            
            result.append({
                "experience_id": exp.get("experience_id"),
                "user_name": user.get("display_name") if user else "Anonymous",
                "user_role": user.get("current_role") if user else None,
                "company": exp.get("company"),
                "role": exp.get("role"),
                "date": exp.get("date"),
                "rounds": exp.get("rounds", []),
                "difficulty": exp.get("difficulty"),
                "offer_received": exp.get("offer_received", False),
                "rating": exp.get("rating"),
                "tips": exp.get("tips"),
                "helpful_count": exp.get("helpful_count", 0),
            })
        
        return result
    
    async def share_experience(self, user_id: str, experience_data: Dict) -> Dict[str, Any]:
        """Share interview experience"""
        
        experience_id = str(uuid4())
        
        experience = {
            "experience_id": experience_id,
            "user_id": user_id,
            "company": experience_data.get("company"),
            "company_id": experience_data.get("company_id"),
            "role": experience_data.get("role"),
            "date": experience_data.get("date", datetime.utcnow().isoformat()),
            "rounds": experience_data.get("rounds", []),
            "difficulty": experience_data.get("difficulty"),
            "questions_asked": experience_data.get("questions_asked", []),
            "offer_received": experience_data.get("offer_received", False),
            "salary": experience_data.get("salary"),
            "rating": experience_data.get("rating"),
            "tips": experience_data.get("tips"),
            "helpful_count": 0,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        firebase_client.set_data(
            f"interview_experiences/{user_id}/{experience_id}",
            experience
        )
        
        return experience
    
    async def calculate_readiness(self, user_id: str, company_id: str) -> Dict[str, Any]:
        """Calculate user's readiness for a specific company"""
        
        company = await self.get_company(company_id)
        if not company:
            return {}
        
        # Get company questions
        questions = await self.get_company_questions(company_id, None, None, 500)
        
        # Get user's performance on these questions
        user_attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
        
        question_performance = {}
        for q in questions:
            qid = q["question_id"]
            attempts = [a for a in user_attempts.values() if a.get("question_id") == qid]
            
            if attempts:
                correct = sum(1 for a in attempts if a.get("is_correct", False))
                total = len(attempts)
                question_performance[qid] = {
                    "accuracy": round(correct / total * 100, 2),
                    "attempts": total,
                }
        
        # Calculate overall readiness
        if not question_performance:
            overall = 0
        else:
            overall = sum(p["accuracy"] for p in question_performance.values()) / len(question_performance)
        
        # Get topic-wise readiness
        topic_readiness = {}
        for q in questions:
            topic = q.get("topic")
            if topic not in topic_readiness:
                topic_readiness[topic] = {"total": 0, "correct": 0}
            
            qid = q["question_id"]
            if qid in question_performance:
                # Estimate correctness based on accuracy
                attempts = [a for a in user_attempts.values() if a.get("question_id") == qid]
                correct = sum(1 for a in attempts if a.get("is_correct", False))
                topic_readiness[topic]["total"] += len(attempts)
                topic_readiness[topic]["correct"] += correct
        
        # Calculate topic scores
        topic_scores = {}
        for topic, data in topic_readiness.items():
            if data["total"] > 0:
                topic_scores[topic] = round(data["correct"] / data["total"] * 100, 2)
            else:
                topic_scores[topic] = 0
        
        # Determine readiness level
        if overall >= 80:
            level = "highly_ready"
        elif overall >= 60:
            level = "ready"
        elif overall >= 40:
            level = "almost_ready"
        else:
            level = "not_ready"
        
        return {
            "company": company.get("name"),
            "overall_readiness": round(overall, 2),
            "readiness_level": level,
            "questions_attempted": len(question_performance),
            "total_questions": len(questions),
            "topic_readiness": topic_scores,
            "recommended_focus": self._get_recommended_focus(topic_scores, company),
        }
    
    def _get_recommended_focus(self, topic_scores: Dict[str, float], company: Dict) -> List[str]:
        """Get recommended topics to focus on"""
        company_topics = set(company.get("topics", []))
        weak_topics = [
            topic for topic, score in topic_scores.items()
            if score < 60 and topic in company_topics
        ]
        return sorted(weak_topics, key=lambda t: topic_scores[t])[:5]
    
    async def get_preparation_tips(self, company_id: str) -> List[str]:
        """Get company-specific preparation tips"""
        
        tips = firebase_client.get_data(f"company_tips/{company_id}")
        if tips:
            return tips.get("tips", [])
        
        # Default tips based on company
        company = await self.get_company(company_id)
        if not company:
            return []
        
        return [
            f"Research {company.get('name')}'s products and culture",
            f"Practice {company.get('difficulty')}-level questions",
            "Review system design principles",
            "Prepare for behavioral questions",
            "Practice coding on a whiteboard",
        ]
    
    async def track_interest(self, user_id: str, company_id: str):
        """Track that user is interested in this company"""
        
        user = firebase_client.get_data(f"users/{user_id}")
        if user:
            targets = user.get("target_companies", [])
            company = await self.get_company(company_id)
            if company and company.get("name") not in targets:
                targets.append(company.get("name"))
                firebase_client.update_data(f"users/{user_id}", {
                    "target_companies": targets
                })
    
    async def create_company(self, company_data: Dict, created_by: str) -> Dict:
        """Create a new company (admin)"""
        
        company_id = str(uuid4())
        
        company = {
            "company_id": company_id,
            "name": company_data["name"],
            "description": company_data.get("description", ""),
            "logo": company_data.get("logo"),
            "difficulty": company_data.get("difficulty", "hard"),
            "topics": company_data.get("topics", []),
            "roles": company_data.get("roles", []),
            "interview_process": company_data.get("interview_process", []),
            "created_by": created_by,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        firebase_client.set_data(f"companies/{company_id}", company)
        
        return company
    
    async def update_company(self, company_id: str, company_data: Dict) -> Dict:
        """Update company information (admin)"""
        
        company = firebase_client.get_data(f"companies/{company_id}")
        if not company:
            raise ValueError("Company not found")
        
        company.update(company_data)
        company["updated_at"] = datetime.utcnow().isoformat()
        
        firebase_client.set_data(f"companies/{company_id}", company)
        
        # Clear cache
        await cache_manager.delete(f"company:{company_id}")
        await cache_manager.delete("all_companies")
        
        return company
    
    async def delete_company(self, company_id: str):
        """Delete a company (admin)"""
        
        firebase_client.delete_data(f"companies/{company_id}")
        
        # Clear cache
        await cache_manager.delete(f"company:{company_id}")
        await cache_manager.delete("all_companies")