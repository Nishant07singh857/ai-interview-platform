"""
Interview Schemas - Pydantic models for interview-related API requests/responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.interview import (
    InterviewType, InterviewStatus, InterviewDifficulty,
    InterviewMode, QuestionCategory
)

# Request Schemas
class InterviewSetupRequest(BaseModel):
    """Interview setup request"""
    interview_type: InterviewType = InterviewType.TEXT
    interview_mode: InterviewMode = InterviewMode.PRACTICE
    difficulty: InterviewDifficulty = InterviewDifficulty.INTERMEDIATE
    duration_minutes: int = Field(30, ge=5, le=120)
    
    # Focus areas
    company_focus: Optional[str] = None
    role_focus: Optional[str] = None
    
    # Categories
    categories: List[QuestionCategory] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    
    # Settings
    allow_follow_up: bool = True
    allow_hints: bool = True
    show_feedback_immediately: bool = False
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        if v not in [15, 30, 45, 60, 90, 120]:
            raise ValueError('Duration must be one of: 15, 30, 45, 60, 90, 120 minutes')
        return v

class InterviewResponseSubmission(BaseModel):
    """Interview response submission"""
    session_id: str
    question_id: str
    
    # Response content (one of these should be provided)
    text_response: Optional[str] = None
    audio_base64: Optional[str] = None
    video_base64: Optional[str] = None
    code_response: Optional[str] = None
    
    # Metadata
    time_taken_seconds: int = Field(..., ge=1, le=3600)
    hints_used: int = Field(0, ge=0)

class InterviewAction(BaseModel):
    """Interview action (pause, resume, end)"""
    session_id: str
    action: str  # pause, resume, end, next_question

class InterviewFeedbackRequest(BaseModel):
    """Request interview feedback"""
    session_id: str
    include_detailed: bool = False

# Response Schemas
class InterviewSessionResponse(BaseModel):
    """Interview session response"""
    session_id: str
    interview_type: InterviewType
    interview_mode: InterviewMode
    status: InterviewStatus
    title: str
    description: Optional[str]
    difficulty: InterviewDifficulty
    duration_minutes: int
    company_focus: Optional[str]
    role_focus: Optional[str]
    
    # Current state
    current_question: Optional[Dict[str, Any]]
    current_question_index: int
    total_questions: int
    questions_answered: int
    
    # Time
    started_at: Optional[datetime]
    time_elapsed: int  # seconds
    time_remaining: int  # seconds
    
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InterviewQuestionResponse(BaseModel):
    """Interview question response"""
    question_id: str
    question_text: str
    context: Optional[str]
    category: QuestionCategory
    difficulty: InterviewDifficulty
    
    # For coding questions
    code_snippet: Optional[str]
    programming_language: Optional[str]
    
    # For system design
    requirements: Optional[List[str]]
    constraints: Optional[List[str]]
    
    # Hints (first hint only if not requested)
    hint: Optional[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InterviewResponseResult(BaseModel):
    """Result of submitting a response"""
    response_id: str
    question_id: str
    next_question: Optional[InterviewQuestionResponse]
    session_completed: bool
    progress: Dict[str, Any]
    
    # Immediate feedback if enabled
    feedback: Optional[Dict[str, Any]]

class InterviewFeedbackResponse(BaseModel):
    """Interview feedback response"""
    session_id: str
    
    # Overall scores
    overall_score: float
    technical_score: float
    communication_score: float
    problem_solving_score: float
    
    # Strengths and weaknesses
    strengths: List[str]
    weaknesses: List[str]
    improvements: List[str]
    
    # Detailed analysis
    category_scores: Dict[str, float]
    question_feedback: List[Dict[str, Any]]
    
    # Recommendations
    recommended_topics: List[str]
    
    # Comparison
    percentile: Optional[float]
    
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InterviewTemplateResponse(BaseModel):
    """Interview template response"""
    template_id: str
    name: str
    description: str
    interview_mode: InterviewMode
    difficulty: InterviewDifficulty
    company: Optional[str]
    role: Optional[str]
    duration_minutes: int
    total_questions: int
    categories: List[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InterviewHistoryResponse(BaseModel):
    """Interview history response"""
    session_id: str
    title: str
    interview_type: InterviewType
    interview_mode: InterviewMode
    difficulty: InterviewDifficulty
    company_focus: Optional[str]
    completed_at: datetime
    overall_score: Optional[float]
    duration_minutes: int
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VoiceAnalysisResponse(BaseModel):
    """Voice analysis response"""
    speaking_rate: float
    clarity_score: float
    confidence_score: float
    filler_word_count: int
    filler_words: List[str]
    sentiment: str
    grammar_score: float
    grammar_issues: List[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VideoAnalysisResponse(BaseModel):
    """Video analysis response"""
    eye_contact_score: float
    confidence_score: float
    posture_score: float
    hand_gestures_score: float
    emotions: Dict[str, float]
    attention_score: float
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }