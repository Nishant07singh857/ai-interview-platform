"""
Community Endpoints - Complete community features API
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from app.core.deps import get_current_user, get_current_admin_user
from app.models.user import User
from app.schemas.community import (
    ForumResponse, ThreadResponse, PostResponse,
    StudyGroupResponse, LeaderboardResponse, BadgeResponse
)
from app.services.community_service import CommunityService

router = APIRouter(prefix="/community", tags=["Community"])
logger = logging.getLogger(__name__)
community_service = CommunityService()

# Forums
@router.get("/forums", response_model=List[ForumResponse])
async def get_forums(
    current_user: User = Depends(get_current_user)
):
    """Get all forums"""
    try:
        forums = await community_service.get_forums()
        return forums
    except Exception as e:
        logger.error(f"Error getting forums: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get forums")

@router.get("/forums/{forum_id}", response_model=ForumResponse)
async def get_forum(
    forum_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get forum details"""
    try:
        forum = await community_service.get_forum(forum_id)
        if not forum:
            raise HTTPException(status_code=404, detail="Forum not found")
        return forum
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting forum: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get forum")

# Threads
@router.get("/forums/{forum_id}/threads", response_model=List[ThreadResponse])
async def get_threads(
    forum_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("latest", pattern="^(latest|popular|unanswered)$"),
    current_user: User = Depends(get_current_user)
):
    """Get threads in a forum"""
    try:
        threads = await community_service.get_threads(forum_id, page, limit, sort)
        return threads
    except Exception as e:
        logger.error(f"Error getting threads: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get threads")

@router.get("/threads/{thread_id}", response_model=ThreadResponse)
async def get_thread(
    thread_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get thread details"""
    try:
        thread = await community_service.get_thread(thread_id, current_user.uid)
        if not thread:
            raise HTTPException(status_code=404, detail="Thread not found")
        return thread
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting thread: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get thread")

@router.post("/threads", response_model=ThreadResponse)
async def create_thread(
    thread_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new thread"""
    try:
        thread = await community_service.create_thread(current_user.uid, thread_data)
        return thread
    except Exception as e:
        logger.error(f"Error creating thread: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create thread")

@router.put("/threads/{thread_id}")
async def update_thread(
    thread_id: str,
    thread_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update a thread"""
    try:
        thread = await community_service.update_thread(thread_id, current_user.uid, thread_data)
        return thread
    except Exception as e:
        logger.error(f"Error updating thread: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update thread")

@router.delete("/threads/{thread_id}")
async def delete_thread(
    thread_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a thread"""
    try:
        await community_service.delete_thread(thread_id, current_user.uid)
        return {"message": "Thread deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting thread: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete thread")

@router.post("/threads/{thread_id}/like")
async def like_thread(
    thread_id: str,
    current_user: User = Depends(get_current_user)
):
    """Like a thread"""
    try:
        result = await community_service.like_thread(thread_id, current_user.uid)
        return result
    except Exception as e:
        logger.error(f"Error liking thread: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to like thread")

@router.delete("/threads/{thread_id}/like")
async def unlike_thread(
    thread_id: str,
    current_user: User = Depends(get_current_user)
):
    """Unlike a thread"""
    try:
        result = await community_service.unlike_thread(thread_id, current_user.uid)
        return result
    except Exception as e:
        logger.error(f"Error unliking thread: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unlike thread")

# Posts
@router.get("/threads/{thread_id}/posts", response_model=List[PostResponse])
async def get_posts(
    thread_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get posts in a thread"""
    try:
        posts = await community_service.get_posts(thread_id, page, limit)
        return posts
    except Exception as e:
        logger.error(f"Error getting posts: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get posts")

@router.post("/threads/{thread_id}/posts", response_model=PostResponse)
async def create_post(
    thread_id: str,
    post_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a new post"""
    try:
        post = await community_service.create_post(
            thread_id, current_user.uid, post_data
        )
        return post
    except Exception as e:
        logger.error(f"Error creating post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create post")

@router.put("/posts/{post_id}")
async def update_post(
    post_id: str,
    post_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Update a post"""
    try:
        post = await community_service.update_post(post_id, current_user.uid, post_data)
        return post
    except Exception as e:
        logger.error(f"Error updating post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update post")

@router.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a post"""
    try:
        await community_service.delete_post(post_id, current_user.uid)
        return {"message": "Post deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete post")

@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """Like a post"""
    try:
        result = await community_service.like_post(post_id, current_user.uid)
        return result
    except Exception as e:
        logger.error(f"Error liking post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to like post")

@router.delete("/posts/{post_id}/like")
async def unlike_post(
    post_id: str,
    current_user: User = Depends(get_current_user)
):
    """Unlike a post"""
    try:
        result = await community_service.unlike_post(post_id, current_user.uid)
        return result
    except Exception as e:
        logger.error(f"Error unliking post: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to unlike post")

# Study Groups
@router.get("/study-groups", response_model=List[StudyGroupResponse])
async def get_study_groups(
    topic: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get study groups"""
    try:
        groups = await community_service.get_study_groups(topic)
        return groups
    except Exception as e:
        logger.error(f"Error getting study groups: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get study groups")

@router.get("/study-groups/{group_id}", response_model=StudyGroupResponse)
async def get_study_group(
    group_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get study group details"""
    try:
        group = await community_service.get_study_group(group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Study group not found")
        return group
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting study group: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get study group")

@router.post("/study-groups", response_model=StudyGroupResponse)
async def create_study_group(
    group_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Create a study group"""
    try:
        group = await community_service.create_study_group(current_user.uid, group_data)
        return group
    except Exception as e:
        logger.error(f"Error creating study group: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create study group")

@router.post("/study-groups/{group_id}/join")
async def join_study_group(
    group_id: str,
    current_user: User = Depends(get_current_user)
):
    """Join a study group"""
    try:
        result = await community_service.join_study_group(group_id, current_user.uid)
        return result
    except Exception as e:
        logger.error(f"Error joining study group: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to join study group")

@router.post("/study-groups/{group_id}/leave")
async def leave_study_group(
    group_id: str,
    current_user: User = Depends(get_current_user)
):
    """Leave a study group"""
    try:
        result = await community_service.leave_study_group(group_id, current_user.uid)
        return result
    except Exception as e:
        logger.error(f"Error leaving study group: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to leave study group")

# Leaderboard
@router.get("/leaderboard", response_model=List[LeaderboardResponse])
async def get_leaderboard(
    period: str = Query("all", pattern="^(daily|weekly|monthly|all)$"),
    subject: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user)
):
    """Get leaderboard"""
    try:
        leaderboard = await community_service.get_leaderboard(period, subject, limit)
        return leaderboard
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

# Badges
@router.get("/badges", response_model=List[BadgeResponse])
async def get_all_badges(
    current_user: User = Depends(get_current_user)
):
    """Get all available badges"""
    try:
        badges = await community_service.get_all_badges()
        return badges
    except Exception as e:
        logger.error(f"Error getting badges: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get badges")

@router.get("/users/{user_id}/badges", response_model=List[BadgeResponse])
async def get_user_badges(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get badges earned by a user"""
    try:
        badges = await community_service.get_user_badges(user_id)
        return badges
    except Exception as e:
        logger.error(f"Error getting user badges: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user badges")