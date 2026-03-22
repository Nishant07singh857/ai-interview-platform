"""
AI Interviewer Models - Complete implementation for AI-powered interviews
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class InterviewType(str, Enum):
    """Types of AI interviews"""
    VOICE = "voice"
    VIDEO = "video"
    TEXT = "text"
    MIXED = "mixed"

class InterviewStatus(str, Enum):
    """Interview session status"""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
    TIMED_OUT = "timed_out"
    CANCELLED = "cancelled"

class InterviewDifficulty(str, Enum):
    """Interview difficulty levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class InterviewMode(str, Enum):
    """Interview modes"""
    PRACTICE = "practice"
    MOCK = "mock"
    ASSESSMENT = "assessment"
    COMPANY_SPECIFIC = "company_specific"

class QuestionCategory(str, Enum):
    """Categories of interview questions"""
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    CASE_STUDY = "case_study"
    ML_DESIGN = "ml_design"
    RESEARCH = "research"

class AIInterviewSession(BaseModel):
    """Main AI Interview session model"""
    session_id: str
    user_id: str
    interview_type: InterviewType
    interview_mode: InterviewMode
    status: InterviewStatus = InterviewStatus.SCHEDULED
    
    # Configuration
    title: str
    description: Optional[str] = None
    difficulty: InterviewDifficulty = InterviewDifficulty.INTERMEDIATE
    duration_minutes: int = 30
    company_focus: Optional[str] = None
    role_focus: Optional[str] = None
    
    # Categories to cover
    categories: List[QuestionCategory] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    
    # Questions
    questions: List[Dict[str, Any]] = Field(default_factory=list)
    current_question_index: int = 0
    total_questions: int = 0
    
    # Responses
    responses: List[Dict[str, Any]] = Field(default_factory=list)
    
    # AI Feedback
    feedback: Optional[Dict[str, Any]] = None
    scores: Dict[str, float] = Field(default_factory=dict)
    
    # Timestamps
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Media
    recording_url: Optional[str] = None
    transcript_url: Optional[str] = None
    
    # Settings
    allow_follow_up: bool = True
    allow_hints: bool = True
    show_feedback_immediately: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InterviewQuestion(BaseModel):
    """Interview question model"""
    question_id: str
    category: QuestionCategory
    difficulty: InterviewDifficulty
    
    # Content
    question_text: str
    context: Optional[str] = None
    expected_points: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
    
    # For coding questions
    code_snippet: Optional[str] = None
    programming_language: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    
    # For system design
    requirements: Optional[List[str]] = None
    constraints: Optional[List[str]] = None
    
    # Evaluation criteria
    evaluation_criteria: Dict[str, float] = Field(default_factory=dict)
    max_score: int = 10
    
    # Hints
    hints: List[str] = Field(default_factory=list)
    
    # Resources
    references: List[Dict[str, str]] = Field(default_factory=list)

class InterviewResponse(BaseModel):
    """User's response to interview question"""
    response_id: str
    question_id: str
    user_id: str
    session_id: str
    
    # Response content
    text_response: Optional[str] = None
    audio_response_url: Optional[str] = None
    video_response_url: Optional[str] = None
    code_response: Optional[str] = None
    
    # Metadata
    time_taken_seconds: int
    hints_used: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # AI Analysis
    analysis: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InterviewFeedback(BaseModel):
    """Comprehensive interview feedback"""
    session_id: str
    user_id: str
    
    # Overall scores
    overall_score: float
    technical_score: float
    communication_score: float
    problem_solving_score: float
    
    # Category scores
    category_scores: Dict[str, float] = Field(default_factory=dict)
    
    # Detailed feedback
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    
    # Question-wise feedback
    question_feedback: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Transcript
    transcript: Optional[str] = None
    
    # Recommendations
    recommended_topics: List[str] = Field(default_factory=list)
    resources: List[Dict[str, str]] = Field(default_factory=list)
    
    # Comparison
    vs_peers: Optional[Dict[str, float]] = None
    percentile: Optional[float] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InterviewTemplate(BaseModel):
    """Interview template for different scenarios"""
    template_id: str
    name: str
    description: str
    interview_mode: InterviewMode
    difficulty: InterviewDifficulty
    
    # Company specific
    company: Optional[str] = None
    role: Optional[str] = None
    
    # Question categories distribution
    category_distribution: Dict[str, int] = Field(default_factory=dict)
    
    # Total questions
    total_questions: int
    
    # Duration
    default_duration: int  # minutes
    
    # Questions pool
    question_pool: List[str] = Field(default_factory=list)  # Question IDs
    
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class VoiceAnalysis(BaseModel):
    """Voice analysis for interview responses"""
    response_id: str
    
    # Speech metrics
    speaking_rate: float  # words per minute
    clarity_score: float  # 0-100
    confidence_score: float  # 0-100
    
    # Filler words
    filler_word_count: int
    filler_words: List[str] = Field(default_factory=list)
    
    # Pauses
    total_pauses: int
    avg_pause_duration: float  # seconds
    
    # Sentiment
    sentiment: str  # positive, neutral, negative
    sentiment_score: float
    
    # Key phrases
    key_phrases: List[str] = Field(default_factory=list)
    
    # Grammar
    grammar_score: float
    grammar_issues: List[str] = Field(default_factory=list)

class VideoAnalysis(BaseModel):
    """Video analysis for interview responses"""
    response_id: str
    
    # Facial expressions
    eye_contact_score: float  # 0-100
    smile_frequency: float
    confidence_score: float
    
    # Body language
    posture_score: float
    hand_gestures_score: float
    fidgeting_score: float
    
    # Emotions detected
    emotions: Dict[str, float] = Field(default_factory=dict)
    
    # Attention
    attention_score: float
    distractions: List[str] = Field(default_factory=list)