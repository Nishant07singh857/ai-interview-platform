"""
Question Schemas - Pydantic models for question-related API requests/responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

from app.models.question import (
    DifficultyLevel, SubjectArea, QuestionType, QuestionStatus
)

# Request Schemas
class QuestionCreate(BaseModel):
    """Question creation request"""
    subject: SubjectArea
    topic: str
    subtopic: Optional[str] = None
    type: QuestionType
    difficulty: DifficultyLevel
    
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=10)
    instructions: Optional[str] = None
    
    # For MCQ
    options: Optional[List[Dict[str, Any]]] = None
    
    # For multiple correct
    correct_answers: Optional[List[str]] = None
    
    # For code questions
    code_snippet: Optional[str] = None
    programming_language: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None
    
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
    explanation: str = Field(..., min_length=20)
    detailed_explanation: Optional[str] = None
    hints: List[str] = Field(default_factory=list)
    common_mistakes: Optional[List[str]] = None
    
    # Resources
    references: List[Dict[str, str]] = Field(default_factory=list)
    videos: List[Dict[str, str]] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    
    # Metadata
    tags: List[str] = Field(default_factory=list)
    companies: List[str] = Field(default_factory=list)
    roles: List[str] = Field(default_factory=list)

class QuestionUpdate(BaseModel):
    """Question update request"""
    subject: Optional[SubjectArea] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    type: Optional[QuestionType] = None
    difficulty: Optional[DifficultyLevel] = None
    status: Optional[QuestionStatus] = None
    
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    description: Optional[str] = Field(None, min_length=10)
    instructions: Optional[str] = None
    
    options: Optional[List[Dict[str, Any]]] = None
    correct_answers: Optional[List[str]] = None
    
    code_snippet: Optional[str] = None
    programming_language: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None
    
    expected_answer: Optional[str] = None
    key_points: Optional[List[str]] = None
    word_limit: Optional[int] = None
    
    requirements: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    expected_components: Optional[List[str]] = None
    diagrams_required: Optional[bool] = None
    
    case_data: Optional[Dict[str, Any]] = None
    datasets: Optional[List[str]] = None
    analysis_required: Optional[List[str]] = None
    
    explanation: Optional[str] = Field(None, min_length=20)
    detailed_explanation: Optional[str] = None
    hints: Optional[List[str]] = None
    common_mistakes: Optional[List[str]] = None
    
    references: Optional[List[Dict[str, str]]] = None
    videos: Optional[List[Dict[str, str]]] = None
    images: Optional[List[str]] = None
    
    tags: Optional[List[str]] = None
    companies: Optional[List[str]] = None
    roles: Optional[List[str]] = None

class QuestionSearch(BaseModel):
    """Question search parameters"""
    subject: Optional[SubjectArea] = None
    topic: Optional[str] = None
    subtopic: Optional[str] = None
    type: Optional[QuestionType] = None
    difficulty: Optional[DifficultyLevel] = None
    status: Optional[QuestionStatus] = None
    tags: Optional[List[str]] = None
    companies: Optional[List[str]] = None
    roles: Optional[List[str]] = None
    search_text: Optional[str] = None
    limit: int = 20
    offset: int = 0
    sort_by: str = "created_at"
    sort_order: str = "desc"

class QuestionAttemptCreate(BaseModel):
    """Question attempt submission"""
    question_id: str
    answer: Any
    time_taken_seconds: int = Field(..., ge=1, le=3600)
    hints_used: int = Field(0, ge=0)
    
    # For code questions
    code_submitted: Optional[str] = None
    
    # Feedback
    user_difficulty_rating: Optional[int] = Field(None, ge=1, le=5)
    user_feedback: Optional[str] = Field(None, max_length=500)

# Response Schemas
class QuestionResponse(BaseModel):
    """Question response (without answers)"""
    question_id: str
    subject: SubjectArea
    topic: str
    subtopic: Optional[str]
    type: QuestionType
    difficulty: DifficultyLevel
    status: QuestionStatus
    
    title: str
    description: str
    instructions: Optional[str]
    
    # For MCQ - without correct answers
    options: Optional[List[Dict[str, Any]]]  # is_correct field removed
    
    # For multiple select - without correct answers
    # Options are included without is_correct
    
    # For code questions
    code_snippet: Optional[str]
    programming_language: Optional[str]
    time_limit: Optional[int]
    memory_limit: Optional[int]
    
    # For theory
    word_limit: Optional[int]
    
    # For system design
    requirements: Optional[List[str]]
    constraints: Optional[List[str]]
    diagrams_required: bool
    
    # For case study
    case_data: Optional[Dict[str, Any]]
    datasets: Optional[List[str]]
    
    # Hints (first hint only)
    hints: List[str]
    
    # Resources
    references: List[Dict[str, str]]
    videos: List[Dict[str, str]]
    images: List[str]
    
    # Metadata
    tags: List[str]
    companies: List[str]
    roles: List[str]
    
    # Statistics
    times_used: int
    correct_rate: float
    avg_time_seconds: int
    
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class QuestionDetailResponse(QuestionResponse):
    """Detailed question response (with explanations)"""
    explanation: str
    detailed_explanation: Optional[str]
    common_mistakes: Optional[List[str]]
    
    # All hints
    all_hints: List[str]
    
    class Config:
        from_attributes = True

class QuestionWithAnswerResponse(QuestionDetailResponse):
    """Question response with answers (for review)"""
    # Include correct answers
    correct_answers: Optional[List[str]]
    
    # For MCQ - include correct options
    options_with_answers: Optional[List[Dict[str, Any]]]
    
    # For code - include test cases
    test_cases: Optional[List[Dict[str, Any]]]
    
    # For theory - include expected answer
    expected_answer: Optional[str]
    key_points: Optional[List[str]]
    
    # For system design - include expected components
    expected_components: Optional[List[str]]
    
    # For case study - include analysis required
    analysis_required: Optional[List[str]]
    
    class Config:
        from_attributes = True

class QuestionAttemptResponse(BaseModel):
    """Question attempt response"""
    attempt_id: str
    question_id: str
    is_correct: bool
    time_taken_seconds: int
    hints_used: int
    
    # For code questions
    test_results: Optional[List[Dict[str, Any]]]
    compilation_error: Optional[str]
    runtime_error: Optional[str]
    
    # Explanation
    explanation: str
    correct_answer: Any
    
    attempted_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TopicResponse(BaseModel):
    """Topic response"""
    topic_id: str
    subject: SubjectArea
    name: str
    description: Optional[str]
    parent_topic: Optional[str]
    subtopics: List[str]
    difficulty: DifficultyLevel
    prerequisites: List[str]
    estimated_time: int
    tags: List[str]
    question_count: int
    
    class Config:
        from_attributes = True

class QuestionSetResponse(BaseModel):
    """Question set response"""
    set_id: str
    name: str
    description: Optional[str]
    type: str
    total_questions: int
    subjects: List[SubjectArea]
    topics: List[str]
    difficulty_range: Dict[str, int]
    time_limit: Optional[int]
    company: Optional[str]
    role: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class QuestionSetDetailResponse(QuestionSetResponse):
    """Detailed question set response"""
    questions: List[QuestionResponse]
    shuffle_questions: bool
    shuffle_options: bool
    show_answers: bool
    show_explanations: bool
    allow_retry: bool
    passing_score: Optional[int]
    times_used: int
    average_score: float
    
    class Config:
        from_attributes = True

class PracticeSessionResponse(BaseModel):
    """Practice session response"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime]
    time_spent: Optional[int]
    questions_answered: int
    total_questions: int
    correct_answers: int
    incorrect_answers: int
    score: Optional[float]
    accuracy: Optional[float]
    session_type: str
    completed: bool
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PracticeSessionDetailResponse(PracticeSessionResponse):
    """Detailed practice session response"""
    questions_status: Dict[str, Dict[str, Any]]
    set_id: Optional[str]
    
    class Config:
        from_attributes = True