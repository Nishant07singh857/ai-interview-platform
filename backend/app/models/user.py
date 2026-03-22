"""
User Models - Complete implementation with all user-related models
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    """User role enumeration"""
    FREE = "free"
    PRO = "pro"
    PREMIUM = "premium"
    ADMIN = "admin"
    MODERATOR = "moderator"

class UserStatus(str, Enum):
    """User account status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    DELETED = "deleted"

class ExperienceLevel(str, Enum):
    """Experience level enumeration"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class User(BaseModel):
    """Main User model"""
    uid: str
    email: EmailStr
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    role: UserRole = UserRole.FREE
    status: UserStatus = UserStatus.ACTIVE
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    last_active: Optional[datetime] = None
    
    # Profile
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    
    # Professional
    current_company: Optional[str] = None
    current_role: Optional[str] = None
    years_of_experience: Optional[float] = None
    experience_level: ExperienceLevel = ExperienceLevel.BEGINNER
    
    # Education
    education: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    
    # Skills
    skills: Dict[str, List[str]] = Field(default_factory=lambda: {
        "technical": [],
        "soft": [],
        "domain": []
    })
    
    # Stats
    stats: Dict[str, Any] = Field(default_factory=lambda: {
        "total_questions": 0,
        "correct_answers": 0,
        "accuracy": 0.0,
        "current_streak": 0,
        "longest_streak": 0,
        "total_practice_time": 0,
        "total_tests_taken": 0,
        "average_score": 0.0
    })
    
    # Resume
    resume_url: Optional[str] = None
    resume_parsed_at: Optional[datetime] = None
    parsed_resume: Optional[Dict[str, Any]] = None
    
    # Targets
    target_companies: List[str] = Field(default_factory=list)
    target_roles: List[str] = Field(default_factory=list)
    target_interview_date: Optional[datetime] = None
    
    # Preferences
    preferences: Dict[str, Any] = Field(default_factory=lambda: {
        "theme": "light",
        "language": "en",
        "notifications": {
            "email": True,
            "push": True,
            "daily_reminder": True,
            "weekly_report": True
        },
        "daily_goal": 20,
        "difficulty_preference": "medium",
        "subjects_interest": ["ml", "dl", "ds", "da", "ai"]
    })
    
    # Subscription
    subscription_id: Optional[str] = None
    subscription_plan: Optional[str] = None
    subscription_expires: Optional[datetime] = None
    
    # Security
    email_verified: bool = False
    mfa_enabled: bool = False
    mfa_secret: Optional[str] = None
    token_valid_after: Optional[datetime] = None
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserProfile(BaseModel):
    """User profile for public view"""
    uid: str
    display_name: Optional[str]
    photo_url: Optional[str]
    bio: Optional[str]
    current_company: Optional[str]
    current_role: Optional[str]
    experience_level: ExperienceLevel
    skills: Dict[str, List[str]]
    stats: Dict[str, Any]
    created_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserSession(BaseModel):
    """User session model"""
    session_id: str
    user_id: str
    token: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: str
    user_agent: str
    device_type: str
    location: Optional[str] = None
    is_active: bool = True
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserSkill(BaseModel):
    """User skill tracking"""
    user_id: str
    subject: str
    topic: str
    proficiency: float = 0.0  # 0-100
    level: ExperienceLevel = ExperienceLevel.BEGINNER
    questions_attempted: int = 0
    correct_answers: int = 0
    time_spent: int = 0  # minutes
    last_practiced: Optional[datetime] = None
    mastery_score: float = 0.0
    weak_areas: List[str] = Field(default_factory=list)
    strong_areas: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserProgress(BaseModel):
    """Daily user progress"""
    user_id: str
    date: str  # YYYY-MM-DD
    questions_attempted: int = 0
    correct_answers: int = 0
    time_spent: int = 0  # minutes
    subjects_practiced: List[str] = Field(default_factory=list)
    topics_practiced: List[str] = Field(default_factory=list)
    accuracy: float = 0.0
    streak_continued: bool = False
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserAchievement(BaseModel):
    """User achievements/badges"""
    achievement_id: str
    user_id: str
    name: str
    description: str
    icon: str
    category: str  # practice, streak, accuracy, etc.
    earned_at: datetime
    progress: float = 100.0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserNotification(BaseModel):
    """User notifications"""
    notification_id: str
    user_id: str
    type: str  # info, success, warning, error
    title: str
    message: str
    link: Optional[str] = None
    read: bool = False
    created_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }