"""
Analytics Schemas - Pydantic models for analytics-related API requests/responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date

from app.models.analytics import TimeFrame, MetricType

# Request Schemas
class AnalyticsRequest(BaseModel):
    """Analytics request parameters"""
    timeframe: TimeFrame = TimeFrame.ALL_TIME
    subjects: Optional[List[str]] = None
    include_details: bool = False

class ComparisonRequest(BaseModel):
    """Comparison request parameters"""
    peer_group: str = "all"  # "all", "same_level", "target_company"
    subjects: Optional[List[str]] = None

# Response Schemas
class AnalyticsSummaryResponse(BaseModel):
    """Analytics summary response"""
    user_id: str
    overall_accuracy: float
    total_questions: int
    current_streak: int
    longest_streak: int
    total_practice_time: int
    average_daily_time: float
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PerformanceTrendResponse(BaseModel):
    """Performance trend response"""
    dates: List[str]
    accuracy: List[float]
    volume: List[int]
    time_spent: List[int]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SubjectPerformanceResponse(BaseModel):
    """Subject performance response"""
    subjects: List[Dict[str, Any]]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TopicMasteryResponse(BaseModel):
    """Topic mastery response"""
    mastered_topics: List[Dict[str, Any]]
    in_progress_topics: List[Dict[str, Any]]
    not_started_topics: List[Dict[str, Any]]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CompanyReadinessResponse(BaseModel):
    """Company readiness response"""
    companies: List[Dict[str, Any]]
    top_matches: List[Dict[str, Any]]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class WeeklyReportResponse(BaseModel):
    """Weekly report response"""
    week_start: date
    week_end: date
    summary: Dict[str, Any]
    trends: Dict[str, Any]
    highlights: Dict[str, Any]
    recommendations: List[str]
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }

class LearningPathResponse(BaseModel):
    """Learning path response"""
    target_role: Optional[str]
    target_companies: List[str]
    milestones: List[Dict[str, Any]]
    weekly_focus: List[Dict[str, Any]]
    estimated_completion: Optional[date]
    
    class Config:
        json_encoders = {
            date: lambda v: v.isoformat()
        }

class PeerComparisonResponse(BaseModel):
    """Peer comparison response"""
    percentile: float
    vs_average: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    rank: Optional[int]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class PredictionResponse(BaseModel):
    """Prediction response"""
    predicted_accuracy: float
    readiness_timeline: List[Dict[str, Any]]
    risk_areas: List[str]
    recommendations: List[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ExportAnalyticsResponse(BaseModel):
    """Export analytics response"""
    format: str
    url: str
    expires_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }