"""
Practice Endpoints - Complete practice module API
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from app.core.deps import get_current_user, get_current_admin_user, get_current_pro_user
from app.models.user import User
from app.schemas.practice import (
    QuickQuizRequest, TopicPracticeRequest, MockTestRequest,
    CompanyGridRequest, AnswerSubmission, SessionAction,
    SessionFeedback, PracticeSessionResponse, PracticeResultResponse,
    PracticeHistoryResponse, CompanyGridInfo
)
from app.services.practice_service import PracticeService
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/practice", tags=["Practice"])
logger = logging.getLogger(__name__)
practice_service = PracticeService()

# Quick Quiz endpoints
@router.post("/quick-quiz/start", response_model=PracticeSessionResponse)
async def start_quick_quiz(
    quiz_request: QuickQuizRequest,
    current_user: User = Depends(get_current_user)
):
    """Start a quick quiz session"""
    try:
        session = await practice_service.start_quick_quiz(
            current_user.uid,
            quiz_request.dict()
        )
        return session
    except Exception as e:
        logger.error(f"Error starting quick quiz: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start quick quiz")

# Topic-wise practice endpoints
@router.post("/topic/start", response_model=PracticeSessionResponse)
async def start_topic_practice(
    topic_request: TopicPracticeRequest,
    current_user: User = Depends(get_current_user)
):
    """Start topic-wise practice session with auto-generation if needed"""
    try:
        logger.info(f"📥 Topic practice request: {topic_request.dict()}")
        
        session = await practice_service.start_topic_practice(
            current_user.uid,
            topic_request.dict()
        )
        
        logger.info(f"✅ Topic practice session created: {session.get('session_id')}")
        return session
        
    except ValueError as e:
        logger.error(f"❌ Value error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"❌ Error starting topic practice: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start topic practice")

@router.get("/topics/{subject}")
async def get_available_topics(
    subject: str,
    current_user: User = Depends(get_current_user)
):
    """Get available topics for a subject"""
    try:
        topics = await practice_service.get_available_topics(subject)
        return {"topics": topics}
    except Exception as e:
        logger.error(f"Error getting topics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get topics")

# Gemini test endpoint (optional, for debugging)
@router.get("/gemini/test")
async def test_gemini(current_user: User = Depends(get_current_user)):
    """Test Gemini integration"""
    try:
        questions = await gemini_service.generate_questions_for_topic(
            subject="Machine Learning",
            topic="Linear Regression",
            count=2
        )
        return {
            "success": True,
            "message": f"Generated {len(questions)} questions",
            "questions": questions
        }
    except Exception as e:
        logger.error(f"❌ Gemini test failed: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

# Mock test endpoints
@router.post("/mock-test/start", response_model=PracticeSessionResponse)
async def start_mock_test(
    test_request: MockTestRequest,
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Start a mock test session (pro feature)"""
    try:
        session = await practice_service.start_mock_test(
            current_user.uid,
            test_request.dict()
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting mock test: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start mock test")

# Company grid endpoints
@router.post("/company/start", response_model=PracticeSessionResponse)
async def start_company_practice(
    company_request: CompanyGridRequest,
    current_user: User = Depends(get_current_pro_user)  # Pro feature
):
    """Start company-specific practice session (pro feature)"""
    try:
        session = await practice_service.start_company_practice(
            current_user.uid,
            company_request.dict()
        )
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting company practice: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start company practice")

@router.get("/companies", response_model=List[CompanyGridInfo])
async def get_company_grids(
    current_user: User = Depends(get_current_pro_user)
):
    """Get available company grids (pro feature)"""
    try:
        companies = await practice_service.get_company_grids(current_user.uid)
        return companies
    except Exception as e:
        logger.error(f"Error getting company grids: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get company grids")

# Session management endpoints
@router.get("/session/{session_id}", response_model=PracticeSessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get practice session details"""
    try:
        session = await practice_service.get_session(session_id, current_user.uid)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get session")

@router.post("/session/{session_id}/answer")
async def submit_answer(
    session_id: str,
    answer: AnswerSubmission,
    current_user: User = Depends(get_current_user)
):
    """Submit answer for a question in the session"""
    try:
        if answer.session_id != session_id:
            raise HTTPException(status_code=400, detail="Session ID mismatch")
        
        result = await practice_service.submit_answer(
            session_id,
            current_user.uid,
            answer.dict()
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit answer")

@router.post("/session/{session_id}/skip")
async def skip_question(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Skip current question"""
    try:
        result = await practice_service.skip_question(session_id, current_user.uid)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error skipping question: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to skip question")

@router.post("/session/{session_id}/pause")
async def pause_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Pause practice session"""
    try:
        await practice_service.pause_session(session_id, current_user.uid)
        return {"message": "Session paused"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error pausing session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to pause session")

@router.post("/session/{session_id}/resume")
async def resume_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Resume practice session"""
    try:
        session = await practice_service.resume_session(session_id, current_user.uid)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error resuming session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to resume session")

@router.post("/session/{session_id}/end")
async def end_session(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """End practice session and get results"""
    try:
        results = await practice_service.end_session(session_id, current_user.uid)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error ending session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to end session")

@router.post("/session/{session_id}/feedback")
async def submit_session_feedback(
    session_id: str,
    feedback: SessionFeedback,
    current_user: User = Depends(get_current_user)
):
    """Submit feedback for a session"""
    try:
        if feedback.session_id != session_id:
            raise HTTPException(status_code=400, detail="Session ID mismatch")
        
        await practice_service.submit_feedback(
            session_id,
            current_user.uid,
            feedback.dict()
        )
        return {"message": "Feedback submitted successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit feedback")

@router.get("/session/{session_id}/results", response_model=PracticeResultResponse)
async def get_session_results(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get results for a completed session"""
    try:
        results = await practice_service.get_session_results(session_id, current_user.uid)
        if not results:
            raise HTTPException(status_code=404, detail="Results not found")
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting results: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get results")

# History endpoints
@router.get("/history", response_model=PracticeHistoryResponse)
async def get_practice_history(
    days: int = Query(30, ge=1, le=365),
    type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get user's practice history"""
    try:
        history = await practice_service.get_practice_history(
            current_user.uid,
            days,
            type
        )
        return history
    except Exception as e:
        logger.error(f"Error getting history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get history")

@router.get("/stats")
async def get_practice_stats(
    current_user: User = Depends(get_current_user)
):
    """Get practice statistics"""
    try:
        stats = await practice_service.get_practice_stats(current_user.uid)
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get stats")

# Leaderboard endpoints
@router.get("/leaderboard/{subject}")
async def get_leaderboard(
    subject: str,
    period: str = Query("all", regex="^(daily|weekly|monthly|all)$"),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """Get leaderboard for a subject"""
    try:
        leaderboard = await practice_service.get_leaderboard(
            subject,
            period,
            limit
        )
        return {"leaderboard": leaderboard}
    except Exception as e:
        logger.error(f"Error getting leaderboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get leaderboard")

# Admin endpoints
@router.post("/company-grid/create")
async def create_company_grid(
    company: str,
    question_ids: List[str],
    admin: User = Depends(get_current_admin_user)
):
    """Create a company-specific question grid (admin only)"""
    try:
        grid = await practice_service.create_company_grid(
            company,
            question_ids,
            admin.uid
        )
        return {"message": "Company grid created", "grid": grid}
    except Exception as e:
        logger.error(f"Error creating company grid: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create company grid")