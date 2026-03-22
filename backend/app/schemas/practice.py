"""
Practice Schemas - Pydantic models for practice-related API requests/responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.practice import PracticeType, SessionStatus

# Request Schemas
class QuickQuizRequest(BaseModel):
    """Quick quiz request"""
    total_questions: int = Field(5, ge=1, le=20)
    time_limit: int = Field(5, ge=1, le=30)
    subjects: Optional[List[str]] = None
    difficulties: Optional[List[str]] = None
    shuffle: bool = True

class TopicPracticeRequest(BaseModel):
    """Topic-wise practice request"""
    subject: str
    topic: str
    subtopics: Optional[List[str]] = None
    total_questions: int = Field(10, ge=1, le=50)
    time_limit: int = Field(10, ge=1, le=60)
    difficulty: Optional[str] = None
    include_explanations: bool = True
    shuffle: bool = True

class MockTestRequest(BaseModel):
    """Mock test request"""
    subject: str
    title: Optional[str] = None
    total_questions: int = Field(30, ge=10, le=100)
    time_limit: int = Field(30, ge=15, le=180)
    passing_score: int = Field(70, ge=0, le=100)
    difficulty_distribution: Optional[Dict[str, int]] = None
    topics: Optional[List[str]] = None

class CompanyGridRequest(BaseModel):
    """Company grid practice request"""
    company: str
    role: Optional[str] = None
    total_questions: int = Field(20, ge=5, le=50)
    time_limit: int = Field(25, ge=10, le=120)
    difficulty_focus: Optional[str] = None

class AnswerSubmission(BaseModel):
    """Answer submission for a question"""
    session_id: str
    question_id: str
    answer: Any
    time_taken_seconds: int = Field(..., ge=1, le=3600)
    hints_used: int = Field(0, ge=0)
    skipped: bool = False

class SessionAction(BaseModel):
    """Session action (pause, resume, end)"""
    session_id: str
    action: str  # pause, resume, end

class SessionFeedback(BaseModel):
    """Session feedback"""
    session_id: str
    rating: int = Field(..., ge=1, le=5)
    feedback: Optional[str] = Field(None, max_length=500)

# Response Schemas
class PracticeSessionResponse(BaseModel):
    """Practice session response"""
    session_id: str
    type: PracticeType
    status: SessionStatus
    title: Optional[str] = None
    description: Optional[str] = None
    total_questions: int
    time_limit: Optional[int] = None
    passing_score: Optional[int] = None  # 🔴 Add default None
    subject: Optional[str] = None
    topic: Optional[str] = None
    company: Optional[str] = None  # 🔴 Add default None
    
    # Current question
    current_question_index: int = 0
    current_question: Optional[Dict[str, Any]] = None
    
    # Progress
    questions_answered: int = 0
    questions_remaining: Optional[int] = None  # 🔴 Add default None
    correct_answers: int = 0
    incorrect_answers: int = 0
    time_elapsed: int = 0  # seconds
    time_remaining: Optional[int] = None  # seconds
    
    # Timestamps
    started_at: Optional[datetime] = None
    created_at: datetime
    
    # 🔴 Add validator to ensure all fields have values
    @validator('questions_remaining', always=True)
    def set_questions_remaining(cls, v, values):
        if v is None and 'total_questions' in values and 'questions_answered' in values:
            return values['total_questions'] - values['questions_answered']
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        # 🔴 Allow extra fields from backend
        extra = "allow"

class PracticeSessionDetailResponse(PracticeSessionResponse):
    """Detailed practice session response"""
    questions: List[Dict[str, Any]] = []
    question_status: Dict[str, Dict[str, Any]] = {}
    time_per_question: List[int] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        extra = "allow"

class PracticeResultResponse(BaseModel):
    """Practice session results response"""
    session_id: str
    type: PracticeType
    score: float = 0.0
    accuracy: float = 0.0
    total_time_spent: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    skipped_questions: int = 0
    
    # Detailed performance
    subject_wise: Dict[str, Dict[str, Any]] = {}
    topic_wise: Dict[str, Dict[str, Any]] = {}
    difficulty_wise: Dict[str, Dict[str, Any]] = {}
    
    # Analysis
    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendations: List[str] = []
    
    # Comparison
    percentile: Optional[float] = None
    average_score: Optional[float] = None
    
    completed_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        extra = "allow"

class PracticeHistoryResponse(BaseModel):
    """Practice history response"""
    total_sessions: int = 0
    total_time_spent: int = 0  # minutes
    average_score: float = 0.0
    average_accuracy: float = 0.0
    recent_sessions: List[Dict[str, Any]] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        extra = "allow"

class CompanyGridInfo(BaseModel):
    """Company grid information"""
    company: str
    description: Optional[str] = None
    total_questions: int = 0
    topics: List[str] = []
    difficulty_breakdown: Dict[str, int] = {}
    average_company_score: float = 0.0
    user_score: Optional[float] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
        extra = "allow"