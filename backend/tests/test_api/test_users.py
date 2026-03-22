"""
Users API Tests
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_user_profile(auth_headers):
    """Test get user profile"""
    response = client.get("/api/v1/users/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "display_name" in data
    assert "stats" in data

def test_update_user_profile(auth_headers):
    """Test update user profile"""
    response = client.put(
        "/api/v1/users/me",
        headers=auth_headers,
        json={
            "display_name": "Updated Name",
            "bio": "This is my updated bio",
            "location": "San Francisco, CA"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["display_name"] == "Updated Name"
    assert data["bio"] == "This is my updated bio"

def test_update_user_preferences(auth_headers):
    """Test update user preferences"""
    response = client.put(
        "/api/v1/users/me/preferences",
        headers=auth_headers,
        json={
            "theme": "dark",
            "daily_goal": 30,
            "notifications": {
                "email": False,
                "push": True
            }
        }
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Preferences updated successfully"

def test_update_targets(auth_headers):
    """Test update target companies"""
    response = client.put(
        "/api/v1/users/me/targets",
        headers=auth_headers,
        json={
            "target_companies": ["Google", "Amazon"],
            "target_roles": ["ML Engineer", "Data Scientist"]
        }
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Targets updated successfully"

def test_get_user_stats(auth_headers):
    """Test get user statistics"""
    response = client.get("/api/v1/users/me/stats", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "total_questions" in data
    assert "accuracy" in data
    assert "current_streak" in data

def test_get_user_progress(auth_headers):
    """Test get user progress"""
    response = client.get("/api/v1/users/me/progress?days=30", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_recent_activity(auth_headers):
    """Test get recent activity"""
    response = client.get("/api/v1/users/me/activity", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "activities" in data

def test_get_weak_areas(auth_headers):
    """Test get weak areas"""
    response = client.get("/api/v1/users/me/weak-areas", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "weak_areas" in data or isinstance(data, dict)

def test_get_recommendations(auth_headers):
    """Test get personalized recommendations"""
    response = client.get("/api/v1/users/me/recommendations", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data

def test_get_achievements(auth_headers):
    """Test get user achievements"""
    response = client.get("/api/v1/users/me/achievements", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

# Admin endpoints
def test_get_all_users(admin_auth_headers):
    """Test get all users (admin)"""
    response = client.get("/api/v1/users/", headers=admin_auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_user_by_id(admin_auth_headers, test_user):
    """Test get user by ID (admin)"""
    response = client.get(
        f"/api/v1/users/{test_user['uid']}",
        headers=admin_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == test_user["uid"]

def test_update_user_role(admin_auth_headers, test_user):
    """Test update user role (admin)"""
    response = client.put(
        f"/api/v1/users/{test_user['uid']}/role",
        headers=admin_auth_headers,
        params={"role": "pro"}
    )
    
    assert response.status_code == 200
    assert "message" in response.json()

def test_suspend_user(admin_auth_headers, test_user):
    """Test suspend user (admin)"""
    response = client.post(
        f"/api/v1/users/{test_user['uid']}/suspend",
        headers=admin_auth_headers,
        params={"reason": "Violation of terms"}
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "User suspended successfully"

def test_activate_user(admin_auth_headers, test_user):
    """Test activate user (admin)"""
    response = client.post(
        f"/api/v1/users/{test_user['uid']}/activate",
        headers=admin_auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "User activated successfully"

def test_search_users(admin_auth_headers):
    """Test search users (admin)"""
    response = client.get(
        "/api/v1/users/search/test",
        headers=admin_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "users" in data