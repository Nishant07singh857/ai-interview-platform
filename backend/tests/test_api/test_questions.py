"""
Questions API Tests
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_questions(auth_headers):
    """Test get questions with filters"""
    response = client.get(
        "/api/v1/questions/?subject=ml&limit=10",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if data:
        assert "question_id" in data[0]
        assert "title" in data[0]

def test_search_questions(auth_headers):
    """Test search questions"""
    response = client.get(
        "/api/v1/questions/search?query=regression",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_question_by_id(auth_headers, test_question):
    """Test get question by ID"""
    response = client.get(
        f"/api/v1/questions/{test_question['question_id']}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["question_id"] == test_question["question_id"]
    assert "title" in data
    # Should not include answers
    assert "correct_answers" not in data

def test_get_question_with_answers(auth_headers, test_question):
    """Test get question with answers (pro feature)"""
    response = client.get(
        f"/api/v1/questions/{test_question['question_id']}/with-answers",
        headers=auth_headers
    )
    
    # Free users should get 403
    assert response.status_code == 403

def test_get_question_with_answers_premium(premium_auth_headers, test_question):
    """Test get question with answers (premium)"""
    response = client.get(
        f"/api/v1/questions/{test_question['question_id']}/with-answers",
        headers=premium_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "correct_answers" in data

def test_attempt_question_mcq(auth_headers, test_question):
    """Test attempt MCQ question"""
    response = client.post(
        f"/api/v1/questions/{test_question['question_id']}/attempt",
        headers=auth_headers,
        json={
            "answer": "C",
            "time_taken_seconds": 45
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "is_correct" in data
    assert "explanation" in data

def test_attempt_question_wrong_answer(auth_headers, test_question):
    """Test attempt with wrong answer"""
    response = client.post(
        f"/api/v1/questions/{test_question['question_id']}/attempt",
        headers=auth_headers,
        json={
            "answer": "A",
            "time_taken_seconds": 30
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["is_correct"] == False

def test_get_hint(auth_headers, test_question):
    """Test get question hint"""
    response = client.get(
        f"/api/v1/questions/{test_question['question_id']}/hint",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "hint" in data

def test_get_topics(auth_headers):
    """Test get all topics"""
    response = client.get("/api/v1/questions/topics/all", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_topics_by_subject(auth_headers):
    """Test get topics by subject"""
    response = client.get(
        "/api/v1/questions/topics/all?subject=ml",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    for topic in data:
        assert topic.get("subject") == "ml"

def test_get_topic_by_id(auth_headers):
    """Test get topic by ID"""
    # First get a topic ID
    topics = client.get("/api/v1/questions/topics/all", headers=auth_headers).json()
    if topics:
        topic_id = topics[0]["topic_id"]
        response = client.get(
            f"/api/v1/questions/topics/{topic_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["topic_id"] == topic_id

def test_get_public_sets(auth_headers):
    """Test get public question sets"""
    response = client.get(
        "/api/v1/questions/sets/public?limit=5",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# Admin endpoints
def test_create_question(admin_auth_headers):
    """Test create question (admin)"""
    response = client.post(
        "/api/v1/questions/",
        headers=admin_auth_headers,
        json={
            "subject": "ml",
            "topic": "Linear Regression",
            "type": "mcq",
            "difficulty": "medium",
            "title": "New Test Question",
            "description": "Test description",
            "options": [
                {"id": "A", "text": "Option A", "is_correct": False},
                {"id": "B", "text": "Option B", "is_correct": True},
                {"id": "C", "text": "Option C", "is_correct": False}
            ],
            "correct_answers": ["B"],
            "explanation": "Test explanation",
            "hints": ["Hint 1", "Hint 2"]
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Test Question"
    assert "question_id" in data

def test_update_question(admin_auth_headers, test_question):
    """Test update question (admin)"""
    response = client.put(
        f"/api/v1/questions/{test_question['question_id']}",
        headers=admin_auth_headers,
        json={
            "title": "Updated Question Title",
            "difficulty": "hard"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Question Title"
    assert data["difficulty"] == "hard"

def test_delete_question(admin_auth_headers, test_question):
    """Test delete question (admin)"""
    response = client.delete(
        f"/api/v1/questions/{test_question['question_id']}",
        headers=admin_auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Question deleted successfully"

def test_bulk_create_questions(admin_auth_headers):
    """Test bulk create questions (admin)"""
    response = client.post(
        "/api/v1/questions/bulk",
        headers=admin_auth_headers,
        json=[
            {
                "subject": "ml",
                "topic": "Linear Regression",
                "type": "mcq",
                "difficulty": "easy",
                "title": "Bulk Question 1",
                "description": "Description 1",
                "options": [
                    {"id": "A", "text": "A", "is_correct": True},
                    {"id": "B", "text": "B", "is_correct": False}
                ],
                "correct_answers": ["A"],
                "explanation": "Explanation 1"
            },
            {
                "subject": "dl",
                "topic": "Neural Networks",
                "type": "theory",
                "difficulty": "medium",
                "title": "Bulk Question 2",
                "description": "Description 2",
                "expected_answer": "Expected answer",
                "explanation": "Explanation 2"
            }
        ]
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "questions" in data
    assert len(data["questions"]) == 2