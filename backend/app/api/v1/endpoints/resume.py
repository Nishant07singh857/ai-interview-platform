"""
Resume Endpoints - Complete resume management API
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from typing import Optional, List
import logging

from app.core.deps import get_current_user, get_current_admin_user, get_current_pro_user

from app.models.user import User
from app.schemas.resume import (
    ResumeUploadRequest, ResumeAnalysisRequest, GapAnalysisRequest,
    RoadmapRequest, ResumeResponse, ParsedResumeResponse,
    ResumeAnalysisResponse, GapAnalysisResponse, LearningRoadmapResponse,
    CompanyMatchResponse
)
from app.services.resume_service import ResumeService
from app.core.file_handler import file_handler

router = APIRouter(prefix="/resume", tags=["Resume"])
logger = logging.getLogger(__name__)
resume_service = ResumeService()

# Upload endpoints
@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a resume file"""
    try:
        # Validate file
        await file_handler.validate_file(file, allowed_types=['pdf', 'docx', 'txt'])
        
        # Upload and parse
        result = await resume_service.upload_resume(
            current_user.uid,
            file
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error uploading resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload resume")

@router.get("/list", response_model=List[ResumeResponse])
async def list_resumes(
    current_user: User = Depends(get_current_user)
):
    """List all resumes for current user"""
    try:
        resumes = await resume_service.list_resumes(current_user.uid)
        return resumes
    except Exception as e:
        logger.error(f"Error listing resumes: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list resumes")

@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get resume details"""
    try:
        resume = await resume_service.get_resume(resume_id, current_user.uid)
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        return resume
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get resume")

@router.delete("/{resume_id}")
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a resume"""
    try:
        await resume_service.delete_resume(resume_id, current_user.uid)
        return {"message": "Resume deleted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete resume")

# Parsing endpoints
@router.get("/{resume_id}/parsed", response_model=ParsedResumeResponse)
async def get_parsed_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get parsed resume data"""
    try:
        parsed = await resume_service.get_parsed_resume(resume_id, current_user.uid)
        if not parsed:
            raise HTTPException(status_code=404, detail="Parsed resume not found")
        return parsed
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting parsed resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get parsed resume")

@router.post("/{resume_id}/parse")
async def parse_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Trigger resume parsing"""
    try:
        result = await resume_service.parse_resume(resume_id, current_user.uid)
        return {"message": "Resume parsing started", "status": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error parsing resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to parse resume")

# Analysis endpoints
@router.post("/{resume_id}/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    resume_id: str,
    request: ResumeAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze resume"""
    try:
        analysis = await resume_service.analyze_resume(
            resume_id,
            current_user.uid,
            request.dict()
        )
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze resume")

@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisResponse)
async def get_resume_analysis(
    resume_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get resume analysis"""
    try:
        analysis = await resume_service.get_resume_analysis(resume_id, current_user.uid)
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analysis")

# Gap analysis endpoints
@router.post("/{resume_id}/gap-analysis", response_model=GapAnalysisResponse)
async def analyze_gaps(
    resume_id: str,
    request: GapAnalysisRequest,
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Perform gap analysis for target company (pro feature)"""
    try:
        gap_analysis = await resume_service.analyze_gaps(
            resume_id,
            current_user.uid,
            request.dict()
        )
        return gap_analysis
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error analyzing gaps: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze gaps")

@router.get("/{resume_id}/gap-analysis/{company}")
async def get_gap_analysis(
    resume_id: str,
    company: str,
    current_user: User = Depends(get_current_pro_user)
):
    """Get gap analysis for specific company"""
    try:
        analysis = await resume_service.get_gap_analysis(
            resume_id,
            current_user.uid,
            company
        )
        if not analysis:
            raise HTTPException(status_code=404, detail="Gap analysis not found")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting gap analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get gap analysis")

# Roadmap endpoints
@router.post("/{resume_id}/roadmap", response_model=LearningRoadmapResponse)
async def generate_roadmap(
    resume_id: str,
    request: RoadmapRequest,
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Generate personalized learning roadmap (pro feature)"""
    try:
        roadmap = await resume_service.generate_roadmap(
            resume_id,
            current_user.uid,
            request.dict()
        )
        return roadmap
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating roadmap: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate roadmap")

@router.get("/roadmap/current", response_model=LearningRoadmapResponse)
async def get_current_roadmap(
    current_user: User = Depends(get_current_pro_user)
):
    """Get current learning roadmap"""
    try:
        roadmap = await resume_service.get_current_roadmap(current_user.uid)
        if not roadmap:
            raise HTTPException(status_code=404, detail="No active roadmap found")
        return roadmap
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting roadmap: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get roadmap")

@router.put("/roadmap/{roadmap_id}/milestone/{milestone_id}")
async def update_milestone(
    roadmap_id: str,
    milestone_id: str,
    completed: bool = True,
    current_user: User = Depends(get_current_pro_user)
):
    """Update milestone completion status"""
    try:
        result = await resume_service.update_milestone(
            roadmap_id,
            current_user.uid,
            milestone_id,
            completed
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating milestone: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update milestone")

# Company matching endpoints
@router.get("/company-matches", response_model=List[CompanyMatchResponse])
async def get_company_matches(
    resume_id: Optional[str] = None,
    current_user: User = Depends(get_current_pro_user)
):
    """Get company matches based on resume"""
    try:
        matches = await resume_service.get_company_matches(
            current_user.uid,
            resume_id
        )
        return matches
    except Exception as e:
        logger.error(f"Error getting company matches: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get company matches")

# Skill assessment endpoints
@router.get("/skills/assessment")

async def assess_skills(
    current_user: User = Depends(get_current_user)
):
    """Get detailed skill assessment"""
    try:
        assessment = await resume_service.assess_skills(current_user.uid)
        return assessment
    except Exception as e:
        logger.error(f"Error assessing skills: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to assess skills")

# Job description analysis
@router.post("/analyze-job-description")
async def analyze_job_description(
    job_description: str = Form(...),
    current_user: User = Depends(get_current_pro_user)
):
    """Analyze job description and extract requirements"""
    try:
        analysis = await resume_service.analyze_job_description(job_description)
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing job description: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to analyze job description")

# Resume optimization
@router.post("/{resume_id}/optimize")
async def optimize_for_job(
    resume_id: str,
    job_description: str = Form(...),
    current_user: User = Depends(get_current_pro_user)
):
    """Get resume optimization suggestions for specific job"""
    try:
        suggestions = await resume_service.optimize_for_job(
            resume_id,
            current_user.uid,
            job_description
        )
        return suggestions
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error optimizing resume: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to optimize resume")

# Export endpoints
@router.get("/{resume_id}/export/{format}")
async def export_analysis(
    resume_id: str,
    format: str,  # pdf, json, csv
    current_user: User = Depends(get_current_pro_user)
):
    """Export resume analysis in various formats"""
    try:
        export_data = await resume_service.export_analysis(
            resume_id,
            current_user.uid,
            format
        )
        return export_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error exporting analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to export analysis")

# Admin endpoints
@router.get("/admin/stats")
async def get_resume_stats(
    admin: User = Depends(get_current_admin_user)
):
    """Get resume processing statistics (admin only)"""
    try:
        stats = await resume_service.get_resume_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting resume stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get resume stats")