"""
Company Models - Company and interview experience models
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class Company(BaseModel):
    """Company model"""
    company_id: str
    name: str
    description: Optional[str] = None
    logo: Optional[str] = None
    difficulty: str = "hard"  # easy, medium, hard, expert
    topics: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)
    interview_process: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CompanyStats(BaseModel):
    """Company statistics model"""
    company_id: str
    company_name: str
    total_questions: int = 0
    user_attempts: int = 0
    user_correct: int = 0
    user_accuracy: float = 0.0
    global_attempts: int = 0
    global_accuracy: float = 0.0
    popular_roles: List[str] = Field(default_factory=list)
    difficulty_breakdown: Dict[str, int] = Field(default_factory=dict)
    topic_breakdown: Dict[str, int] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InterviewRound(BaseModel):
    """Interview round model"""
    round_id: str
    type: str  # phone, technical, system_design, behavioral, etc.
    duration_minutes: Optional[int] = None
    questions: List[str] = Field(default_factory=list)
    difficulty: Optional[str] = None
    feedback: Optional[str] = None

class InterviewExperience(BaseModel):
    """Interview experience model"""
    experience_id: str
    user_id: str
    company_id: str
    company: str
    role: str
    date: str
    rounds: List[InterviewRound] = Field(default_factory=list)
    difficulty: str
    questions_asked: List[str] = Field(default_factory=list)
    offer_received: bool = False
    salary: Optional[Dict[str, Any]] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    tips: Optional[str] = None
    helpful_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CompanyTip(BaseModel):
    """Company preparation tip"""
    tip_id: str
    company_id: str
    tip: str
    category: str  # general, technical, behavioral, etc.
    created_by: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    helpful_count: int = 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }