"""
Pytest Configuration and Fixtures
"""

import pytest
import asyncio
from typing import Dict, Any
from datetime import datetime, timedelta
from uuid import uuid4

from app.core.database import firebase_client
from app.core.security import security_manager
from app.models.user import User, UserRole
from app.models.question import Question, DifficultyLevel, SubjectArea, QuestionType

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_db():
    """Provide test database connection"""
    # Setup test database
    firebase_client.initialize()
    yield firebase_client
    # Cleanup after tests
    await cleanup_test_data()

async def cleanup_test_data():
    """Clean up test data"""
    # Delete test users
    test_users = firebase_client.query_firestore("users", "email", ">=", "test_")
    for user in test_users:
        firebase_client.delete_data(f"users/{user['uid']}")
    
    # Delete test questions
    test_questions = firebase_client.query_firestore("questions", "created_by", "==", "test")
    for question in test_questions:
        firebase_client.delete_data(f"questions/{question['question_id']}")

@pytest.fixture
async def test_user() -> Dict[str, Any]:
    """Create a test user"""
    user_id = str(uuid4())
    user_data = {
        "uid": user_id,
        "email": f"test_user_{user_id[:8]}@example.com",
        "display_name": "Test User",
        "role": UserRole.FREE,
        "email_verified": True,
        "created_at": datetime.utcnow().isoformat(),
        "stats": {
            "total_questions": 0,
            "correct_answers": 0,
            "accuracy": 0,
            "current_streak": 0,
            "longest_streak": 0
        },
        "preferences": {
            "theme": "light",
            "notifications": {
                "email": True,
                "push": True,
                "daily_reminder": True,
                "weekly_report": True
            },
            "daily_goal": 20
        }
    }
    
    firebase_client.set_data(f"users/{user_id}", user_data)
    
    # Create auth user
    firebase_client.create_user(
        email=user_data["email"],
        password="Test@123456",
        display_name=user_data["display_name"]
    )
    
    return user_data

@pytest.fixture
async def test_admin_user() -> Dict[str, Any]:
    """Create a test admin user"""
    user_id = str(uuid4())
    user_data = {
        "uid": user_id,
        "email": f"test_admin_{user_id[:8]}@example.com",
        "display_name": "Test Admin",
        "role": UserRole.ADMIN,
        "email_verified": True,
        "created_at": datetime.utcnow().isoformat(),
        "stats": {
            "total_questions": 0,
            "correct_answers": 0,
            "accuracy": 0,
            "current_streak": 0,
            "longest_streak": 0
        },
        "preferences": {
            "theme": "dark",
            "notifications": {
                "email": True,
                "push": True,
                "daily_reminder": True,
                "weekly_report": True
            },
            "daily_goal": 50
        }
    }
    
    firebase_client.set_data(f"users/{user_id}", user_data)
    
    # Create auth user
    firebase_client.create_user(
        email=user_data["email"],
        password="Admin@123456",
        display_name=user_data["display_name"]
    )
    
    return user_data

@pytest.fixture
async def test_premium_user() -> Dict[str, Any]:
    """Create a test premium user"""
    user_id = str(uuid4())
    user_data = {
        "uid": user_id,
        "email": f"test_premium_{user_id[:8]}@example.com",
        "display_name": "Test Premium User",
        "role": UserRole.PREMIUM,
        "email_verified": True,
        "created_at": datetime.utcnow().isoformat(),
        "subscription_id": str(uuid4()),
        "subscription_plan": "premium",
        "subscription_expires": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "stats": {
            "total_questions": 150,
            "correct_answers": 120,
            "accuracy": 80,
            "current_streak": 15,
            "longest_streak": 30
        },
        "preferences": {
            "theme": "system",
            "notifications": {
                "email": True,
                "push": True,
                "daily_reminder": True,
                "weekly_report": True
            },
            "daily_goal": 30
        }
    }
    
    firebase_client.set_data(f"users/{user_id}", user_data)
    return user_data

@pytest.fixture
async def test_question() -> Dict[str, Any]:
    """Create a test question"""
    question_id = str(uuid4())
    question_data = {
        "question_id": question_id,
        "subject": SubjectArea.ML,
        "topic": "Linear Regression",
        "subtopic": "Assumptions",
        "type": QuestionType.MCQ,
        "difficulty": DifficultyLevel.MEDIUM,
        "status": "approved",
        "title": "Test Question: Linear Regression Assumptions",
        "description": "Which of the following is NOT an assumption of linear regression?",
        "options": [
            {"id": "A", "text": "Linearity between features and target", "is_correct": False},
            {"id": "B", "text": "Independence of observations", "is_correct": False},
            {"id": "C", "text": "Normal distribution of features", "is_correct": True},
            {"id": "D", "text": "Homoscedasticity of residuals", "is_correct": False}
        ],
        "correct_answers": ["C"],
        "explanation": "Linear regression assumes normality of errors, not features. Features can have any distribution.",
        "hints": ["Think about what the model assumes about errors vs features"],
        "tags": ["regression", "assumptions", "statistics"],
        "companies": ["Google", "Amazon"],
        "times_used": 0,
        "times_correct": 0,
        "correct_rate": 0,
        "avg_time_seconds": 0,
        "created_by": "test",
        "created_at": datetime.utcnow().isoformat()
    }
    
    firebase_client.set_data(f"questions/{question_id}", question_data)
    return question_data

@pytest.fixture
async def test_code_question() -> Dict[str, Any]:
    """Create a test coding question"""
    question_id = str(uuid4())
    question_data = {
        "question_id": question_id,
        "subject": SubjectArea.DA,
        "topic": "SQL",
        "type": QuestionType.CODE,
        "difficulty": DifficultyLevel.MEDIUM,
        "status": "approved",
        "title": "Test SQL Question: Customer Orders",
        "description": "Write a SQL query to find customers who have placed more than 5 orders.",
        "code_snippet": "-- Tables:\n-- customers: customer_id, name, email\n-- orders: order_id, customer_id, order_date, amount\n\nSELECT \n    c.name,\n    COUNT(o.order_id) as order_count\nFROM customers c\nJOIN orders o ON c.customer_id = o.customer_id\nGROUP BY c.customer_id, c.name\nHAVING COUNT(o.order_id) > 5\nORDER BY order_count DESC;",
        "programming_language": "sql",
        "test_cases": [
            {
                "input": "Sample data",
                "output": "Expected result",
                "hidden": False
            }
        ],
        "explanation": "This query joins customers with orders, groups by customer, filters those with >5 orders, and orders by count.",
        "hints": ["Remember to use GROUP BY with aggregate functions", "HAVING clause filters groups"],
        "created_by": "test",
        "created_at": datetime.utcnow().isoformat()
    }
    
    firebase_client.set_data(f"questions/{question_id}", question_data)
    return question_data

@pytest.fixture
async def test_practice_session(test_user) -> Dict[str, Any]:
    """Create a test practice session"""
    session_id = str(uuid4())
    session_data = {
        "session_id": session_id,
        "user_id": test_user["uid"],
        "type": "quick_quiz",
        "status": "in_progress",
        "title": "Test Quick Quiz",
        "total_questions": 5,
        "time_limit": 300,
        "question_ids": [],
        "questions": {},
        "current_question_index": 0,
        "questions_answered": 0,
        "correct_answers": 0,
        "incorrect_answers": 0,
        "created_at": datetime.utcnow().isoformat(),
        "started_at": datetime.utcnow().isoformat()
    }
    
    firebase_client.set_data(f"practice_sessions/{test_user['uid']}/{session_id}", session_data)
    return session_data

@pytest.fixture
async def test_resume(test_user) -> Dict[str, Any]:
    """Create a test resume record"""
    resume_id = str(uuid4())
    resume_data = {
        "resume_id": resume_id,
        "user_id": test_user["uid"],
        "filename": "test_resume.pdf",
        "file_url": "https://storage.example.com/test_resume.pdf",
        "file_size": 1024,
        "mime_type": "application/pdf",
        "status": "uploaded",
        "uploaded_at": datetime.utcnow().isoformat()
    }
    
    firebase_client.set_data(f"resumes/{test_user['uid']}/{resume_id}", resume_data)
    return resume_data

@pytest.fixture
async def auth_headers(test_user):
    """Create authentication headers for API requests"""
    token = security_manager.create_access_token({
        "sub": test_user["uid"],
        "email": test_user["email"],
        "role": test_user["role"]
    })
    
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def premium_auth_headers(test_premium_user):
    """Create premium authentication headers"""
    token = security_manager.create_access_token({
        "sub": test_premium_user["uid"],
        "email": test_premium_user["email"],
        "role": test_premium_user["role"]
    })
    
    return {"Authorization": f"Bearer {token}"}