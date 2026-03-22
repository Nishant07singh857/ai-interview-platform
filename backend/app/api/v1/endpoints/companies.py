"""
Companies Endpoints - Complete company-specific preparation API
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from app.core.deps import get_current_user, get_current_admin_user
from app.models.user import User
from app.schemas.company import (
    CompanyResponse, CompanyDetailResponse, CompanyQuestionResponse,
    CompanyStatsResponse, InterviewExperienceResponse, CompanyReadinessResponse
)
from app.services.company_service import CompanyService

router = APIRouter(prefix="/companies", tags=["Companies"])
logger = logging.getLogger(__name__)
company_service = CompanyService()

@router.get("/", response_model=List[CompanyResponse])
async def get_all_companies(
    current_user: User = Depends(get_current_user)
):
    """Get all companies with preparation materials"""
    try:
        companies = await company_service.get_all_companies()
        return companies
    except Exception as e:
        logger.error(f"Error getting companies: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get companies")

@router.get("/{company_id}", response_model=CompanyDetailResponse)
async def get_company(
    company_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed company information"""
    try:
        company = await company_service.get_company(company_id)
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        return company
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get company")

@router.get("/{company_id}/questions", response_model=List[CompanyQuestionResponse])
async def get_company_questions(
    company_id: str,
    role: Optional[str] = None,
    difficulty: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user)
):
    """Get questions commonly asked at a company"""
    try:
        questions = await company_service.get_company_questions(
            company_id, role, difficulty, limit
        )
        return questions
    except Exception as e:
        logger.error(f"Error getting company questions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get questions")

@router.get("/{company_id}/stats", response_model=CompanyStatsResponse)
async def get_company_stats(
    company_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get company statistics"""
    try:
        stats = await company_service.get_company_stats(company_id, current_user.uid)
        return stats
    except Exception as e:
        logger.error(f"Error getting company stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

@router.get("/{company_id}/experiences", response_model=List[InterviewExperienceResponse])
async def get_interview_experiences(
    company_id: str,
    role: Optional[str] = None,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get interview experiences shared by users"""
    try:
        experiences = await company_service.get_interview_experiences(
            company_id, role, limit
        )
        return experiences
    except Exception as e:
        logger.error(f"Error getting experiences: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get experiences")

@router.post("/experiences")
async def share_interview_experience(
    experience_data: dict,
    current_user: User = Depends(get_current_user)
):
    """Share your interview experience"""
    try:
        experience = await company_service.share_experience(
            current_user.uid, experience_data
        )
        return {"message": "Experience shared successfully", "data": experience}
    except Exception as e:
        logger.error(f"Error sharing experience: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to share experience")

@router.get("/{company_id}/readiness", response_model=CompanyReadinessResponse)
async def get_company_readiness(
    company_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get your readiness score for a specific company"""
    try:
        readiness = await company_service.calculate_readiness(
            current_user.uid, company_id
        )
        return readiness
    except Exception as e:
        logger.error(f"Error calculating readiness: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to calculate readiness")

@router.get("/{company_id}/tips")
async def get_preparation_tips(
    company_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get company-specific preparation tips"""
    try:
        tips = await company_service.get_preparation_tips(company_id)
        return {"tips": tips}
    except Exception as e:
        logger.error(f"Error getting tips: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get tips")

@router.post("/{company_id}/track")
async def track_company_interest(
    company_id: str,
    current_user: User = Depends(get_current_user)
):
    """Track that user is interested in this company"""
    try:
        await company_service.track_interest(current_user.uid, company_id)
        return {"message": "Interest tracked successfully"}
    except Exception as e:
        logger.error(f"Error tracking interest: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to track interest")

# Admin endpoints
@router.post("/")
async def create_company(
    company_data: dict,
    admin: User = Depends(get_current_admin_user)
):
    """Create a new company (admin only)"""
    try:
        company = await company_service.create_company(company_data, admin.uid)
        return company
    except Exception as e:
        logger.error(f"Error creating company: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create company")

@router.put("/{company_id}")
async def update_company(
    company_id: str,
    company_data: dict,
    admin: User = Depends(get_current_admin_user)
):
    """Update company information (admin only)"""
    try:
        company = await company_service.update_company(company_id, company_data)
        return company
    except Exception as e:
        logger.error(f"Error updating company: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update company")

@router.delete("/{company_id}")
async def delete_company(
    company_id: str,
    admin: User = Depends(get_current_admin_user)
):
    """Delete a company (admin only)"""
    try:
        await company_service.delete_company(company_id)
        return {"message": "Company deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting company: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete company")