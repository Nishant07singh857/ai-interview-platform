"""
Company Schemas - Pydantic models for company-related API requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Response Schemas
class CompanyResponse(BaseModel):
    """Company response"""
    company_id: str
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None
    difficulty: str
    question_count: int
    topics: List[str] = []
    roles: List[str] = []
    
    class Config:
        from_attributes = True

class CompanyDetailResponse(CompanyResponse):
    """Detailed company response"""
    interview_process: List[str] = []
    interview_count: int = 0
    average_rating: float = 0.0
    preparation_tips: List[str] = []
    recent_experiences: List[Dict[str, Any]] = []
    
    class Config:
        from_attributes = True

class CompanyQuestionResponse(BaseModel):
    """Company question response"""
    question_id: str
    title: str
    description: str
    difficulty: str
    topic: str
    times_used: int
    correct_rate: float
    
    class Config:
        from_attributes = True

class CompanyStatsResponse(BaseModel):
    """Company statistics response"""
    company_id: str
    company_name: str
    total_questions: int
    user_attempts: int
    user_correct: int
    user_accuracy: float
    global_attempts: int
    global_accuracy: float
    popular_roles: List[str]
    difficulty_breakdown: Dict[str, int]
    topic_breakdown: Dict[str, int]
    
    class Config:
        from_attributes = True

class InterviewExperienceResponse(BaseModel):
    """Interview experience response"""
    experience_id: str
    user_name: str
    user_role: Optional[str] = None
    company: str
    role: str
    date: str
    rounds: List[Dict[str, Any]]
    difficulty: str
    offer_received: bool
    rating: Optional[int] = None
    tips: Optional[str] = None
    helpful_count: int
    
    class Config:
        from_attributes = True

class CompanyReadinessResponse(BaseModel):
    """Company readiness response"""
    company: str
    overall_readiness: float
    readiness_level: str
    questions_attempted: int
    total_questions: int
    topic_readiness: Dict[str, float]
    recommended_focus: List[str]
    
    class Config:
        from_attributes = True