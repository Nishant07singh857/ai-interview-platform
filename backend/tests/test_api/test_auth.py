"""
Authentication API Tests
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    """Test user registration"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "Test@123456",
            "display_name": "New User"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["display_name"] == "New User"
    assert "uid" in data

def test_register_duplicate_email(test_user):
    """Test registration with existing email"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user["email"],
            "password": "Test@123456",
            "display_name": "Another User"
        }
    )
    
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data

def test_register_invalid_email():
    """Test registration with invalid email"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "invalid-email",
            "password": "Test@123456",
            "display_name": "Test User"
        }
    )
    
    assert response.status_code == 422

def test_register_weak_password():
    """Test registration with weak password"""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "weak",
            "display_name": "Test User"
        }
    )
    
    assert response.status_code == 422

def test_login_success(test_user):
    """Test successful login"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user["email"],
            "password": "Test@123456"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(test_user):
    """Test login with wrong password"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user["email"],
            "password": "Wrong@123456"
        }
    )
    
    assert response.status_code == 401

def test_login_nonexistent_user():
    """Test login with non-existent user"""
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "Test@123456"
        }
    )
    
    assert response.status_code == 401

def test_get_current_user(auth_headers):
    """Test get current user endpoint"""
    response = client.get("/api/v1/auth/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "uid" in data

def test_get_current_user_no_token():
    """Test get current user without token"""
    response = client.get("/api/v1/auth/me")
    
    assert response.status_code == 401

def test_refresh_token(test_user):
    """Test token refresh"""
    # First login to get tokens
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user["email"],
            "password": "Test@123456"
        }
    )
    tokens = login_response.json()
    
    # Refresh token
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] != tokens["access_token"]

def test_logout(auth_headers):
    """Test logout"""
    response = client.post("/api/v1/auth/logout", headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json()["message"] == "Logged out successfully"

def test_forgot_password():
    """Test forgot password"""
    response = client.post(
        "/api/v1/auth/forgot-password",
        params={"email": "test@example.com"}
    )
    
    assert response.status_code == 200
    assert "message" in response.json()

def test_change_password(auth_headers, test_user):
    """Test change password"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "Test@123456",
            "new_password": "NewTest@123456"
        }
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"

def test_change_password_wrong_current(auth_headers):
    """Test change password with wrong current password"""
    response = client.post(
        "/api/v1/auth/change-password",
        headers=auth_headers,
        json={
            "current_password": "Wrong@123456",
            "new_password": "NewTest@123456"
        }
    )
    
    assert response.status_code == 400