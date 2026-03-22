"""
Community Service - Complete community features logic
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
from uuid import uuid4

from app.core.database import firebase_client
from app.core.cache import cache_manager
from app.services.user_service import UserService

logger = logging.getLogger(__name__)

class CommunityService:
    """Community service with complete business logic"""
    
    def __init__(self):
        self.user_service = UserService()
    
    # Forum Methods
    async def get_forums(self) -> List[Dict[str, Any]]:
        """Get all forums"""
        
        forums = firebase_client.get_data("forums") or {}
        
        result = []
        for forum_id, forum in forums.items():
            # Get thread count
            threads = firebase_client.query_firestore(
                "threads",
                "forum_id",
                "==",
                forum_id
            )
            
            result.append({
                "forum_id": forum_id,
                "name": forum.get("name"),
                "description": forum.get("description"),
                "icon": forum.get("icon"),
                "thread_count": len(threads),
                "last_activity": forum.get("last_activity"),
            })
        
        return result
    
    async def get_forum(self, forum_id: str) -> Optional[Dict[str, Any]]:
        """Get forum details"""
        
        forum = firebase_client.get_data(f"forums/{forum_id}")
        
        if not forum:
            return None
        
        # Get top threads
        threads = firebase_client.query_firestore(
            "threads",
            "forum_id",
            "==",
            forum_id
        )
        
        # Sort by last activity
        threads.sort(key=lambda x: x.get("last_activity", ""), reverse=True)
        
        return {
            **forum,
            "forum_id": forum_id,
            "threads": threads[:10],
            "thread_count": len(threads),
        }
    
    # Thread Methods
    async def get_threads(
        self,
        forum_id: str,
        page: int,
        limit: int,
        sort: str
    ) -> List[Dict[str, Any]]:
        """Get threads in a forum"""
        
        threads = firebase_client.query_firestore(
            "threads",
            "forum_id",
            "==",
            forum_id
        )
        
        # Apply sorting
        if sort == "latest":
            threads.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort == "popular":
            threads.sort(key=lambda x: x.get("views", 0), reverse=True)
        elif sort == "unanswered":
            threads = [t for t in threads if t.get("reply_count", 0) == 0]
            threads.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Paginate
        start = (page - 1) * limit
        end = start + limit
        paginated = threads[start:end]
        
        # Enhance with user data
        result = []
        for thread in paginated:
            user = await self.user_service.get_user_profile(thread.get("user_id"))
            result.append({
                **thread,
                "user_name": user.get("display_name") if user else "Anonymous",
                "user_avatar": user.get("photo_url") if user else None,
            })
        
        return result
    
    async def get_thread(self, thread_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get thread details"""
        
        thread = firebase_client.get_data(f"threads/{thread_id}")
        
        if not thread:
            return None
        
        # Increment view count
        views = thread.get("views", 0) + 1
        firebase_client.update_data(f"threads/{thread_id}", {"views": views})
        
        # Get posts
        posts = firebase_client.query_firestore(
            "posts",
            "thread_id",
            "==",
            thread_id
        )
        posts.sort(key=lambda x: x.get("created_at", ""))
        
        # Enhance posts with user data
        enhanced_posts = []
        for post in posts:
            user = await self.user_service.get_user_profile(post.get("user_id"))
            enhanced_posts.append({
                **post,
                "user_name": user.get("display_name") if user else "Anonymous",
                "user_avatar": user.get("photo_url") if user else None,
                "liked": user_id in post.get("likes", []),
            })
        
        # Check if user liked the thread
        liked = user_id in thread.get("likes", [])
        
        return {
            **thread,
            "thread_id": thread_id,
            "posts": enhanced_posts,
            "post_count": len(posts),
            "liked": liked,
        }
    
    async def create_thread(self, user_id: str, thread_data: Dict) -> Dict:
        """Create a new thread"""
        
        thread_id = str(uuid4())
        
        thread = {
            "thread_id": thread_id,
            "forum_id": thread_data["forum_id"],
            "user_id": user_id,
            "title": thread_data["title"],
            "content": thread_data["content"],
            "tags": thread_data.get("tags", []),
            "views": 0,
            "likes": [],
            "reply_count": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_activity": datetime.utcnow().isoformat(),
        }
        
        firebase_client.set_data(f"threads/{thread_id}", thread)
        
        # Update forum last activity
        firebase_client.update_data(f"forums/{thread_data['forum_id']}", {
            "last_activity": datetime.utcnow().isoformat()
        })
        
        return thread
    
    async def update_thread(self, thread_id: str, user_id: str, thread_data: Dict) -> Dict:
        """Update a thread"""
        
        thread = firebase_client.get_data(f"threads/{thread_id}")
        
        if not thread:
            raise ValueError("Thread not found")
        
        if thread.get("user_id") != user_id:
            raise ValueError("Not authorized to update this thread")
        
        thread.update(thread_data)
        thread["updated_at"] = datetime.utcnow().isoformat()
        
        firebase_client.set_data(f"threads/{thread_id}", thread)
        
        return thread
    
    async def delete_thread(self, thread_id: str, user_id: str):
        """Delete a thread"""
        
        thread = firebase_client.get_data(f"threads/{thread_id}")
        
        if not thread:
            raise ValueError("Thread not found")
        
        if thread.get("user_id") != user_id:
            raise ValueError("Not authorized to delete this thread")
        
        # Delete all posts in thread
        posts = firebase_client.query_firestore("posts", "thread_id", "==", thread_id)
        for post in posts:
            firebase_client.delete_data(f"posts/{post.get('post_id')}")
        
        firebase_client.delete_data(f"threads/{thread_id}")
    
    async def like_thread(self, thread_id: str, user_id: str) -> Dict:
        """Like a thread"""
        
        thread = firebase_client.get_data(f"threads/{thread_id}")
        
        if not thread:
            raise ValueError("Thread not found")
        
        likes = thread.get("likes", [])
        if user_id not in likes:
            likes.append(user_id)
            firebase_client.update_data(f"threads/{thread_id}", {"likes": likes})
        
        return {"likes": len(likes)}
    
    async def unlike_thread(self, thread_id: str, user_id: str) -> Dict:
        """Unlike a thread"""
        
        thread = firebase_client.get_data(f"threads/{thread_id}")
        
        if not thread:
            raise ValueError("Thread not found")
        
        likes = thread.get("likes", [])
        if user_id in likes:
            likes.remove(user_id)
            firebase_client.update_data(f"threads/{thread_id}", {"likes": likes})
        
        return {"likes": len(likes)}
    
    # Post Methods
    async def get_posts(self, thread_id: str, page: int, limit: int) -> List[Dict]:
        """Get posts in a thread"""
        
        posts = firebase_client.query_firestore(
            "posts",
            "thread_id",
            "==",
            thread_id
        )
        
        posts.sort(key=lambda x: x.get("created_at", ""))
        
        start = (page - 1) * limit
        end = start + limit
        paginated = posts[start:end]
        
        # Enhance with user data
        result = []
        for post in paginated:
            user = await self.user_service.get_user_profile(post.get("user_id"))
            result.append({
                **post,
                "user_name": user.get("display_name") if user else "Anonymous",
                "user_avatar": user.get("photo_url") if user else None,
            })
        
        return result
    
    async def create_post(self, thread_id: str, user_id: str, post_data: Dict) -> Dict:
        """Create a new post"""
        
        post_id = str(uuid4())
        
        post = {
            "post_id": post_id,
            "thread_id": thread_id,
            "user_id": user_id,
            "content": post_data["content"],
            "parent_id": post_data.get("parent_id"),
            "likes": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        firebase_client.set_data(f"posts/{post_id}", post)
        
        # Update thread reply count and last activity
        thread = firebase_client.get_data(f"threads/{thread_id}")
        if thread:
            reply_count = thread.get("reply_count", 0) + 1
            firebase_client.update_data(f"threads/{thread_id}", {
                "reply_count": reply_count,
                "last_activity": datetime.utcnow().isoformat()
            })
        
        return post
    
    async def update_post(self, post_id: str, user_id: str, post_data: Dict) -> Dict:
        """Update a post"""
        
        post = firebase_client.get_data(f"posts/{post_id}")
        
        if not post:
            raise ValueError("Post not found")
        
        if post.get("user_id") != user_id:
            raise ValueError("Not authorized to update this post")
        
        post.update(post_data)
        post["updated_at"] = datetime.utcnow().isoformat()
        
        firebase_client.set_data(f"posts/{post_id}", post)
        
        return post
    
    async def delete_post(self, post_id: str, user_id: str):
        """Delete a post"""
        
        post = firebase_client.get_data(f"posts/{post_id}")
        
        if not post:
            raise ValueError("Post not found")
        
        if post.get("user_id") != user_id:
            raise ValueError("Not authorized to delete this post")
        
        firebase_client.delete_data(f"posts/{post_id}")
        
        # Update thread reply count
        thread = firebase_client.get_data(f"threads/{post.get('thread_id')}")
        if thread:
            reply_count = max(0, thread.get("reply_count", 0) - 1)
            firebase_client.update_data(f"threads/{post.get('thread_id')}", {
                "reply_count": reply_count
            })
    
    async def like_post(self, post_id: str, user_id: str) -> Dict:
        """Like a post"""
        
        post = firebase_client.get_data(f"posts/{post_id}")
        
        if not post:
            raise ValueError("Post not found")
        
        likes = post.get("likes", [])
        if user_id not in likes:
            likes.append(user_id)
            firebase_client.update_data(f"posts/{post_id}", {"likes": likes})
        
        return {"likes": len(likes)}
    
    async def unlike_post(self, post_id: str, user_id: str) -> Dict:
        """Unlike a post"""
        
        post = firebase_client.get_data(f"posts/{post_id}")
        
        if not post:
            raise ValueError("Post not found")
        
        likes = post.get("likes", [])
        if user_id in likes:
            likes.remove(user_id)
            firebase_client.update_data(f"posts/{post_id}", {"likes": likes})
        
        return {"likes": len(likes)}
    
    # Study Group Methods
    async def get_study_groups(self, topic: Optional[str]) -> List[Dict]:
        """Get study groups"""
        
        groups = firebase_client.get_data("study_groups") or {}
        
        result = []
        for group_id, group in groups.items():
            if topic and topic not in group.get("topics", []):
                continue
            
            members = group.get("members", [])
            result.append({
                "group_id": group_id,
                "name": group.get("name"),
                "description": group.get("description"),
                "topics": group.get("topics", []),
                "member_count": len(members),
                "max_members": group.get("max_members", 20),
                "created_by": group.get("created_by"),
                "created_at": group.get("created_at"),
            })
        
        return result
    
    async def get_study_group(self, group_id: str) -> Optional[Dict]:
        """Get study group details"""
        
        group = firebase_client.get_data(f"study_groups/{group_id}")
        
        if not group:
            return None
        
        # Get member details
        members = []
        for user_id in group.get("members", []):
            user = await self.user_service.get_user_profile(user_id)
            if user:
                members.append({
                    "user_id": user_id,
                    "name": user.get("display_name"),
                    "avatar": user.get("photo_url"),
                })
        
        return {
            **group,
            "group_id": group_id,
            "members": members,
        }
    
    async def create_study_group(self, user_id: str, group_data: Dict) -> Dict:
        """Create a study group"""
        
        group_id = str(uuid4())
        
        group = {
            "group_id": group_id,
            "name": group_data["name"],
            "description": group_data.get("description", ""),
            "topics": group_data.get("topics", []),
            "members": [user_id],
            "max_members": group_data.get("max_members", 20),
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        firebase_client.set_data(f"study_groups/{group_id}", group)
        
        return group
    
    async def join_study_group(self, group_id: str, user_id: str) -> Dict:
        """Join a study group"""
        
        group = firebase_client.get_data(f"study_groups/{group_id}")
        
        if not group:
            raise ValueError("Study group not found")
        
        members = group.get("members", [])
        if user_id in members:
            return {"message": "Already a member"}
        
        if len(members) >= group.get("max_members", 20):
            raise ValueError("Group is full")
        
        members.append(user_id)
        firebase_client.update_data(f"study_groups/{group_id}", {
            "members": members,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return {"message": "Joined group successfully"}
    
    async def leave_study_group(self, group_id: str, user_id: str) -> Dict:
        """Leave a study group"""
        
        group = firebase_client.get_data(f"study_groups/{group_id}")
        
        if not group:
            raise ValueError("Study group not found")
        
        members = group.get("members", [])
        if user_id not in members:
            return {"message": "Not a member"}
        
        members.remove(user_id)
        
        # If no members left, delete the group
        if not members:
            firebase_client.delete_data(f"study_groups/{group_id}")
            return {"message": "Group deleted (no members left)"}
        
        firebase_client.update_data(f"study_groups/{group_id}", {
            "members": members,
            "updated_at": datetime.utcnow().isoformat()
        })
        
        return {"message": "Left group successfully"}
    
    # Leaderboard Methods
    async def get_leaderboard(
        self,
        period: str,
        subject: Optional[str],
        limit: int
    ) -> List[Dict]:
        """Get leaderboard"""
        
        # Determine date range
        now = datetime.utcnow()
        if period == "daily":
            start_date = now - timedelta(days=1)
        elif period == "weekly":
            start_date = now - timedelta(days=7)
        elif period == "monthly":
            start_date = now - timedelta(days=30)
        else:
            start_date = datetime(2000, 1, 1)
        
        # Get all users
        users = firebase_client.get_data("users") or {}
        
        leaderboard = []
        for user_id, user in users.items():
            # Get user's performance in period
            attempts = firebase_client.get_data(f"attempts/{user_id}") or {}
            
            period_attempts = []
            for attempt in attempts.values():
                attempt_date = datetime.fromisoformat(attempt.get("attempted_at", "2000-01-01"))
                if attempt_date >= start_date:
                    if subject:
                        # Check if question is in subject
                        question = firebase_client.get_data(f"questions/{attempt.get('question_id')}")
                        if question and question.get("subject") == subject:
                            period_attempts.append(attempt)
                    else:
                        period_attempts.append(attempt)
            
            if period_attempts:
                correct = sum(1 for a in period_attempts if a.get("is_correct", False))
                accuracy = round(correct / len(period_attempts) * 100, 2)
                
                leaderboard.append({
                    "user_id": user_id,
                    "user_name": user.get("display_name", "Anonymous"),
                    "user_avatar": user.get("photo_url"),
                    "score": accuracy,
                    "questions_attempted": len(period_attempts),
                    "correct_answers": correct,
                })
        
        # Sort by score
        leaderboard.sort(key=lambda x: x["score"], reverse=True)
        
        return leaderboard[:limit]
    
    # Badge Methods
    async def get_all_badges(self) -> List[Dict]:
        """Get all available badges"""
        
        badges = firebase_client.get_data("badges") or {}
        
        return [
            {
                "badge_id": badge_id,
                "name": badge.get("name"),
                "description": badge.get("description"),
                "icon": badge.get("icon"),
                "category": badge.get("category"),
                "requirement": badge.get("requirement"),
            }
            for badge_id, badge in badges.items()
        ]
    
    async def get_user_badges(self, user_id: str) -> List[Dict]:
        """Get badges earned by a user"""
        
        user_badges = firebase_client.get_data(f"user_badges/{user_id}") or {}
        
        result = []
        for badge_id, data in user_badges.items():
            badge = firebase_client.get_data(f"badges/{badge_id}")
            if badge:
                result.append({
                    "badge_id": badge_id,
                    "name": badge.get("name"),
                    "description": badge.get("description"),
                    "icon": badge.get("icon"),
                    "category": badge.get("category"),
                    "earned_at": data.get("earned_at"),
                })
        
        return result