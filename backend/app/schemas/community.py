"""
Community Schemas - Pydantic models for community features
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Forum Schemas
class ForumResponse(BaseModel):
    """Forum response"""
    forum_id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    thread_count: int = 0
    last_activity: Optional[str] = None
    
    class Config:
        from_attributes = True

# Thread Schemas
class ThreadResponse(BaseModel):
    """Thread response"""
    thread_id: str
    forum_id: str
    user_id: str
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    title: str
    content: str
    tags: List[str] = Field(default_factory=list)
    views: int = 0
    likes: int = 0
    reply_count: int = 0
    created_at: str
    updated_at: Optional[str] = None
    last_activity: str
    liked: bool = False
    
    class Config:
        from_attributes = True

# Post Schemas
class PostResponse(BaseModel):
    """Post response"""
    post_id: str
    thread_id: str
    user_id: str
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    content: str
    parent_id: Optional[str] = None
    likes: int = 0
    created_at: str
    updated_at: Optional[str] = None
    liked: bool = False
    
    class Config:
        from_attributes = True

# Study Group Schemas
class StudyGroupResponse(BaseModel):
    """Study group response"""
    group_id: str
    name: str
    description: Optional[str] = None
    topics: List[str] = Field(default_factory=list)
    member_count: int = 0
    max_members: int = 20
    created_by: str
    created_at: str
    members: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        from_attributes = True

# Leaderboard Schemas
class LeaderboardResponse(BaseModel):
    """Leaderboard response"""
    user_id: str
    user_name: str
    user_avatar: Optional[str] = None
    score: float
    questions_attempted: int
    correct_answers: int
    rank: Optional[int] = None
    
    class Config:
        from_attributes = True

# Badge Schemas
class BadgeResponse(BaseModel):
    """Badge response"""
    badge_id: str
    name: str
    description: str
    icon: str
    category: str
    earned_at: Optional[str] = None
    
    class Config:
        from_attributes = True