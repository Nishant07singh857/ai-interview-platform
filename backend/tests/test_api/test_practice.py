"""
Practice API Tests
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_start_quick_quiz(auth_headers):
    """Test start quick quiz"""
    response = client.post(
        "/api/v1/practice/quick-quiz/start",
        headers=auth_headers,
        json={
            "total_questions": 5,
            "time_limit": 5,
            "subjects": ["ml", "dl"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "quick_quiz"
    assert data["total_questions"] == 5
    assert "session_id" in data
    assert "current_question" in data

def test_start_topic_practice(auth_headers):
    """Test start topic practice"""
    response = client.post(
        "/api/v1/practice/topic/start",
        headers=auth_headers,
        json={
            "subject": "ml",
            "topic": "Linear Regression",
            "total_questions": 10
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "topic_wise"
    assert data["subject"] == "ml"
    assert data["topic"] == "Linear Regression"

def test_start_topic_practice_invalid_topic(auth_headers):
    """Test start topic practice with invalid topic"""
    response = client.post(
        "/api/v1/practice/topic/start",
        headers=auth_headers,
        json={
            "subject": "ml",
            "topic": "NonExistentTopic",
            "total_questions": 10
        }
    )
    
    assert response.status_code == 400

def test_start_mock_test_pro(premium_auth_headers):
    """Test start mock test (premium)"""
    response = client.post(
        "/api/v1/practice/mock-test/start",
        headers=premium_auth_headers,
        json={
            "subject": "ml",
            "title": "ML Mock Test",
            "total_questions": 30,
            "time_limit": 30
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "mock_test"
    assert data["total_questions"] == 30

def test_start_mock_test_free(auth_headers):
    """Test start mock test (free - should fail)"""
    response = client.post(
        "/api/v1/practice/mock-test/start",
        headers=auth_headers,
        json={
            "subject": "ml",
            "total_questions": 30,
            "time_limit": 30
        }
    )
    
    assert response.status_code == 403

def test_start_company_practice(premium_auth_headers):
    """Test start company practice (premium)"""
    response = client.post(
        "/api/v1/practice/company/start",
        headers=premium_auth_headers,
        json={
            "company": "Google",
            "role": "ML Engineer",
            "total_questions": 20
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == "company_grid"
    assert data["company"] == "Google"

def test_get_available_topics(auth_headers):
    """Test get available topics"""
    response = client.get(
        "/api/v1/practice/topics/ml",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "topics" in data

def test_get_session(auth_headers, test_practice_session):
    """Test get practice session"""
    response = client.get(
        f"/api/v1/practice/session/{test_practice_session['session_id']}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == test_practice_session["session_id"]

def test_submit_answer(auth_headers, test_practice_session, test_question):
    """Test submit answer"""
    # First add question to session
    session_id = test_practice_session['session_id']
    
    response = client.post(
        f"/api/v1/practice/session/{session_id}/answer",
        headers=auth_headers,
        json={
            "session_id": session_id,
            "question_id": test_question['question_id'],
            "answer": "C",
            "time_taken_seconds": 45
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "is_correct" in data
    assert "next_question" in data or "session_completed" in data

def test_skip_question(auth_headers, test_practice_session):
    """Test skip question"""
    session_id = test_practice_session['session_id']
    
    response = client.post(
        f"/api/v1/practice/session/{session_id}/skip",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "next_question" in data or "session_completed" in data

def test_pause_session(auth_headers, test_practice_session):
    """Test pause session"""
    session_id = test_practice_session['session_id']
    
    response = client.post(
        f"/api/v1/practice/session/{session_id}/pause",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Session paused"

def test_resume_session(auth_headers, test_practice_session):
    """Test resume session"""
    session_id = test_practice_session['session_id']
    
    # First pause
    client.post(f"/api/v1/practice/session/{session_id}/pause", headers=auth_headers)
    
    # Then resume
    response = client.post(
        f"/api/v1/practice/session/{session_id}/resume",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["status"] == "in_progress"

def test_end_session(auth_headers, test_practice_session):
    """Test end session"""
    session_id = test_practice_session['session_id']
    
    response = client.post(
        f"/api/v1/practice/session/{session_id}/end",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["completed"] == True

def test_get_session_results(auth_headers, test_practice_session):
    """Test get session results"""
    session_id = test_practice_session['session_id']
    
    # End session first
    client.post(f"/api/v1/practice/session/{session_id}/end", headers=auth_headers)
    
    # Get results
    response = client.get(
        f"/api/v1/practice/session/{session_id}/results",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "score" in data
    assert "accuracy" in data

def test_submit_feedback(auth_headers, test_practice_session):
    """Test submit session feedback"""
    session_id = test_practice_session['session_id']
    
    response = client.post(
        f"/api/v1/practice/session/{session_id}/feedback",
        headers=auth_headers,
        json={
            "session_id": session_id,
            "rating": 5,
            "feedback": "Great session!"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Feedback submitted successfully"

def test_get_practice_history(auth_headers):
    """Test get practice history"""
    response = client.get(
        "/api/v1/practice/history?days=30",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total_sessions" in data
    assert "recent_sessions" in data

def test_get_practice_stats(auth_headers):
    """Test get practice statistics"""
    response = client.get("/api/v1/practice/stats", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "total_sessions" in data
    assert "overall_accuracy" in data or "total_questions_attempted" in data

def test_get_leaderboard(auth_headers):
    """Test get leaderboard"""
    response = client.get(
        "/api/v1/practice/leaderboard/ml?period=all&limit=10",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "leaderboard" in data