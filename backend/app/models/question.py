"""
Question Models - Complete implementation for all question types
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    """Question difficulty levels"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class SubjectArea(str, Enum):
    """Main subject areas"""
    ML = "machine_learning"
    DL = "deep_learning"
    DS = "data_science"
    DA = "data_analysis"
    AI = "artificial_intelligence"

class QuestionType(str, Enum):
    """Types of questions"""
    MCQ = "mcq"
    CODE = "code"
    THEORY = "theory"
    SYSTEM_DESIGN = "system_design"
    CASE_STUDY = "case_study"
    MULTIPLE_SELECT = "multiple_select"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"
    MATCHING = "matching"

class QuestionStatus(str, Enum):
    """Question status"""
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"

class Topic(BaseModel):
    """Topic model"""
    topic_id: str
    subject: SubjectArea
    name: str
    description: Optional[str] = None
    parent_topic: Optional[str] = None
    subtopics: List[str] = Field(default_factory=list)
    difficulty: DifficultyLevel
    prerequisites: List[str] = Field(default_factory=list)
    estimated_time: int = 10  # minutes
    tags: List[str] = Field(default_factory=list)
    question_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Question(BaseModel):
    """Main Question model"""
    question_id: str
    subject: SubjectArea
    topic: str
    subtopic: Optional[str] = None
    type: QuestionType
    difficulty: DifficultyLevel
    status: QuestionStatus = QuestionStatus.APPROVED
    
    # Content
    title: str
    description: str
    instructions: Optional[str] = None
    
    # For MCQ
    options: Optional[List[Dict[str, Any]]] = None  # [{"id": "A", "text": "...", "is_correct": false}]
    
    # For multiple correct
    correct_answers: Optional[List[str]] = None  # List of correct option IDs
    
    # For code questions
    code_snippet: Optional[str] = None
    programming_language: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None  # [{"input": "...", "output": "...", "hidden": false}]
    time_limit: Optional[int] = None  # milliseconds
    memory_limit: Optional[int] = None  # MB
    
    # For theory
    expected_answer: Optional[str] = None
    key_points: Optional[List[str]] = None
    word_limit: Optional[int] = None
    
    # For system design
    requirements: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    expected_components: Optional[List[str]] = None
    diagrams_required: bool = False
    
    # For case study
    case_data: Optional[Dict[str, Any]] = None
    datasets: Optional[List[str]] = None
    analysis_required: Optional[List[str]] = None
    
    # Explanation
    explanation: str
    detailed_explanation: Optional[str] = None
    hints: List[str] = Field(default_factory=list)
    common_mistakes: Optional[List[str]] = None
    
    # Resources
    references: List[Dict[str, str]] = Field(default_factory=list)  # [{"title": "...", "url": "..."}]
    videos: List[Dict[str, str]] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    companies: List[str] = Field(default_factory=list)  # Companies that ask this
    roles: List[str] = Field(default_factory=list)  # Target roles
    
    # Statistics
    times_used: int = 0
    times_correct: int = 0
    times_incorrect: int = 0
    correct_rate: float = 0.0
    avg_time_seconds: int = 0
    difficulty_rating: float = 0.0  # User-rated difficulty
    
    # Authorship
    created_by: str
    created_at: datetime
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    # Versioning
    version: int = 1
    previous_versions: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @validator('options')
    def validate_mcq_options(cls, v, values):
        if values.get('type') == QuestionType.MCQ:
            if not v or len(v) < 2:
                raise ValueError('MCQ must have at least 2 options')
            correct_count = sum(1 for opt in v if opt.get('is_correct', False))
            if correct_count != 1:
                raise ValueError('MCQ must have exactly 1 correct answer')
        return v
    
    @validator('correct_answers')
    def validate_multiple_select(cls, v, values):
        if values.get('type') == QuestionType.MULTIPLE_SELECT:
            if not v or len(v) < 1:
                raise ValueError('Multiple select must have at least 1 correct answer')
        return v

class QuestionAttempt(BaseModel):
    """Record of a question attempt by user"""
    attempt_id: str
    user_id: str
    question_id: str
    session_id: Optional[str] = None
    
    # Answer
    answer: Any  # Could be option ID, code, text, etc.
    is_correct: bool
    time_taken_seconds: int
    hints_used: int = 0
    
    # For code questions
    code_submitted: Optional[str] = None
    test_results: Optional[List[Dict[str, Any]]] = None
    compilation_error: Optional[str] = None
    runtime_error: Optional[str] = None
    
    # Feedback
    user_difficulty_rating: Optional[int] = None  # 1-5
    user_feedback: Optional[str] = None
    
    # Metadata
    attempted_at: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class QuestionSet(BaseModel):
    """Collection of questions (for practice sessions, mock tests)"""
    set_id: str
    name: str
    description: Optional[str] = None
    type: str  # "practice", "mock_test", "custom", "company_specific"
    
    # Content
    questions: List[str]  # List of question IDs
    total_questions: int
    subjects: List[SubjectArea] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    difficulty_range: Dict[str, int] = Field(default_factory=lambda: {
        "easy": 0,
        "medium": 0,
        "hard": 0,
        "expert": 0
    })
    
    # Settings
    time_limit: Optional[int] = None  # minutes
    shuffle_questions: bool = True
    shuffle_options: bool = True
    show_answers: bool = True
    show_explanations: bool = True
    allow_retry: bool = False
    passing_score: Optional[int] = None  # percentage
    
    # Company specific
    company: Optional[str] = None
    role: Optional[str] = None
    
    # Metadata
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    times_used: int = 0
    average_score: float = 0.0
    tags: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PracticeSession(BaseModel):
    """Practice session tracking"""
    session_id: str
    user_id: str
    set_id: Optional[str] = None
    
    # Session info
    start_time: datetime
    end_time: Optional[datetime] = None
    time_spent: Optional[int] = None  # seconds
    
    # Progress
    questions_answered: int = 0
    total_questions: int
    correct_answers: int = 0
    incorrect_answers: int = 0
    skipped_questions: int = 0
    
    # Results
    score: Optional[float] = None
    accuracy: Optional[float] = None
    
    # Questions status
    questions_status: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    # {
    #   "question_id": {
    #     "status": "pending/answered/skipped",
    #     "answer": ...,
    #     "is_correct": true/false,
    #     "time_taken": 45
    #   }
    # }
    
    # Metadata
    session_type: str  # "quick_quiz", "topic_practice", "mock_test", "company_grid"
    completed: bool = False
    abandoned: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }