"""
Resume Models - Complete implementation for resume parsing, analysis and roadmap
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ResumeStatus(str, Enum):
    """Resume processing status"""
    UPLOADED = "uploaded"
    PARSING = "parsing"
    PARSED = "parsed"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    FAILED = "failed"

class ExperienceLevel(str, Enum):
    """Experience level based on resume"""
    ENTRY = "entry_level"
    JUNIOR = "junior"
    MID = "mid_level"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"

class SkillProficiency(str, Enum):
    """Skill proficiency levels"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class Resume(BaseModel):
    """Main resume model"""
    resume_id: str
    user_id: str
    filename: str
    file_url: str
    file_size: int
    mime_type: str
    status: ResumeStatus = ResumeStatus.UPLOADED
    uploaded_at: datetime
    parsed_at: Optional[datetime] = None
    analyzed_at: Optional[datetime] = None
    
    # Parsed data
    parsed_data: Optional[Dict[str, Any]] = None
    
    # Analysis results
    analysis: Optional[Dict[str, Any]] = None
    
    # Error if failed
    error_message: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ParsedResume(BaseModel):
    """Parsed resume data structure"""
    # Personal Information
    personal_info: Dict[str, Any] = Field(default_factory=dict)
    
    # Professional Summary
    summary: Optional[str] = None
    
    # Skills
    skills: Dict[str, List[Dict[str, Any]]] = Field(default_factory=lambda: {
        "technical": [],
        "soft": [],
        "domain": [],
        "tools": [],
        "languages": []
    })
    
    # Experience
    work_experience: List[Dict[str, Any]] = Field(default_factory=list)
    total_experience_years: float = 0.0
    experience_level: ExperienceLevel = ExperienceLevel.ENTRY
    
    # Education
    education: List[Dict[str, Any]] = Field(default_factory=list)
    highest_degree: Optional[str] = None
    graduation_year: Optional[int] = None
    
    # Projects
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    project_count: int = 0
    
    # Certifications
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    certification_count: int = 0
    
    # Publications
    publications: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Achievements
    achievements: List[str] = Field(default_factory=list)
    
    # Languages
    languages: List[Dict[str, str]] = Field(default_factory=list)
    
    # Contact
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None

class SkillAnalysis(BaseModel):
    """Detailed skill analysis"""
    skill_name: str
    category: str
    proficiency: SkillProficiency
    years_of_experience: Optional[float] = None
    last_used: Optional[str] = None
    projects_using: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0, le=1)
    is_core_competency: bool = False
    recommendations: List[str] = Field(default_factory=list)

class ExperienceAnalysis(BaseModel):
    """Experience analysis"""
    company: str
    role: str
    duration_months: int
    achievements: List[str]
    technologies_used: List[str]
    relevance_score: float = Field(..., ge=0, le=1)
    growth_trajectory: str  # "increasing", "stable", "decreasing"

class EducationAnalysis(BaseModel):
    """Education analysis"""
    degree: str
    field: str
    institution: str
    graduation_year: int
    gpa: Optional[float] = None
    relevance_to_target: float = Field(..., ge=0, le=1)
    notable_courses: List[str] = Field(default_factory=list)

class ResumeAnalysis(BaseModel):
    """Complete resume analysis"""
    # Overall metrics
    overall_score: float = Field(..., ge=0, le=100)
    ats_score: float = Field(..., ge=0, le=100)
    completeness_score: float = Field(..., ge=0, le=100)
    
    # Detailed analysis
    skill_analysis: List[SkillAnalysis] = Field(default_factory=list)
    experience_analysis: List[ExperienceAnalysis] = Field(default_factory=list)
    education_analysis: List[EducationAnalysis] = Field(default_factory=list)
    project_analysis: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Strengths and weaknesses
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    gaps: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Recommendations
    immediate_actions: List[str] = Field(default_factory=list)
    short_term_goals: List[str] = Field(default_factory=list)
    long_term_goals: List[str] = Field(default_factory=list)
    
    # Target alignment
    target_readiness: Dict[str, float] = Field(default_factory=dict)
    recommended_targets: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Market insights
    market_demand: Dict[str, Any] = Field(default_factory=dict)
    salary_estimate: Optional[Dict[str, Any]] = None
    
    analyzed_at: datetime

class GapAnalysis(BaseModel):
    """Gap analysis between current and target"""
    current_state: ParsedResume
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    
    # Skill gaps
    skill_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    experience_gap: Dict[str, Any] = Field(default_factory=dict)
    education_gap: Dict[str, Any] = Field(default_factory=dict)
    project_gap: Dict[str, Any] = Field(default_factory=dict)
    certification_gap: List[str] = Field(default_factory=list)
    
    # Readiness scores
    overall_readiness: float = 0.0
    technical_readiness: float = 0.0
    behavioral_readiness: float = 0.0
    system_design_readiness: float = 0.0
    
    # Priority areas
    high_priority_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    medium_priority_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    low_priority_gaps: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Timeline
    estimated_preparation_time: int = 0  # days
    recommended_interview_date: Optional[datetime] = None

class RoadmapMilestone(BaseModel):
    """Roadmap milestone"""
    milestone_id: str
    title: str
    description: str
    category: str  # "skill", "project", "certification", "practice"
    target_date: datetime
    completed: bool = False
    completed_at: Optional[datetime] = None
    tasks: List[Dict[str, Any]] = Field(default_factory=list)
    resources: List[Dict[str, str]] = Field(default_factory=list)
    progress: float = 0.0

class LearningRoadmap(BaseModel):
    """Personalized learning roadmap"""
    roadmap_id: str
    user_id: str
    target_company: Optional[str] = None
    target_role: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Timeline
    start_date: datetime
    target_interview_date: datetime
    total_days: int
    
    # Milestones
    milestones: List[RoadmapMilestone] = Field(default_factory=list)
    
    # Weekly breakdown
    weekly_plan: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Daily tasks
    daily_tasks: Dict[str, List[Dict[str, Any]]] = Field(default_factory=dict)
    
    # Resources
    recommended_courses: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_books: List[Dict[str, Any]] = Field(default_factory=list)
    recommended_practice: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Progress tracking
    overall_progress: float = 0.0
    completed_milestones: int = 0
    total_milestones: int = 0
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }