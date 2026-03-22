"""
User Schemas - Pydantic models for API requests/responses
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import re

from app.models.user import UserRole, ExperienceLevel

# Request Schemas
class UserCreate(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    display_name: Optional[str] = Field(None, min_length=2, max_length=50)
    
    @field_validator('password')
    def validate_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v
    
    @field_validator('display_name')
    def validate_display_name(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_\s]+$', v):
            raise ValueError('Display name can only contain letters, numbers, spaces and underscores')
        return v

class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str

class ChangePassword(BaseModel):
    """Password change request"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    def validate_new_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class PasswordReset(BaseModel):
    """Password reset request"""
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('new_password')
    def validate_new_password(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class EmailVerification(BaseModel):
    """Email verification request"""
    token: str

class UserUpdate(BaseModel):
    """User profile update request"""
    display_name: Optional[str] = Field(None, min_length=2, max_length=50)
    photo_url: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    location: Optional[str] = Field(None, max_length=100)
    website: Optional[str] = None
    github: Optional[str] = None
    linkedin: Optional[str] = None
    twitter: Optional[str] = None
    current_company: Optional[str] = Field(None, max_length=100)
    current_role: Optional[str] = Field(None, max_length=100)
    years_of_experience: Optional[float] = Field(None, ge=0, le=50)
    experience_level: Optional[ExperienceLevel] = None
    
    @field_validator('website', 'github', 'linkedin', 'twitter')
    def validate_urls(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        return v
    
    @field_validator('display_name')
    def validate_display_name(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9_\s]+$', v):
            raise ValueError('Display name can only contain letters, numbers, spaces and underscores')
        return v

class UserPreferencesUpdate(BaseModel):
    """User preferences update"""
    theme: Optional[str] = Field(None, pattern='^(light|dark|system)$')
    language: Optional[str] = Field(None, pattern='^(en|es|fr|de|zh|ja)$')
    notifications: Optional[Dict[str, bool]] = None
    daily_goal: Optional[int] = Field(None, ge=1, le=100)
    difficulty_preference: Optional[str] = Field(None, pattern='^(easy|medium|hard|expert)$')
    subjects_interest: Optional[List[str]] = None

class UserTargetUpdate(BaseModel):
    """User target companies and roles update"""
    target_companies: Optional[List[str]] = None
    target_roles: Optional[List[str]] = None
    target_interview_date: Optional[datetime] = None

# Response Schemas
class UserResponse(BaseModel):
    """User data response"""
    uid: str
    email: str
    display_name: Optional[str]
    photo_url: Optional[str]
    role: UserRole
    status: str
    created_at: datetime
    last_login: Optional[datetime]
    email_verified: bool
    mfa_enabled: bool
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserProfileResponse(BaseModel):
    """User profile response (public)"""
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
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserDetailResponse(UserResponse):
    """Detailed user response (private)"""
    bio: Optional[str]
    location: Optional[str]
    website: Optional[str]
    github: Optional[str]
    linkedin: Optional[str]
    twitter: Optional[str]
    current_company: Optional[str]
    current_role: Optional[str]
    years_of_experience: Optional[float]
    experience_level: ExperienceLevel
    education: List[Dict[str, Any]]
    certifications: List[str]
    skills: Dict[str, List[str]]
    stats: Dict[str, Any]
    preferences: Dict[str, Any]
    target_companies: List[str]
    target_roles: List[str]
    target_interview_date: Optional[datetime]
    subscription_plan: Optional[str]
    subscription_expires: Optional[datetime]
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class UserStatsResponse(BaseModel):
    """User statistics response"""
    total_questions: int
    correct_answers: int
    accuracy: float
    current_streak: int
    longest_streak: int
    total_practice_time: int
    total_tests_taken: int
    average_score: float
    subjects_breakdown: Dict[str, Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
    
    class Config:
        from_attributes = True