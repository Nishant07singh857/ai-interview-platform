"""
Practice Models - Complete implementation for practice sessions, quizzes and tests
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class PracticeType(str, Enum):
    """Types of practice sessions"""
    QUICK_QUIZ = "quick_quiz"
    TOPIC_WISE = "topic_wise"
    MOCK_TEST = "mock_test"
    COMPANY_GRID = "company_grid"
    CUSTOM = "custom"

class SessionStatus(str, Enum):
    """Session status"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    TIMED_OUT = "timed_out"
    ABANDONED = "abandoned"

class DifficultyDistribution(BaseModel):
    """Difficulty distribution for tests"""
    easy: int = 0
    medium: int = 0
    hard: int = 0
    expert: int = 0

class PracticeSession(BaseModel):
    """Main practice session model"""
    session_id: str
    user_id: str
    type: PracticeType
    status: SessionStatus = SessionStatus.NOT_STARTED
    
    # Configuration
    title: Optional[str] = None
    description: Optional[str] = None
    total_questions: int
    time_limit: Optional[int] = None  # minutes
    passing_score: Optional[int] = None  # percentage
    
    # Content
    subject: Optional[str] = None
    topic: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    question_ids: List[str] = Field(default_factory=list)
    
    # Questions in session with their status
    questions: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    # {
    #   "question_id": {
    #     "order": 1,
    #     "status": "pending/answered/skipped",
    #     "answer": None,
    #     "is_correct": None,
    #     "time_taken": None,
    #     "hints_used": 0
    #   }
    # }
    
    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    
    # Progress
    current_question_index: int = 0
    questions_answered: int = 0
    questions_skipped: int = 0
    correct_answers: int = 0
    incorrect_answers: int = 0
    
    # Results
    score: Optional[float] = None  # percentage
    accuracy: Optional[float] = None
    total_time_spent: Optional[int] = None  # seconds
    time_per_question: Optional[List[int]] = Field(default_factory=list)
    
    # Feedback
    feedback: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class QuizConfig(BaseModel):
    """Configuration for quick quiz"""
    type: PracticeType = PracticeType.QUICK_QUIZ
    total_questions: int = 5
    time_limit: int = 5  # minutes
    subjects: List[str] = Field(default_factory=list)
    difficulties: List[str] = Field(default_factory=list)
    shuffle: bool = True

class TopicPracticeConfig(BaseModel):
    """Configuration for topic-wise practice"""
    type: PracticeType = PracticeType.TOPIC_WISE
    subject: str
    topic: str
    subtopics: Optional[List[str]] = None
    total_questions: int = 10
    time_limit: int = 10  # minutes
    difficulty: Optional[str] = None
    include_explanations: bool = True
    shuffle: bool = True

class MockTestConfig(BaseModel):
    """Configuration for mock tests"""
    type: PracticeType = PracticeType.MOCK_TEST
    subject: str
    title: str
    description: Optional[str] = None
    total_questions: int = 30
    time_limit: int = 30  # minutes
    passing_score: int = 70  # percentage
    difficulty_distribution: DifficultyDistribution = Field(default_factory=DifficultyDistribution)
    topics: List[str] = Field(default_factory=list)
    include_section_wise_scoring: bool = True
    show_results_immediately: bool = True

class CompanyGridConfig(BaseModel):
    """Configuration for company-specific practice"""
    type: PracticeType = PracticeType.COMPANY_GRID
    company: str
    role: Optional[str] = None
    total_questions: int = 20
    time_limit: int = 25  # minutes
    difficulty_focus: Optional[str] = None
    include_recent_questions: bool = True
    include_company_specific_topics: bool = True

class PracticeResult(BaseModel):
    """Practice session results"""
    session_id: str
    user_id: str
    type: PracticeType
    score: float
    accuracy: float
    total_time_spent: int
    correct_answers: int
    incorrect_answers: int
    skipped_questions: int
    subject_wise_performance: Dict[str, Dict[str, Any]]
    topic_wise_performance: Dict[str, Dict[str, Any]]
    difficulty_wise_performance: Dict[str, Dict[str, Any]]
    time_distribution: List[int]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    percentile: Optional[float] = None
    rank: Optional[int] = None
    created_at: datetime

class PracticeHistory(BaseModel):
    """Practice history summary"""
    session_id: str
    type: PracticeType
    title: str
    subject: Optional[str]
    topic: Optional[str]
    company: Optional[str]
    score: float
    accuracy: float
    total_questions: int
    correct_answers: int
    time_spent: int
    completed_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }