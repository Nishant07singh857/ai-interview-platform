"""
Analytics API Tests
"""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_analytics_summary(auth_headers):
    """Test get analytics summary"""
    response = client.get("/api/v1/analytics/summary", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "overall_accuracy" in data
    assert "total_questions" in data
    assert "current_streak" in data

def test_get_performance_trends(auth_headers):
    """Test get performance trends"""
    response = client.get(
        "/api/v1/analytics/trends?days=30",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "dates" in data
    assert "accuracy" in data
    assert "volume" in data

def test_get_subject_performance(auth_headers):
    """Test get subject performance"""
    response = client.get("/api/v1/analytics/subjects", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "subjects" in data

def test_get_subject_details(auth_headers):
    """Test get subject details"""
    response = client.get(
        "/api/v1/analytics/subjects/ml",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "subject" in data

def test_get_topic_mastery(auth_headers):
    """Test get topic mastery"""
    response = client.get("/api/v1/analytics/topics/mastery", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "mastered_topics" in data
    assert "in_progress_topics" in data
    assert "not_started_topics" in data

def test_get_weak_topics(auth_headers):
    """Test get weak topics"""
    response = client.get(
        "/api/v1/analytics/topics/weak?limit=5",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "weak_topics" in data

def test_get_strong_topics(auth_headers):
    """Test get strong topics"""
    response = client.get(
        "/api/v1/analytics/topics/strong?limit=5",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "strong_topics" in data

def test_get_company_readiness_pro(premium_auth_headers):
    """Test get company readiness (premium)"""
    response = client.get(
        "/api/v1/analytics/companies/readiness",
        headers=premium_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "companies" in data

def test_get_company_readiness_free(auth_headers):
    """Test get company readiness (free - should fail)"""
    response = client.get(
        "/api/v1/analytics/companies/readiness",
        headers=auth_headers
    )
    
    assert response.status_code == 403

def test_get_company_details_pro(premium_auth_headers):
    """Test get company details (premium)"""
    response = client.get(
        "/api/v1/analytics/companies/Google/readiness",
        headers=premium_auth_headers
    )
    
    assert response.status_code == 200

def test_get_difficulty_performance(auth_headers):
    """Test get difficulty performance"""
    response = client.get("/api/v1/analytics/difficulty", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_get_question_type_performance(auth_headers):
    """Test get question type performance"""
    response = client.get("/api/v1/analytics/question-types", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)

def test_get_time_analysis(auth_headers):
    """Test get time analysis"""
    response = client.get("/api/v1/analytics/time", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "average_time" in data

def test_get_weekly_report_pro(premium_auth_headers):
    """Test get weekly report (premium)"""
    response = client.get(
        "/api/v1/analytics/reports/weekly",
        headers=premium_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "week_start" in data
    assert "summary" in data

def test_generate_learning_path_pro(premium_auth_headers):
    """Test generate learning path (premium)"""
    response = client.get(
        "/api/v1/analytics/learning-path?target_role=ML+Engineer",
        headers=premium_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "milestones" in data

def test_compare_with_peers_pro(premium_auth_headers):
    """Test compare with peers (premium)"""
    response = client.get(
        "/api/v1/analytics/compare?peer_group=all",
        headers=premium_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "percentile" in data

def test_get_predictions_pro(premium_auth_headers):
    """Test get predictions (premium)"""
    response = client.get(
        "/api/v1/analytics/predictions",
        headers=premium_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "predicted_accuracy" in data

def test_get_skill_gaps(auth_headers):
    """Test get skill gaps"""
    response = client.get("/api/v1/analytics/skill-gaps", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "skill_gaps" in data

def test_get_recommendations(auth_headers):
    """Test get recommendations"""
    response = client.get(
        "/api/v1/analytics/recommendations?limit=5",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data

def test_get_streak_info(auth_headers):
    """Test get streak info"""
    response = client.get("/api/v1/analytics/streak", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "current_streak" in data

def test_get_activity_heatmap(auth_headers):
    """Test get activity heatmap"""
    response = client.get("/api/v1/analytics/heatmap", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "data" in data

def test_get_milestones(auth_headers):
    """Test get milestones"""
    response = client.get("/api/v1/analytics/milestones", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "milestones" in data

def test_get_dashboard_data(auth_headers):
    """Test get dashboard data"""
    response = client.get("/api/v1/analytics/dashboard", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "trends" in data