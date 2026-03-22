"""
Analytics Models - Complete implementation for analytics and insights
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from enum import Enum

class TimeFrame(str, Enum):
    """Time frame for analytics"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    ALL_TIME = "all_time"

class MetricType(str, Enum):
    """Types of metrics"""
    ACCURACY = "accuracy"
    SPEED = "speed"
    VOLUME = "volume"
    CONSISTENCY = "consistency"
    MASTERY = "mastery"

class UserAnalytics(BaseModel):
    """Main user analytics model"""
    user_id: str
    last_updated: datetime
    
    # Overall metrics
    total_questions_attempted: int = 0
    total_correct: int = 0
    total_incorrect: int = 0
    overall_accuracy: float = 0.0
    average_time_per_question: float = 0.0
    
    # Streak
    current_streak: int = 0
    longest_streak: int = 0
    last_active_date: Optional[date] = None
    
    # Time based
    total_practice_time: int = 0  # minutes
    average_daily_time: float = 0.0
    most_active_day: Optional[str] = None
    
    # Subject performance
    subject_performance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Topic mastery
    topic_mastery: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Difficulty performance
    difficulty_performance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Question type performance
    question_type_performance: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Company readiness
    company_readiness: Dict[str, float] = Field(default_factory=dict)
    
    # Learning pace
    learning_pace: Dict[str, float] = Field(default_factory=dict)
    
    # Predictions
    predicted_readiness: Dict[str, float] = Field(default_factory=dict)
    recommended_focus: List[Dict[str, Any]] = Field(default_factory=list)

class DailyProgress(BaseModel):
    """Daily progress tracking"""
    user_id: str
    date: date
    questions_attempted: int = 0
    correct_answers: int = 0
    accuracy: float = 0.0
    time_spent: int = 0  # minutes
    subjects_practiced: List[str] = Field(default_factory=list)
    topics_practiced: List[str] = Field(default_factory=list)
    streaks_maintained: bool = False
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }

class WeeklyReport(BaseModel):
    """Weekly performance report"""
    user_id: str
    week_start: date
    week_end: date
    
    # Summary
    total_questions: int
    average_accuracy: float
    total_time: int  # minutes
    active_days: int
    
    # Trends
    accuracy_trend: List[float]
    volume_trend: List[int]
    time_trend: List[int]
    
    # Best performance
    best_day: Dict[str, Any]
    best_subject: Dict[str, Any]
    best_topic: Dict[str, Any]
    
    # Improvements
    improved_areas: List[Dict[str, Any]]
    declined_areas: List[Dict[str, Any]]
    
    # Recommendations
    focus_areas: List[str]
    achievements: List[str]
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }

class SubjectMastery(BaseModel):
    """Subject mastery analysis"""
    subject: str
    overall_mastery: float  # 0-100
    
    # Topics breakdown
    topics: Dict[str, Dict[str, Any]]
    
    # Strengths and weaknesses
    strong_topics: List[str]
    weak_topics: List[str]
    
    # Progress over time
    mastery_history: List[Dict[str, Any]]
    
    # Recommendations
    next_topics: List[str]
    review_topics: List[str]
    
    # Time to mastery prediction
    estimated_time_to_master: Optional[int] = None  # days

class CompanyReadiness(BaseModel):
    """Company-specific readiness analysis"""
    company: str
    
    # Overall readiness
    overall_score: float  # 0-100
    readiness_level: str  # "not_ready", "almost_ready", "ready", "highly_ready"
    
    # Component scores
    technical_score: float
    behavioral_score: float
    system_design_score: float
    
    # Topic readiness
    topic_readiness: Dict[str, float]
    
    # Gap analysis
    critical_gaps: List[str]
    recommended_topics: List[str]
    
    # Success probability
    interview_success_probability: float
    estimated_preparation_time: int  # days
    
    # Comparison
    vs_peers: Dict[str, float]
    vs_top_performers: Dict[str, float]

class SkillGap(BaseModel):
    """Skill gap analysis"""
    skill_name: str
    current_level: str
    required_level: str
    gap_severity: str  # "low", "medium", "high"
    estimated_time_to_close: int  # days
    resources: List[Dict[str, str]]
    
class LearningPath(BaseModel):
    """Personalized learning path"""
    user_id: str
    generated_at: datetime
    
    # Overall plan
    target_role: Optional[str]
    target_companies: List[str]
    estimated_completion_date: Optional[date]
    
    # Milestones
    milestones: List[Dict[str, Any]]
    
    # Weekly focus
    weekly_focus: List[Dict[str, Any]]
    
    # Daily recommendations
    daily_recommendations: Dict[str, List[Dict[str, Any]]]
    
    # Resource recommendations
    resources: List[Dict[str, Any]]
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat()
        }

class PerformancePrediction(BaseModel):
    """Performance predictions"""
    user_id: str
    predicted_at: datetime
    
    # Future performance
    predicted_accuracy_next_week: float
    predicted_topics_to_master: List[str]
    predicted_streak: int
    
    # Interview readiness
    readiness_timeline: List[Dict[str, Any]]
    
    # Risk areas
    risk_areas: List[Dict[str, Any]]
    
    # Recommendations
    preventive_actions: List[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PeerComparison(BaseModel):
    """Peer comparison analytics"""
    user_id: str
    compared_at: datetime
    
    # Overall comparison
    percentile_rank: float
    vs_average: Dict[str, float]
    vs_top_10: Dict[str, float]
    
    # Subject comparison
    subject_comparison: Dict[str, Dict[str, float]]
    
    # Strengths vs peers
    relative_strengths: List[str]
    relative_weaknesses: List[str]
    
    # Ranking
    global_rank: Optional[int]
    subject_ranks: Dict[str, int]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }