"""
Resume API Tests
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import io

client = TestClient(app)

def test_upload_resume(auth_headers):
    """Test upload resume"""
    # Create a mock PDF file
    file_content = b"%PDF-1.4 test content"
    files = {
        "file": ("test_resume.pdf", io.BytesIO(file_content), "application/pdf")
    }
    
    response = client.post(
        "/api/v1/resume/upload",
        headers=auth_headers,
        files=files
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_resume.pdf"
    assert data["status"] == "uploaded"
    assert "resume_id" in data

def test_upload_invalid_file_type(auth_headers):
    """Test upload invalid file type"""
    files = {
        "file": ("test.exe", io.BytesIO(b"test"), "application/x-msdownload")
    }
    
    response = client.post(
        "/api/v1/resume/upload",
        headers=auth_headers,
        files=files
    )
    
    assert response.status_code == 400

def test_list_resumes(auth_headers):
    """Test list resumes"""
    response = client.get("/api/v1/resume/list", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_resume(auth_headers, test_resume):
    """Test get resume by ID"""
    response = client.get(
        f"/api/v1/resume/{test_resume['resume_id']}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["resume_id"] == test_resume["resume_id"]

def test_delete_resume(auth_headers, test_resume):
    """Test delete resume"""
    response = client.delete(
        f"/api/v1/resume/{test_resume['resume_id']}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Resume deleted successfully"

def test_parse_resume(auth_headers, test_resume):
    """Test parse resume"""
    response = client.post(
        f"/api/v1/resume/{test_resume['resume_id']}/parse",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "Resume parsing started"

def test_get_parsed_resume(auth_headers, test_resume):
    """Test get parsed resume data"""
    response = client.get(
        f"/api/v1/resume/{test_resume['resume_id']}/parsed",
        headers=auth_headers
    )
    
    # May be 404 if not parsed yet
    assert response.status_code in [200, 404]

def test_analyze_resume(auth_headers, test_resume):
    """Test analyze resume"""
    response = client.post(
        f"/api/v1/resume/{test_resume['resume_id']}/analyze",
        headers=auth_headers,
        json={}
    )
    
    assert response.status_code in [200, 400]  # May fail if not parsed

def test_analyze_gaps_pro(premium_auth_headers, test_resume):
    """Test gap analysis (premium)"""
    response = client.post(
        f"/api/v1/resume/{test_resume['resume_id']}/gap-analysis",
        headers=premium_auth_headers,
        json={
            "target_company": "Google",
            "target_role": "ML Engineer"
        }
    )
    
    assert response.status_code in [200, 400]  # May fail if not parsed

def test_analyze_gaps_free(auth_headers, test_resume):
    """Test gap analysis (free - should fail)"""
    response = client.post(
        f"/api/v1/resume/{test_resume['resume_id']}/gap-analysis",
        headers=auth_headers,
        json={
            "target_company": "Google",
            "target_role": "ML Engineer"
        }
    )
    
    assert response.status_code == 403

def test_generate_roadmap_pro(premium_auth_headers, test_resume):
    """Test generate roadmap (premium)"""
    response = client.post(
        f"/api/v1/resume/{test_resume['resume_id']}/roadmap",
        headers=premium_auth_headers,
        json={
            "target_company": "Google",
            "target_role": "ML Engineer",
            "hours_per_week": 10
        }
    )
    
    assert response.status_code in [200, 400]  # May fail if gap analysis not done

def test_get_company_matches(premium_auth_headers):
    """Test get company matches"""
    response = client.get(
        "/api/v1/resume/company-matches",
        headers=premium_auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_assess_skills(auth_headers):
    """Test assess skills"""
    response = client.get(
        "/api/v1/resume/skills/assessment",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_analyze_job_description(premium_auth_headers):
    """Test analyze job description"""
    response = client.post(
        "/api/v1/resume/analyze-job-description",
        headers=premium_auth_headers,
        data={"job_description": "We are looking for a Machine Learning Engineer with 5+ years of experience in Python, TensorFlow, and AWS."}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "skills" in data
    assert "min_experience" in data

def test_optimize_for_job(premium_auth_headers, test_resume):
    """Test optimize resume for job"""
    response = client.post(
        f"/api/v1/resume/{test_resume['resume_id']}/optimize",
        headers=premium_auth_headers,
        data={"job_description": "Looking for ML Engineer with Python and TensorFlow experience."}
    )
    
    assert response.status_code in [200, 400]  # May fail if resume not parsed

def test_export_analysis(premium_auth_headers, test_resume):
    """Test export analysis"""
    response = client.get(
        f"/api/v1/resume/{test_resume['resume_id']}/export/pdf",
        headers=premium_auth_headers
    )
    
    assert response.status_code in [200, 400]  # May fail if analysis not done