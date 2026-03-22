"""
Resume Schemas - Pydantic models for resume-related API requests/responses
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from app.models.resume import ResumeStatus, ExperienceLevel, SkillProficiency

# Request Schemas
class ResumeUploadRequest(BaseModel):
    """Resume upload request"""
    filename: str
    file_size: int
    mime_type: str

class ResumeAnalysisRequest(BaseModel):
    """Resume analysis request"""
    resume_id: str
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    job_description: Optional[str] = None

class GapAnalysisRequest(BaseModel):
    """Gap analysis request"""
    resume_id: str
    target_company: str
    target_role: str
    job_description: Optional[str] = None

class RoadmapRequest(BaseModel):
    """Roadmap generation request"""
    resume_id: str
    target_company: str
    target_role: str
    target_interview_date: Optional[datetime] = None
    hours_per_week: int = Field(10, ge=1, le=40)

# Response Schemas
class ResumeResponse(BaseModel):
    """Resume response"""
    resume_id: str
    filename: str
    file_url: str
    file_size: int
    status: ResumeStatus
    uploaded_at: datetime
    parsed_at: Optional[datetime]
    analyzed_at: Optional[datetime]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ParsedResumeResponse(BaseModel):
    """Parsed resume response"""
    resume_id: str
    personal_info: Dict[str, Any]
    summary: Optional[str]
    skills: Dict[str, List[Dict[str, Any]]]
    work_experience: List[Dict[str, Any]]
    total_experience_years: float
    experience_level: ExperienceLevel
    education: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    certifications: List[Dict[str, Any]]
    parsed_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ResumeAnalysisResponse(BaseModel):
    """Resume analysis response"""
    resume_id: str
    overall_score: float
    ats_score: float
    completeness_score: float
    strengths: List[str]
    weaknesses: List[str]
    gaps: List[Dict[str, Any]]
    immediate_actions: List[str]
    short_term_goals: List[str]
    target_readiness: Dict[str, float]
    analyzed_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GapAnalysisResponse(BaseModel):
    """Gap analysis response"""
    resume_id: str
    target_company: str
    target_role: str
    overall_readiness: float
    technical_readiness: float
    behavioral_readiness: float
    skill_gaps: List[Dict[str, Any]]
    experience_gap: Dict[str, Any]
    education_gap: Dict[str, Any]
    project_gap: Dict[str, Any]
    high_priority_gaps: List[Dict[str, Any]]
    estimated_preparation_time: int
    recommended_interview_date: Optional[datetime]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RoadmapMilestoneResponse(BaseModel):
    """Roadmap milestone response"""
    milestone_id: str
    title: str
    description: str
    category: str
    target_date: datetime
    completed: bool
    progress: float
    tasks: List[Dict[str, Any]]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class LearningRoadmapResponse(BaseModel):
    """Learning roadmap response"""
    roadmap_id: str
    target_company: str
    target_role: str
    created_at: datetime
    target_interview_date: datetime
    total_days: int
    overall_progress: float
    milestones: List[RoadmapMilestoneResponse]
    weekly_plan: List[Dict[str, Any]]
    recommended_courses: List[Dict[str, Any]]
    recommended_practice: List[Dict[str, Any]]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class SkillAssessmentResponse(BaseModel):
    """Skill assessment response"""
    skill_name: str
    proficiency: SkillProficiency
    confidence_score: float
    years_experience: Optional[float]
    projects_count: int
    recommendations: List[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CompanyMatchResponse(BaseModel):
    """Company match response"""
    company: str
    match_score: float
    readiness_score: float
    skill_match: float
    experience_match: float
    education_match: float
    missing_skills: List[str]
    recommended_roles: List[str]
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }